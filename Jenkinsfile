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
                
                withCredentials([file(credentialsId: 'config-json-file', variable: 'CONFIG_PATH')]) {
                    // Agregamos "|| true" para que el error de Gmail no ponga el pipeline en rojo
                    sh '''
                      docker run --rm \
                        -e CONFIG_FILE=/app/config.json \
                        -v $CONFIG_PATH:/app/config.json:ro \
                        -v $WORKSPACE/app/data:/app/data:ro \
                        -v $WORKSPACE/output:/app/output \
                        $IMAGE || true
                    '''
                }
            }
        }
    }

    post {
        always {
            // Esto asegura que el Excel aparezca en la interfaz pase lo que pase
            archiveArtifacts artifacts: 'output/ComisionesCalculadas.xlsx', 
                             fingerprint: true, 
                             allowEmptyArchive: true 
        }
    }
}