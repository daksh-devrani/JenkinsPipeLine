def runCmd(cmd) {
    if (isUnix()) {
        sh(script: cmd)
    } else {
        bat(script: cmd)
    }
}

pipeline {
    agent any

    environment {
        // On Linux/macOS: keep as 'trivy'
        // On Windows: either ensure 'trivy' is in PATH or replace with full path, e.g. 'C:\\Trivy\\trivy.exe'
        TRIVY_EXE = 'trivy'
    }

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
                    if (isUnix()) {
                        sh '''
                            rm -rf reports
                            mkdir -p reports

                            curl -L https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/html.tpl -o reports/html.tpl

                            echo "Running Trivy JSON scan..."
                            $TRIVY_EXE image --format json -o reports/trivy_report.json --severity MEDIUM,HIGH,CRITICAL demo_app_try || echo "Trivy JSON scan failed (continuing pipeline)"

                            echo "Running Trivy HTML scan..."
                            $TRIVY_EXE image --format template --template "@reports/html.tpl" -o reports/trivy_report.html --severity MEDIUM,HIGH,CRITICAL demo_app_try || echo "Trivy HTML scan failed (continuing pipeline)"
                        '''
                    } else {
                        bat '''
                            IF EXIST reports ( rmdir /s /q reports )
                            mkdir reports

                            curl -L https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/html.tpl -o reports\\html.tpl

                            echo Running Trivy JSON scan...
                            "%TRIVY_EXE%" image --format json -o reports\\trivy_report.json --severity MEDIUM,HIGH,CRITICAL demo_app_try  ||  echo Trivy JSON scan failed ^(continuing pipeline^)

                            echo Running Trivy HTML scan...
                            "%TRIVY_EXE%" image --format template --template "@reports\\html.tpl" -o reports\\trivy_report.html --severity MEDIUM,HIGH,CRITICAL demo_app_try  ||  echo Trivy HTML scan failed ^(continuing pipeline^)
                        '''
                    }
                }
            }
        }

        stage("Create Network") {
            steps {
                script {
                    if (isUnix()) {
                        sh 'docker network inspect network1 >/dev/null 2>&1 || docker network create network1'
                    } else {
                        bat 'docker network inspect network1 >nul 2>&1 || docker network create network1'
                    }
                }
            }
        }

        stage("Run App Container") {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            docker run -d --rm \
                                --network network1 \
                                --name demo_app_running \
                                -p 8123:80 \
                                demo_app_try:latest
                        '''
                        sh 'sleep 8'
                    } else {
                        bat '''
                            docker run -d --rm --network network1 --name demo_app_running -p 8123:80 demo_app_try:latest
                        '''
                        bat 'timeout /T 8 /NOBREAK'
                    }
                }
            }
        }

        stage("OWASP ZAP Scan") {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            chmod -R 777 reports

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
                        bat '''
                            icacls reports /grant Everyone:(OI)(CI)F /T

                            docker run --rm ^
                                --network network1 ^
                                -v "%cd%\\reports:/zap/wrk/" ^
                                ghcr.io/zaproxy/zaproxy:stable zap-baseline.py ^
                                    -t http://demo_app_running:80 ^
                                    -r zap_report.html ^
                                    -J zap_report.json ^
                                    -l FAIL || echo ZAP scan failed ^(continuing pipeline^)
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
                    sh 'docker stop demo_app_running || true'
                    sh 'docker network rm network1 || true'
                } else {
                    bat 'docker stop demo_app_running || echo Docker stop failed ^(continuing pipeline^)'
                    bat 'docker network rm network1 || echo Docker network remove failed ^(continuing pipeline^)'
                }
            }

            // If you install the "HTML Publisher" plugin, you can enable this:
            // publishHTML([
            //     reportDir: 'reports',
            //     reportFiles: 'trivy_report.html,zap_report.html',
            //     reportName: 'Security Reports'
            // ])
        }
    }
}
