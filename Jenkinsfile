pipeline {
    agent { label 'linux docker' } 

    environment {
        IMAGE = "comisiones-app:${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps { 
                checkout scm 
            }
        }

        stage('Build') {
            steps {
                sh 'docker build -t $IMAGE .'
            }
        }

        stage('Test job') {
            steps {
                sh 'mkdir -p $WORKSPACE/output'
                sh '''
                  docker run --rm \
                    -e CONFIG_FILE=/app/config.json \
                    -v $WORKSPACE/app/config.json:/app/config.json:ro \
                    -v $WORKSPACE/app/data:/app/data:ro \
                    -v $WORKSPACE/output:/app/output \
                    $IMAGE
                '''
            }
        }
    }

    post {
        success {
            archiveArtifacts artifacts: 'output/ComisionesCalculadas.xlsx', fingerprint: true
        }
    }
}