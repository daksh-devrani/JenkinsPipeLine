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
                    if (isUnix()) {
                        runCmd 'rm -rf reports'
                        runCmd 'mkdir -p reports'
                        runCmd 'curl -L https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/html.tpl -o reports/html.tpl'
                        runCmd 'trivy image --format json -o reports/trivy_report.json --severity MEDIUM,HIGH,CRITICAL demo_app_try || true'
                        runCmd 'trivy image --format template --template "@reports/html.tpl" -o reports/trivy_report.html --severity MEDIUM,HIGH,CRITICAL demo_app_try || true'
                    } else {
                        runCmd 'rmdir /S /Q reports || echo No reports dir'
                        runCmd 'mkdir reports'
                        runCmd 'curl -L https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/html.tpl -o reports\\html.tpl'
                        runCmd 'trivy image --format json -o reports\\trivy_report.json --severity MEDIUM,HIGH,CRITICAL demo_app_try || exit /b 0'
                        runCmd 'trivy image --format template --template "@reports\\html.tpl" -o reports\\trivy_report.html --severity MEDIUM,HIGH,CRITICAL demo_app_try || exit /b 0'
                    }
                }
            }
        }

        stage("Create Network") {
            steps {
                script {
                    if (isUnix()) {
                        runCmd 'docker network inspect network1 >/dev/null 2>&1 || docker network create network1'
                    } else {
                        runCmd 'docker network inspect network1 >nul 2>&1 || docker network create network1'
                    }
                }
            }
        }

        stage("Run App Container") {
            steps {
                script {
                    if (isUnix()) {
                        runCmd '''
                            docker run -d --rm \
                                --network network1 \
                                --name demo_app_running \
                                -p 8123:80 \
                                demo_app_try:latest
                        '''
                        runCmd 'sleep 8'
                    } else {
                        runCmd '''
                            docker run -d --rm ^
                                --network network1 ^
                                --name demo_app_running ^
                                -p 8123:80 ^
                                demo_app_try:latest
                        '''
                        runCmd 'ping -n 9 127.0.0.1 >nul'
                    }
                }
            }
        }

        stage("OWASP ZAP Scan") {
            steps {
                script {
                    if (isUnix()) {
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
                    } else {
                        runCmd '''
                            docker run --rm ^
                            --network network1 ^
                            -v %cd%\\reports:/zap/wrk/ ^
                            ghcr.io/zaproxy/zaproxy:stable zap-baseline.py ^
                                -t http://demo_app_running:80 ^
                                -r zap_report.html ^
                                -J zap_report.json ^
                                -l FAIL || exit /b 0
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                if (isUnix()) {
                    runCmd 'docker stop demo_app_running || true'
                    runCmd 'docker network rm network1 || true'
                } else {
                    runCmd 'docker stop demo_app_running || exit /b 0'
                    runCmd 'docker network rm network1 || exit /b 0'
                }
            }

            // publishHTML can stay the same
             publishHTML([
		allowMissing: true,               // don't fail build if report missing
                alwaysLinkToLastBuild: true,
                keepAll: true,                    // keep reports for all builds

                 reportDir: 'reports',
                 reportFiles: 'trivy_report.html,zap_report.html',
                 reportName: 'Security Reports'
             ])
        }
    }
}
