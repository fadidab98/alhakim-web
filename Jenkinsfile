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
                    image 'docker:27.3.1'
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
                        // Verify the pushed image
                        sh """
                            docker pull ghcr.io/${env.IMAGE_NAMESPACE}/${env.IMAGE_NAME}:${env.IMAGE_TAG}
                            docker inspect ghcr.io/${env.IMAGE_NAMESPACE}/${env.IMAGE_NAME}:${env.IMAGE_TAG} | grep -E 'Created|Id'
                        """
                    }
                }
            }
        }

        stage('Cleanup') {
            agent {
                docker {
                    image 'docker:27.3.1'
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
                                
                                // Create remote directory
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
                                    echo 'Logging into ghcr.io' && \
                                    docker login ghcr.io -u '${CR_USER}' --password '\${CR_PASS}' || { echo 'Docker login failed'; exit 1; } && \
                                    cat /root/.docker/config.json && \
                                    echo 'Docker login succeeded' && \
                                    echo 'Removing old images' && \
                                    docker image rm ghcr.io/${env.IMAGE_NAMESPACE}/${env.IMAGE_NAME}:${env.IMAGE_TAG} || true && \
                                    docker image rm postgres:13 || true && \
                                    echo 'Checking database volume' && \
                                    docker volume ls | grep postgres_data && \
                                    echo 'Pulling images' && \
                                    docker-compose -f docker-compose.yaml pull || { echo 'Docker compose pull failed'; exit 1; } && \
                                    echo 'Inspecting pulled image' && \
                                    docker inspect ghcr.io/${env.IMAGE_NAMESPACE}/${env.IMAGE_NAME}:${env.IMAGE_TAG} | grep -E 'Created|Id' && \
                                    docker-compose -f docker-compose.yaml down || true && \
                                    docker-compose -f docker-compose.yaml up -d && \
                                    docker-compose exec -T web python manage.py migrate && \
                                    docker-compose exec -T web python manage.py collectstatic --noinput && \
                                    docker ps -a && \
                                    docker inspect alhakim-web-web-1 | grep -E 'Image|Created|Id' && \
                                    echo 'Verifying database data' && \
                                    docker-compose exec -T db psql -U alhakim_user -d alhakim_db -c '\\dt' && \
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