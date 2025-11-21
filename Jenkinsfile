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
                    runCmd 'docker build -t sreyassharma/signed_images_jenkins:1.0.1 .'
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
                        // runCmd 'curl -L https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/html.tpl -o reports/html.tpl'
                        runCmd 'trivy image --format json -o reports/trivy_report.json --severity MEDIUM,HIGH,CRITICAL sreyassharma/signed_images_jenkins || true'
                        runCmd 'trivy image --format template --template "@tplFormat/html.tpl" -o tplFormat/trivy_report.html --severity MEDIUM,HIGH,CRITICAL sreyassharma/signed_images_jenkins || true'
                    } else {
                        runCmd 'rmdir /S /Q reports || echo No reports dir'
                        runCmd 'mkdir reports'
                        // runCmd 'curl -L https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/html.tpl -o reports\\html.tpl'
                        runCmd 'trivy image --format json -o reports\\trivy_report.json --severity MEDIUM,HIGH,CRITICAL sreyassharma/signed_images_jenkins || exit /b 0'
                        runCmd 'trivy image --format template --template "@tplFormat\\html.tpl" -o tplFormat\\trivy_report.html --severity MEDIUM,HIGH,CRITICAL sreyassharma/signed_images_jenkins || exit /b 0'
                    }
                }
            }
        }

        stage("Push Docker Image") {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'Docker', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        if (isUnix()) {
                            runCmd 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                            runCmd 'docker push sreyassharma/signed_images_jenkins:1.0.1'
                        } else {
                            runCmd 'echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin'
                            runCmd 'docker push sreyassharma/signed_images_jenkins:1.0.1'
                        }
                    }
                }
            }
        }

        stage("Sign Docker Image") {
            steps {
                script {
                    withCredentials([string(credentialsId: 'CosignPrivateKey', variable: 'COSIGN_KEY')]) {
                        if (isUnix()) {
                            runCmd "echo \"$COSIGN_KEY\" > cosign.key"
                            runCmd "cosign sign --key cosign.key docker.io/sreyassharma/signed_images_jenkins:1.0.1"
                            runCmd "rm cosign.key"    // Linux
                        } else {
                            runCmd "echo %COSIGN_KEY% > cosign.key"
                            runCmd "cosign sign --key cosign.key docker.io/sreyassharma/signed_images_jenkins:1.0.1"
                            runCmd "del cosign.key"   // Windows
                        }
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
                                sreyassharma/signed_images_jenkins:1.0.1
                        '''
                        runCmd 'sleep 8'
                    } else {
                        runCmd '''
                            docker run -d --rm ^
                                --network network1 ^
                                --name demo_app_running ^
                                -p 8123:80 ^
                                sreyassharma/signed_images_jenkins:1.0.1
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
