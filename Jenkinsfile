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
        SECRET_KEY = credentials('SECRET_KEY')
        DATABASE_NAME = credentials('DATABASE_NAME')
        DATABASE_USER = credentials('DATABASE_USER')
        DATABASE_PASSWORD = credentials('DATABASE_PASSWORD')
        EMAIL_HOST_USER = credentials('EMAIL_HOST_USER')
        EMAIL_HOST_PASSWORD = credentials('EMAIL_HOST_PASSWORD')
        CLOUDINARY_CLOUD = credentials('CLOUDINARY_CLOUD')
        CLOUDINARY_KEY = credentials('CLOUDINARY_KEY')
        CLOUDINARY_SECRET = credentials('CLOUDINARY_SECRET')
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
                script {
                    // Validate environment variables
                    def missingVars = []
                    ['SECRET_KEY', 'DATABASE_NAME', 'DATABASE_USER', 'DATABASE_PASSWORD', 'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD', 'CLOUDINARY_CLOUD', 'CLOUDINARY_KEY', 'CLOUDINARY_SECRET'].each { var ->
                        if (!env[var] || env[var].trim() == '') {
                            missingVars << var
                        }
                    }
                    if (missingVars) {
                        error "Missing or empty environment variables: ${missingVars.join(', ')}. Check Jenkins credentials."
                    }
                }
                sh(script: """
                    /bin/bash -c '
                    cat << EOF > .env
                    SECRET_KEY=\${SECRET_KEY}
                    DATABASE_NAME=\${DATABASE_NAME}
                    DATABASE_USER=\${DATABASE_USER}
                    DATABASE_PASSWORD=\${DATABASE_PASSWORD}
                    EMAIL_HOST_USER=\${EMAIL_HOST_USER}
                    EMAIL_HOST_PASSWORD=\${EMAIL_HOST_PASSWORD}
                    CLOUDINARY_CLOUD=\${CLOUDINARY_CLOUD}
                    CLOUDINARY_KEY=\${CLOUDINARY_KEY}
                    CLOUDINARY_SECRET=\${CLOUDINARY_SECRET}
                    EOF
                    chmod 600 .env
                    ls -la .env
                    '
                """)
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