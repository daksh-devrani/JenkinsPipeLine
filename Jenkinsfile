def runCmd(cmd) {
    if (isUnix()) {
        sh(script: cmd)
    } else {
        bat(script: cmd)
    }
}

pipeline {
    agent any

    stages {
        stage("Build Docker Image") {
            steps {
                script {
                    runCmd 'docker build -t demo_app_try:latest .'
                }
            }
        }

        stage("Cleanup Docker") {
            steps {
                script {
                    runCmd 'docker image prune -f'
                }
            }
        }

        stage("Trivy Scan") {
            steps {
                script {
                    runCmd 'trivy image --exit-code 1 --format json -o reports/trivy_repost.json --severity MEDIUM,HIGH,CRITICAL demo_app_try'
                }
            }
        }

        stage("Create Network") {
            steps {
                script {
                    runCmd 'docker network inspect network1 >/dev/null 2>&1 || docker network create network1'
                }
            }
        }

        stage("Run App Container") {
            steps {
                script {
                    runCmd '''
                        docker run -d --rm \
                            --network network1 \
                            --name demo_app_running \
                            -p 8080:8080 \
                            demo_app_try:latest
                    '''
                    runCmd 'sleep 8'
                }
            }
        }

        stage("OWASP ZAP Scan") {
            steps {
                script {
                    runCmd """
                        docker run --rm \
                        --network network1 \
                        -v \$(pwd):/zap/wrk/ \
                        ghcr.io/zaproxy/zaproxy:stable zap-baseline.py \
                            -t http://demo_app_running:80 \
                            -r reports/zap_report.html \
                            -J reports/zap_report.json || true \
                            --exit-code-min-level HIGH
                    """
                }
            }
        }
    }

    post {
        always {
            script {
                runCmd 'docker stop demo_app_running || true'
                runCmd 'docker network rm network1 || true'
            }
        }
    }
}
