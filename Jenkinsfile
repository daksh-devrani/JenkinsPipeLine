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
                    // Ensure reports directory exists
                    runCmd 'rm -rf reports'
                    runCmd 'mkdir reports'

                    // Download HTML template
                    runCmd 'curl -L https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/html.tpl -o reports/html.tpl'

                    // JSON report (machine-readable)
                    runCmd 'trivy image --format json -o reports/trivy_report.json --severity MEDIUM,HIGH,CRITICAL demo_app_try || true'

                    // HTML report (human-readable)
                    runCmd 'trivy image --format template --template "@reports/html.tpl" -o reports/trivy_report.html --severity MEDIUM,HIGH,CRITICAL demo_app_try || true'
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
                            -p 8080:80 \
                            demo_app_try:latest
                    '''
                    runCmd 'sleep 8'
                }
            }
        }

        stage("OWASP ZAP Scan") {
            steps {
                script {
                    // Ensure reports directory is writable by ZAP user (UID 1000)
                    runCmd 'chmod -R 777 reports'

                    runCmd '''
                        docker run --rm \
                        --network network1 \
                        -v $(pwd)/reports:/zap/wrk/ \
                        ghcr.io/zaproxy/zaproxy:stable zap-baseline.py \
                            -t http://demo_app_running:80 \
                            -r zap_report.html \
                            -J zap_report.json \
                            -l FAIL || true
                    '''
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

            // install "publishHTML"
            publishHTML([
                reportDir: 'reports',
                reportFiles: 'trivy_repor   t.html,zap_report.html',
                reportName: 'Security Reports'
            ])
        }
    }
}
