/*
   OPTIMIZED JENKINSFILE — DevSecOps Pipeline
   ✔ Cross-platform (Windows/Linux)
   ✔ Trivy Scan
   ✔ Push Image
   ✔ Cosign Signing
   ✔ OWASP ZAP Scan
   ✔ HTML Reporting
*/

def runCmd(cmd) {
    if (isUnix()) {
        sh "${cmd}"
    } else {
        bat "${cmd}"
    }
}

pipeline {
    agent any

    environment {
        IMAGE = "sreyassharma/signed_images_jenkins:1.0.1"
        REPORT_DIR = "reports"
    }

    stages {

        /* ----------------------------------------------------------------------
                                BUILD DOCKER IMAGE
        ---------------------------------------------------------------------- */
        stage("Build Docker Image") {
            steps {
                script {
                    runCmd("docker build -t ${IMAGE} .")
                }
            }
        }

        /* ----------------------------------------------------------------------
                                CLEANUP DOCKER
        ---------------------------------------------------------------------- */
        stage("Cleanup Docker") {
            steps {
                script {
                    runCmd("docker image prune -f")
                }
            }
        }

        /* ----------------------------------------------------------------------
                                TRIVY SCAN
        ---------------------------------------------------------------------- */
        stage("Trivy Scan") {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            rm -rf reports
                            mkdir -p reports
                            trivy image --format json -o reports/trivy_report.json \
                                --severity MEDIUM,HIGH,CRITICAL $IMAGE || true

                            trivy image --format template --template "@/tplFormat/html.tpl" \
                                -o reports/trivy_report.html \
                                --severity MEDIUM,HIGH,CRITICAL $IMAGE || true
                        '''
                    } else {
                        bat '''
                            if exist reports ( rmdir /S /Q reports ) else ( echo No reports dir )
                            mkdir reports

                            trivy image --format json -o reports\\trivy_report.json --severity MEDIUM,HIGH,CRITICAL %IMAGE% || exit /b 0
                            trivy image --format template --template "@tplFormat\\html.tpl" -o reports\\trivy_report.html --severity MEDIUM,HIGH,CRITICAL %IMAGE% || exit /b 0
                        '''
                    }
                }
            }
        }

        /* ----------------------------------------------------------------------
                                PUSH DOCKER IMAGE
        ---------------------------------------------------------------------- */
        stage("Push Docker Image") {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'Docker', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        runCmd('echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin'.replace("%","$"))
                        runCmd("docker push ${IMAGE}")
                    }
                }
            }
        }

        /* ----------------------------------------------------------------------
                                SIGN DOCKER IMAGE (COSIGN)
        ---------------------------------------------------------------------- */
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
                                cosign sign --key cosign.key --pass-env COSIGN_PASSWORD docker.io/$IMAGE
                                rm cosign.key
                            '''
                        } else {
                            bat '''
                                echo %COSIGN_KEY% > cosign.key
                                cosign sign --key cosign.key --pass-env COSIGN_PASSWORD docker.io/%IMAGE%
                                del cosign.key
                            '''
                        }
                    }
                }
            }
        }

        /* ----------------------------------------------------------------------
                                CREATE DOCKER NETWORK
        ---------------------------------------------------------------------- */
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

        /* ----------------------------------------------------------------------
                                RUN APP CONTAINER
        ---------------------------------------------------------------------- */
        stage("Run App Container") {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            docker run -d --rm --network network1 --name demo_app_running -p 8123:80 $IMAGE
                            sleep 8
                        '''
                    } else {
                        bat '''
                            docker run -d --rm --network network1 --name demo_app_running -p 8123:80 %IMAGE%
                        '''
                        bat 'ping -n 9 127.0.0.1 >nul'
                    }
                }
            }
        }

        /* ----------------------------------------------------------------------
                                OWASP ZAP SCAN
        ---------------------------------------------------------------------- */
        stage("OWASP ZAP Scan") {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            chmod -R 777 reports

                            docker run --rm --network network1 \
                                -v $(pwd)/reports:/zap/wrk/ \
                                ghcr.io/zaproxy/zaproxy:stable zap.sh -cmd -addonupdate

                            docker run --rm --network network1 \
                                -v $(pwd)/reports:/zap/wrk/ \
                                ghcr.io/zaproxy/zaproxy:stable zap-full-scan.py \
                                    -t http://demo_app_running:80 \
                                    -r zap_full_report.html \
                                    -J zap_full_report.json -a || true
                        '''
                    } else {
                        bat '''
                            docker run --rm --network network1 -v %cd%\\reports:/zap/wrk/ ghcr.io/zaproxy/zaproxy:stable zap.sh -cmd -addonupdate

                            docker run --rm --network network1 -v %cd%\\reports:/zap/wrk/ ghcr.io/zaproxy/zaproxy:stable zap-full-scan.py ^
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

    /* ----------------------------------------------------------------------
                             POST CLEANUP + REPORT PUBLISH  
    ---------------------------------------------------------------------- */
    post {
        always {
            script {
                // Stop container safely
                if (isUnix()) {
                    sh 'docker stop demo_app_running >/dev/null 2>&1 || true'
                    sh 'docker network rm network1 >/dev/null 2>&1 || true'
                } else {
                    bat 'docker stop demo_app_running 2>nul || exit /b 0'
                    bat 'docker network rm network1 2>nul || exit /b 0'
                }
            }

            // Publish Security Reports
            publishHTML([
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: "${REPORT_DIR}",
                reportFiles: "trivy_report.html,zap_full_report.html",
                reportName: "Security Reports"
            ])
        }
    }
}
