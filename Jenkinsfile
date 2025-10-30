pipeline {
    agent any

    stages {
        stage("Build Docker Image") {
            steps {
                sh 'docker build -t demo_app_try:latest .'
            }
        }

        stage("Cleanup Docker") {
            steps {
                sh 'docker image prune -f'
            }
        }

        stage("Trivy Scan") {
            steps {
                sh 'trivy image --exit-code 1 --severity HIGH,CRITICAL demo_app'
            }
        }


    }
}
