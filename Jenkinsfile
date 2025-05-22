pipeline {
    agent none
    // Define parameters for GitHub Secrets
    parameters {
        string(name: 'SECRET_KEY', defaultValue: '', description: 'Django secret key')
        string(name: 'DATABASE_NAME', defaultValue: '', description: 'Database name')
        string(name: 'DATABASE_USER', defaultValue: '', description: 'Database user')
        string(name: 'DATABASE_PASSWORD', defaultValue: '', description: 'Database password')
        string(name: 'EMAIL_HOST_USER', defaultValue: '', description: 'Email host user')
        string(name: 'EMAIL_HOST_PASSWORD', defaultValue: '', description: 'Email host password')
        string(name: 'CLOUDINARY_CLOUD', defaultValue: '', description: 'Cloudinary cloud name')
        string(name: 'CLOUDINARY_KEY', defaultValue: '', description: 'Cloudinary API key')
        string(name: 'CLOUDINARY_SECRET', defaultValue: '', description: 'Cloudinary API secret')
    }
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

        stage('Create .env File') {
            agent any
            steps {
                sh """
                    cat << EOF > .env
                    SECRET_KEY=\${params.SECRET_KEY}
                    DATABASE_NAME=\${params.DATABASE_NAME}
                    DATABASE_USER=\${params.DATABASE_USER}
                    DATABASE_PASSWORD=\${params.DATABASE_PASSWORD}
                    EMAIL_HOST_USER=\${params.EMAIL_HOST_USER}
                    EMAIL_HOST_PASSWORD=\${params.EMAIL_HOST_PASSWORD}
                    CLOUDINARY_CLOUD=\${params.CLOUDINARY_CLOUD}
                    CLOUDINARY_KEY=\${params.CLOUDINARY_KEY}
                    CLOUDINARY_SECRET=\${params.CLOUDINARY_SECRET}
                    EOF
                    chmod 600 .env
                    ls
                """
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
                sh 'rm -f .env || true'
            }
        }

        stage('Deploy to Server') {
            agent any
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    sshagent(credentials: ['jenkins-key']) {
                        withCredentials([usernamePassword(credentialsId: 'CR_PAT', usernameVariable: 'CR_USER', passwordVariable: 'CR_PASS')]) {
                            script {
                                sh 'ls -la docker-compose.yaml .env || { echo "docker-compose.yaml or .env missing"; exit 1; }'
                                sh """
                                    ssh -o StrictHostKeyChecking=no ${env.SERVER_USER}@${env.SERVER_HOST} \
                                    "mkdir -p ${env.REMOTE_DIR} && chmod 755 ${env.REMOTE_DIR}"
                                """
                                sh """
                                    scp -o StrictHostKeyChecking=no docker-compose.yaml .env \
                                    ${env.SERVER_USER}@${env.SERVER_HOST}:${env.REMOTE_DIR}/
                                """
                                sh """
                                    ssh -o StrictHostKeyChecking=no ${env.SERVER_USER}@${env.SERVER_HOST} \
                                    "groups && \
                                    sudo systemctl status nginx && \
                                    ls -l /var/run/docker.sock && \
                                    cd ${env.REMOTE_DIR} && \
                                    ls -l docker-compose.yaml .env && \
                                    chmod 600 ${env.REMOTE_DIR}/.env && \
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
            sh 'rm -f .env || true'
        }
    }
}