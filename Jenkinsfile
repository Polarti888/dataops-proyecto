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
                // Crear carpeta de salida con permisos para el workspace
                sh 'mkdir -p $WORKSPACE/output'
                
                // Ejecución del contenedor usando el secreto de Jenkins
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
        always {
            // Archivar el resultado sin importar si el script falla al enviar el correo
            archiveArtifacts artifacts: 'output/ComisionesCalculadas.xlsx', 
                             fingerprint: true, 
                             allowEmptyArchive: true 
        }
    }
}