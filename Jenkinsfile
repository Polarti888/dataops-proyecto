pipeline {
    // 1. Usamos el nuevo label que configuraste
    agent { label 'linux docker' }

    environment {
        IMAGE = "comisiones-app:${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps { 
                // Baja el código de GitHub al workspace de la VM
                checkout scm 
            }
        }

        stage('Build') {
            steps {
                // Construye la imagen usando el Dockerfile del repo
                sh 'docker build -t $IMAGE .'
            }
        }

        stage('Test job') {
            steps {
                // Crea la carpeta de salida en el workspace del agente
                sh 'mkdir -p $WORKSPACE/output'
                
                // Ejecuta el contenedor mapeando las rutas internas /app/
                sh '''
                  docker run --rm \
                    -v $WORKSPACE/config.json:/app/config.json:ro \
                    -v $WORKSPACE/data:/app/data:ro \
                    -v $WORKSPACE/output:/app/output \
                    $IMAGE
                '''
            }
        }
    }

    post {
        success {
            // Publica el Excel en la interfaz de Jenkins para descarga
            archiveArtifacts artifacts: 'output/ComisionesCalculadas.xlsx', fingerprint: true
        }
    }
}