def runCmd(cmd) {
    if (isUnix()) { sh(script: cmd) }
    else { bat(script: cmd) }
}

pipeline {
    agent any

    stages {

        /* -------------------------------------------
         BUILD DOCKER IMAGE
         ------------------------------------------- */
        stage("Build Docker Image") {
            steps {
                script {
                    runCmd 'docker build -t sreyassharma/signed_images_jenkins:1.0.1 .'
                }
            }
        }

        /* -------------------------------------------
         CLEANUP DOCKER
         ------------------------------------------- */
        stage("Cleanup Docker") {
            steps {
                script { runCmd 'docker image prune -f' }
            }
        }

        /* -------------------------------------------
         TRIVY SCAN
         ------------------------------------------- */
        stage("Trivy Scan") {
            steps {
                script {
                    if (isUnix()) {
                        sh 'rm -rf reports'
                        sh 'mkdir -p reports'
                        sh 'trivy image --format json -o reports/trivy_report.json --severity MEDIUM,HIGH,CRITICAL sreyassharma/signed_images_jenkins:1.0.1 || true'
                        sh 'trivy image --format template --template "@tplFormat/html.tpl" -o reports/trivy_report.html --severity MEDIUM,HIGH,CRITICAL sreyassharma/signed_images_jenkins:1.0.1 || true'
                    } else {
                        bat 'rmdir /S /Q reports || echo No reports dir'
                        bat 'mkdir reports'
                        bat 'trivy image --format json -o reports\\trivy_report.json --severity MEDIUM,HIGH,CRITICAL sreyassharma/signed_images_jenkins:1.0.1 || exit /b 0'
                        bat 'trivy image --format template --template "@tplFormat\\html.tpl" -o reports\\trivy_report.html --severity MEDIUM,HIGH,CRITICAL sreyassharma/signed_images_jenkins:1.0.1 || exit /b 0'
                    }
                }
            }
        }

        /* -------------------------------------------
         SNYK SAST & CONTAINER SCAN  (WINDOWS)
         ------------------------------------------- */
        stage('Snyk SAST Scan') {
            steps {
                script {
                    bat "if not exist reports mkdir reports"

                    withCredentials([string(credentialsId: 'SynkToken', variable: 'SNYK_TOKEN')]) {

                        echo "Authenticating Snyk CLI..."
                        bat """ snyk auth %SNYK_TOKEN% """

                        echo "Running Snyk Source Code Scan (SAST)..."
                        bat """ snyk code test --json > reports\\snyk_source_report.json || exit 0 """

                        echo "Running Snyk Container Scan..."
                        bat """ snyk container test sreyassharma/signed_images_jenkins:1.0.1 --json > reports\\snyk_container_report.json || exit 0 """

                        echo "Converting Snyk reports to HTML..."
                        bat """
                            npx snyk-to-html -i reports\\snyk_source_report.json -o reports\\snyk_source_report.html || exit 0
                            npx snyk-to-html -i reports\\snyk_container_report.json -o reports\\snyk_container_report.html || exit 0
                        """
                    }
                }
            }

            post {
                always {
                    archiveArtifacts artifacts: 'reports/snyk_*', fingerprint: true

                    publishHTML([
                        allowMissing: true,
                        reportDir: 'reports',
                        reportFiles: 'snyk_source_report.html',
                        reportName: 'Snyk Source Code (SAST) Report',
                        keepAll: true,
                        alwaysLinkToLastBuild: true
                    ])

                    publishHTML([
                        allowMissing: true,
                        reportDir: 'reports',
                        reportFiles: 'snyk_container_report.html',
                        reportName: 'Snyk Container Vulnerability Report',
                        keepAll: true,
                        alwaysLinkToLastBuild: true
                    ])
                }
            }
        }

        /* -------------------------------------------
         PUSH DOCKER IMAGE
         ------------------------------------------- */
        stage("Push Docker Image") {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'Docker', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        if (isUnix()) {
                            sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                            sh 'docker push sreyassharma/signed_images_jenkins:1.0.1'
                        } else {
                            bat 'echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin'
                            bat 'docker push sreyassharma/signed_images_jenkins:1.0.1'
                        }
                    }
                }
            }
        }

        /* -------------------------------------------
         COSIGN SIGNING
         ------------------------------------------- */
        stage("Sign Docker Image") {
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'CosignPrivateKey', variable: 'COSIGN_KEY'),
                        string(credentialsId: 'CosignPassword', variable: 'COSIGN_PASSWORD')
                    ]) {
                        if (isUnix()) {
                            sh '''
                                echo "$COSIGN_KEY" > cosign.key
                                cosign sign --key cosign.key --pass-env COSIGN_PASSWORD docker.io/sreyassharma/signed_images_jenkins:1.0.1
                                rm cosign.key
                            '''
                        } else {
                            bat '''
                                echo %COSIGN_KEY% > cosign.key
                                cosign sign --key cosign.key --pass-env COSIGN_PASSWORD docker.io/sreyassharma/signed_images_jenkins:1.0.1
                                del cosign.key
                            '''
                        }
                    }
                }
            }
        }

        /* -------------------------------------------
         CREATE NETWORK
         ------------------------------------------- */
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

        /* -------------------------------------------
         RUN APP CONTAINER
         ------------------------------------------- */
        stage("Run App Container") {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            docker run -d --rm \
                                --network network1 \
                                --name demo_app_running \
                                -p 8123:80 \
                                sreyassharma/signed_images_jenkins:1.0.1
                        '''
                        sh 'sleep 8'
                    } else {
                        bat '''
                            docker run -d --rm ^
                                --network network1 ^
                                --name demo_app_running ^
                                -p 8123:80 ^
                                sreyassharma/signed_images_jenkins:1.0.1
                        '''
                        bat 'ping -n 9 127.0.0.1 >nul'
                    }
                }
            }
        }

        /* -------------------------------------------
         OWASP ZAP SCAN
         ------------------------------------------- */
        stage("OWASP ZAP Scan") {
            steps {
                script {
                    if (isUnix()) {
                        sh 'chmod -R 777 reports'
                        sh '''
                            docker run --rm \
                            --network network1 \
                            -v $(pwd)/reports:/zap/wrk/ \
                            ghcr.io/zaproxy/zaproxy:stable zap-full-scan.py \
                                -t http://demo_app_running:80 \
                                -r zap_full_report.html \
                                -J zap_full_report.json \
                                -a || true
                        '''
                    } else {
                        bat '''
                            docker run --rm ^
                            --network network1 ^
                            -v %cd%\\reports:/zap/wrk/ ^
                            ghcr.io/zaproxy/zaproxy:stable zap-full-scan.py ^
                                -t http://demo_app_running:80 ^
                                -r zap_full_report.html ^
                                -J zap_full_report.json ^
                                -a || exit /b 0
                        '''
                    }
                }
            }
        }
    }

    /* -------------------------------------------
       POST ACTIONS
       ------------------------------------------- */
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

            publishHTML([
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'reports',
                reportFiles: 'trivy_report.html,zap_full_report.html',
                reportName: 'Security Reports'
            ])
        }
    }
}
