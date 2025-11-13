pipeline {
    agent any

    environment {
    PATH = "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:/Applications/Docker.app/Contents/Resources/bin"
    }

    
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
                sh 'trivy image --exit-code 1 --severity HIGH,CRITICAL demo_app_try'
            }
        }

        stage("Create Network") {
            steps {
                sh 'docker network inspect network1 >/dev/null 2>&1 || docker network create network1'
            }
        }

        stage("Run App Container") {
            steps {
                sh '''
                    docker run -d --rm \
                        --network network1 \
                        --name demo_app_running \
                        -p 8080:8080 \
                        demo_app_try:latest
                '''
                sh 'sleep 8'
            }
        }

        stage("OWASP ZAP Scan") {
            steps {
                sh """
                docker run --rm \
                    --network network1 \
                    -v \$(pwd):/zap/wrk/ \
                    ghcr.io/zaproxy/zaproxy:stable zap-baseline.py \
                        -t http://demo_app_running:8080 \
                        -r zap_report.html
                """
            }
        }

    }
    post {
        always {
            sh 'docker stop demo_app_running || true'
            sh 'docker network rm network1 || true'
        }
    }
}
