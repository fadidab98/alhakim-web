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
        SECRET_KEY = credentials('ALHAKIM_SECRET_KEY')
        DATABASE_NAME = credentials('ALHAKIM_DATABASE_NAME')
        DATABASE_USER = credentials('ALHAKIM_DATABASE_USER')
        DATABASE_PASSWORD = credentials('ALHAKIM_DATABASE_PASSWORD')
        EMAIL_HOST_USER = credentials('ALHAKIM_EMAIL_HOST_USER')
        EMAIL_HOST_PASSWORD = credentials('ALHAKIM_EMAIL_HOST_PASSWORD')
        CLOUDINARY_CLOUD = credentials('ALHAKIM_CLOUDINARY_CLOUD')
        CLOUDINARY_KEY = credentials('ALHAKIM_CLOUDINARY_KEY')
        CLOUDINARY_SECRET = credentials('ALHAKIM_CLOUDINARY_SECRET')
    }
    stages {
        stage('Checkout') {
            agent any
            steps {
                echo "Starting Checkout stage"
                timeout(time: 5, unit: 'MINUTES') {
                    git branch: 'master', credentialsId: 'jenkins', url: 'https://github.com/fadidab98/alhakim-web.git'
                }
                echo "Checkout completed"
            }
        }

        stage('Debug Workspace') {
            agent any
            steps {
                echo "Starting Debug Workspace stage"
                sh 'ls -la'
                sh 'which bash || echo "Bash not found"'
                echo "Debug Workspace completed"
            }
        }

        stage('Create .env File') {
            agent any
            steps {
                echo "Starting Create .env File stage"
                script {
                    try {
                        // Validate environment variables
                        echo "Validating environment variables"
                        def missingVars = []
                        if (!env.SECRET_KEY || env.SECRET_KEY.trim() == '') {
                            missingVars << 'SECRET_KEY'
                        }
                        if (!env.DATABASE_NAME || env.DATABASE_NAME.trim() == '') {
                            missingVars << 'DATABASE_NAME'
                        }
                        if (!env.DATABASE_USER || env.DATABASE_USER.trim() == '') {
                            missingVars << 'DATABASE_USER'
                        }
                        if (!env.DATABASE_PASSWORD || env.DATABASE_PASSWORD.trim() == '') {
                            missingVars << 'DATABASE_PASSWORD'
                        }
                        if (!env.EMAIL_HOST_USER || env.EMAIL_HOST_USER.trim() == '') {
                            missingVars << 'EMAIL_HOST_USER'
                        }
                        if (!env.EMAIL_HOST_PASSWORD || env.EMAIL_HOST_PASSWORD.trim() == '') {
                            missingVars << 'EMAIL_HOST_PASSWORD'
                        }
                        if (!env.CLOUDINARY_CLOUD || env.CLOUDINARY_CLOUD.trim() == '') {
                            missingVars << 'CLOUDINARY_CLOUD'
                        }
                        if (!env.CLOUDINARY_KEY || env.CLOUDINARY_KEY.trim() == '') {
                            missingVars << 'CLOUDINARY_KEY'
                        }
                        if (!env.CLOUDINARY_SECRET || env.CLOUDINARY_SECRET.trim() == '') {
                            missingVars << 'CLOUDINARY_SECRET'
                        }
                        if (missingVars) {
                            error "Missing or empty environment variables: ${missingVars.join(', ')}. Check Jenkins credentials."
                        }
                        echo "All environment variables are defined"
                    } catch (Exception e) {
                        error "Validation failed: ${e.message}"
                    }
                }
                script {
                    def status = sh(script: """
                        /bin/bash -c '
                        echo "Creating .env file"
                        rm -f .env
                        set -e
                        touch .env
                        echo "SECRET_KEY=\${SECRET_KEY}" >> .env
                        echo "DATABASE_NAME=\${DATABASE_NAME}" >> .env
                        echo "DATABASE_USER=\${DATABASE_USER}" >> .env
                        echo "DATABASE_PASSWORD=\${DATABASE_PASSWORD}" >> .env
                        echo "EMAIL_HOST_USER=\${EMAIL_HOST_USER}" >> .env
                        echo "EMAIL_HOST_PASSWORD=\${EMAIL_HOST_PASSWORD}" >> .env
                        echo "CLOUDINARY_CLOUD=\${CLOUDINARY_CLOUD}" >> .env
                        echo "CLOUDINARY_KEY=\${CLOUDINARY_KEY}" >> .env
                        echo "CLOUDINARY_SECRET=\${CLOUDINARY_SECRET}" >> .env
                        chmod 600 .env
                        ls -la .env
                        echo ".env file created successfully"
                        '
                    """, returnStatus: true)
                    if (status != 0) {
                        error "Failed to create .env file: shell command exited with status ${status}"
                    }
                }
                echo "Create .env File completed"
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
                echo "Starting Build stage"
                timeout(time: 10, unit: 'MINUTES') {
                    script {
                        echo "Packaging Docker image"
                        sh 'ls -la '
                        def image = docker.build("${env.IMAGE_NAMESPACE}/${env.IMAGE_NAME}:${env.IMAGE_TAG}")
                        docker.withRegistry('https://ghcr.io', 'CR_PAT') {
                            image.push("${env.IMAGE_TAG}")
                            image.push('latest')
                        }
                    }
                }
                echo "Build completed"
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
                echo "Starting Cleanup stage"
                sh "docker rmi ${env.IMAGE_NAME}:${env.IMAGE_TAG} || true"
                sh "docker rmi ghcr.io/${env.IMAGE_NAMESPACE}/${env.IMAGE_NAME}:${env.IMAGE_TAG} || true"
                sh "docker rmi ghcr.io/${env.IMAGE_NAMESPACE}/${env.IMAGE_NAME}:latest || true"
                sh 'rm -f .env || true'
                echo "Cleanup completed"
            }
        }

        stage('Deploy to Server') {
            agent any
            steps {
                echo "Starting Deploy to Server stage"
                timeout(time: 5, unit: 'MINUTES') {
                    sshagent(credentials: ['jenkins-key']) {
                        withCredentials([usernamePassword(credentialsId: 'CR_PAT', usernameVariable: 'CR_USER', passwordVariable: 'CR_PASS')]) {
                            script {
                                sh 'ls -la docker-compose.yaml || { echo "docker-compose.yaml missing"; exit 1; }'
                                sh """
                                    ssh -o StrictHostKeyChecking=no ${env.SERVER_USER}@${env.SERVER_HOST} \
                                    "mkdir -p ${env.REMOTE_DIR} && chmod 755 ${env.REMOTE_DIR}"
                                """
                                sh """
                                    scp -o StrictHostKeyChecking=no docker-compose.yaml \
                                    ${env.SERVER_USER}@${env.SERVER_HOST}:${env.REMOTE_DIR}/
                                """
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
                echo "Deploy to Server completed"
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