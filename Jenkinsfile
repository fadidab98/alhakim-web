pipeline {
    agent none
    environment {
        IMAGE_NAMESPACE = "fadidab98"
        IMAGE_NAME = "alhakim-web"
        GITHUB_CRED = credentials('jenkins')
        CR_PAT = credentials('CR_PAT')
        IMAGE_TAG = "latest"
        SERVER_USER = "jenkins_user"
        SERVER_HOST = "217.154.21.206"
        REMOTE_DIR = "/projects/alhakim-web"
    }
    stages {
        stage('Checkout') {
            agent any
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    git branch: 'master', credentialsId: 'jenkins', url: 'https://github.com/fadidab98/alhakim-web.git'
                }
            }
        }

        stage('Debug Workspace') {
            agent any
            steps {
                sh 'ls -la'
            }
        }

        stage('Build, Run, Tag, and Push Image') {
            agent {
                docker {
                    image 'docker:28.0.4'
                    args '-v /var/run/docker.sock:/var/run/docker.sock --group-add 988 --env HOME=/tmp'
                }
            }
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    script {
                        echo "####### Packaging stage #######"
                        def image = docker.build("${env.IMAGE_NAMESPACE}/${env.IMAGE_NAME}:${env.IMAGE_TAG}")
                        docker.withRegistry('https://ghcr.io', 'CR_PAT') {
                            image.push("${env.IMAGE_TAG}")
                            image.push('latest')
                        }
                    }
                }
            }
        }

        stage('Cleanup') {
            agent {
                docker {
                    image 'docker:28.0.4'
                    args '-v /var/run/docker.sock:/var/run/docker.sock --group-add 988 --env HOME=/tmp'
                }
            }
            steps {
                sh "docker rmi ${env.IMAGE_NAME}:${env.IMAGE_TAG} || true"
                sh "docker rmi ghcr.io/${env.IMAGE_NAMESPACE}/${env.IMAGE_NAME}:${env.IMAGE_TAG} || true"
                sh "docker rmi ghcr.io/${env.IMAGE_NAMESPACE}/${env.IMAGE_NAME}:latest || true"
            }
        }

        stage('Deploy to Server') {
            agent any
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    sshagent(credentials: ['jenkins-key']) {
                        withCredentials([usernamePassword(credentialsId: 'CR_PAT', usernameVariable: 'CR_USER', passwordVariable: 'CR_PASS')]) {
                            script {
                                // Verify local files
                                sh 'ls -la docker-compose.yaml || { echo "docker-compose.yaml missing"; exit 1; }'
                                
                                // Create remote directory first
                                sh """
                                    ssh -o StrictHostKeyChecking=no ${env.SERVER_USER}@${env.SERVER_HOST} \
                                    "mkdir -p ${env.REMOTE_DIR} && chmod 755 ${env.REMOTE_DIR}"
                                """
                                
                                // Copy docker-compose.yaml
                                sh """
                                    scp -o StrictHostKeyChecking=no docker-compose.yaml \
                                    ${env.SERVER_USER}@${env.SERVER_HOST}:${env.REMOTE_DIR}/
                                """
                                
                                // Deploy and run docker-compose
                                sh """
                                    ssh -o StrictHostKeyChecking=no ${env.SERVER_USER}@${env.SERVER_HOST} \
                                    "groups && \
                                    sudo systemctl status nginx && \
                                    ls -l /var/run/docker.sock && \
                                    cd ${env.REMOTE_DIR} && \
                                    ls -l docker-compose.yaml && \
                                    docker login ghcr.io -u '${CR_USER}' --password '\${CR_PASS}' && \
                                    docker image rm ghcr.io/${env.IMAGE_NAMESPACE}/${env.IMAGE_NAME}:${env.IMAGE_TAG} || true && \
                                    docker-compose -f docker-compose.yaml pull && \
                                    docker-compose -f docker-compose.yaml down || true && \
                                    docker-compose -f docker-compose.yaml up -d && \
                                    docker-compose exec -T web python manage.py migrate && \
                                    echo 'Deployment succeeded'"
                                """
                            }
                        }
                    }
                }
            }
        }
    }
    post {
        always {
            echo "Pipeline completed" 
        }
    }
}