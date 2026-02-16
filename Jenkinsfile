Aquí tienes el Jenkinsfile completo y corregido para que el Build #4 sea exitoso, integrando el label de tu nodo y la solución al error de rutas que vimos en el log anterior:

Groovy
pipeline {
    // 1. Usamos el label exacto que configuraste en tu nodo
    agent { label 'linux docker' } 

    environment {
        // Nombre de la imagen para este build
        IMAGE = "comisiones-app:${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps { 
                // Descarga el código desde GitHub al workspace de la VM
                checkout scm 
            }
        }

        stage('Build') {
            steps {
                // Construye la imagen usando el Dockerfile que está en la raíz
                sh 'docker build -t $IMAGE .'
            }
        }

        stage('Test job') {
            steps {
                // Crea la carpeta de salida en el workspace para recibir el Excel
                sh 'mkdir -p $WORKSPACE/output'
                
                // Ejecuta el contenedor con las rutas corregidas y la variable de entorno
                // Se asume que config.json y data/ están dentro de la carpeta 'app/'
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
            // Publica el archivo Excel en la interfaz de Jenkins para su descarga
            archiveArtifacts artifacts: 'output/ComisionesCalculadas.xlsx', fingerprint: true
        }
    }
}