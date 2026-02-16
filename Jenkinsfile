pipeline {
    agent { label 'linux docker' } 

    environment {
        IMAGE = "comisiones-app:${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Build') {
            steps { sh 'docker build -t $IMAGE .' }
        }

        stage('Test job') {
            steps {
                sh 'mkdir -p $WORKSPACE/output'
                // Usamos el secreto de Jenkins aquí
                withCredentials([file(credentialsId: 'config-json-file', variable: 'CONFIG_PATH')]) {
                    sh '''
                      docker run --rm \
                        -e CONFIG_FILE=/app/config.json \
                        -v $CONFIG_PATH:/app/config.json:ro \
                        -v $WORKSPACE/app/data:/app/data:ro \
                        -v $WORKSPACE/output:/app/output \
                        $IMAGE
                    '''
                }
            }
        }
    }

    post {
        success {
            archiveArtifacts artifacts: 'output/ComisionesCalculadas.xlsx', fingerprint: true
        }
    }
}