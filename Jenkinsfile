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
        GRYPE_PATH = "C:\\grype_0.104.0_windows_amd64"
        TRIVY_PATH = "C:\\trivy_0.67.2_windows-64bit"
        SNYK_PATH  = "C:\\Program Files\\Snyk"

        PATH = "${GRYPE_PATH};${TRIVY_PATH};${SNYK_PATH};${env.PATH}"
    }

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
                        // sh 'rm -rf reports'
                        // sh 'mkdir -p reports'
                        runCmd 'curl -L https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/html.tpl -o reports/html.tpl'
                        sh 'trivy image --format json -o reports/trivy_report.json --severity MEDIUM,HIGH,CRITICAL sreyassharma/signed_images_jenkins:1.0.1 || true'
                        sh 'trivy image --format template --template "@reports/html.tpl" -o reports/trivy_report.html --severity MEDIUM,HIGH,CRITICAL sreyassharma/signed_images_jenkins:1.0.1 || true'
                    } else {
                        bat 'rmdir /S /Q reports || echo No reports dir'
                        bat 'mkdir reports'
                        runCmd 'curl -L https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/html.tpl -o reports\\html.tpl'
                        bat 'trivy image --format json -o reports\\trivy_report.json --severity MEDIUM,HIGH,CRITICAL sreyassharma/signed_images_jenkins:1.0.1 || exit /b 0'
                        bat 'trivy image --format template --template "@reports\\html.tpl" -o reports\\trivy_report.html --severity MEDIUM,HIGH,CRITICAL sreyassharma/signed_images_jenkins:1.0.1 || exit /b 0'
                    }
                }
            }
        }

        stage('Snyk Security Scan') {
            steps {
                withCredentials([string(credentialsId: 'SnykToken_Text', variable: 'SNYK_TOKEN')]) {
                    script {
                        if (isUnix()) {
                            // Authenticate once
                            sh 'snyk auth $SNYK_TOKEN'

                            sh 'npm install'
                            // Source (dependency) scan
                            sh 'snyk test --json > reports/snyk_source_report.json || true'
                            sh 'snyk test --json | snyk-to-html -o reports/snyk_source_report.html || true'

                            // Container image scan
                            sh 'snyk container test sreyassharma/signed_images_jenkins:1.0.1 --json > reports/snyk_container_report.json || true'
                            sh 'snyk container test sreyassharma/signed_images_jenkins:1.0.1 --json | snyk-to-html -o reports/snyk_container_report.html || true'

                        } else {
                            bat "snyk auth %SNYK_TOKEN%"

                            // Source (dependency) scan
                            bat "snyk test --json > reports\\snyk_source_report.json || exit /b 0"
                            bat "snyk test --json | snyk-to-html -o reports\\snyk_source_report.html || exit /b 0"

                            // Container image scan
                            bat "snyk container test sreyassharma/signed_images_jenkins:1.0.1 --json > reports\\snyk_container_report.json || exit /b 0"
                            bat "snyk container test sreyassharma/signed_images_jenkins:1.0.1 --json | snyk-to-html -o reports\\snyk_container_report.html || exit /b 0"
                        }
                    }
                }
            }
        }

        stage("Grype Scan") {
            steps {
                script {

                    if(isUnix()) {
                        sh '''
                        grype sreyassharma/signed_images_jenkins:1.0.1 -o json > reports/grype_report.json || exit 0
                        grype sreyassharma/signed_images_jenkins:1.0.1 -o table > reports/grype_report.txt || exit 0
                        '''

                    }

                    else{
                        bat "\"${GRYPE_PATH}\\grype.exe\" sreyassharma/signed_images_jenkins:1.0.1 -o json > reports\\grype_report.json || exit 0"
                        bat "\"${GRYPE_PATH}\\grype.exe\" sreyassharma/signed_images_jenkins:1.0.1 -o table > reports\\grype_report.txt || exit 0"

                        // def foundHigh = bat(returnStatus: true, script: 'findstr /I "CRITICAL HIGH" reports\\grype_report.json')
                        // if (foundHigh == 0) {
                        //     echo "HIGH/CRITICAL vulnerabilities found — marking build UNSTABLE"
                        //     currentBuild.result = 'UNSTABLE'
                        // } else {
                        //     echo "No HIGH/CRITICAL vulnerabilities found"
                        // }
                    }

                }
            }
        }

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

        // i can use digest but is bit complex
        stage("Sign Docker Image") {
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'CosignPrivateKey', variable: 'COSIGN_KEY'),
                        string(credentialsId: 'CosignPassword', variable: 'COSIGN_PASSWORD')
                    ]) {
                        if (isUnix()) {
                            sh '''
                                cat > cosign.key <<EOF
                                    $COSIGN_KEY
                                    EOF

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

        stage("Suricata Monitoring") {
            steps {
                script {

                    if(isUnix()){
                        sh ''' 
                            docker run -d --rm \
                                --name suricata \
                                --network network1 \
                                --cap-add=NET_ADMIN \
                                --cap-add=NET_RAW \
                                jasonish/suricata \
                                suricata -i eth0 -c /etc/suricata/suricata.yaml -l /var/log/suricata/

                            sleep 10

                            docker cp suricata:/var/log/suricata/eve.json reports/eve.json
                        '''
                    }

                    else{
                        bat """
                            docker run -d --rm ^
                                --name suricata ^
                                --network network1 ^
                                --cap-add=NET_ADMIN ^
                                --cap-add=NET_RAW ^
                                jasonish/suricata ^
                                suricata -i eth0 -c /etc/suricata/suricata.yaml -l /var/log/suricata/

                            ping -n 10 127.0.0.1 >nul

                            docker cp suricata:/var/log/suricata/eve.json reports\\suricata\\eve.json
                        """
                    }
                }
            }
        }

        stage("Convert Suricata Report") {
            steps {
                script {
                    if (isUnix()) {
                        sh 'python3 scripts/eve_to_html.py'
                    } else {
                        bat 'python scripts\\eve_to_html.py'
                    }
                }
            }
        }


        stage("OWASP ZAP Scan") {
		    steps {
		        script {
		            if (isUnix()) {
		                // sh 'chmod -R 777 reports'
		
		                sh '''
		                    docker run --rm \
		                    --network network1 \
		                    -v $(pwd)/reports:/zap/wrk/ \
		                    ghcr.io/zaproxy/zaproxy:stable zap.sh -cmd \
		                        -addonupdate \
		                        -addoninstall ascanrulesAlpha \
		                        -addoninstall ascanrulesBeta \
		                        -addoninstall pscanrulesAlpha \
		                        -addoninstall pscanrulesBeta \
		                        -addoninstall retire \
		                        -addoninstall fuzzer \
		                        -addoninstall openapi \
		                        -addoninstall graphql \
		                        -addoninstall log4shell
		
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
		                    ghcr.io/zaproxy/zaproxy:stable zap.sh -cmd^
		                        -addonupdate ^
		                        -addoninstall ascanrulesAlpha ^
		                        -addoninstall ascanrulesBeta ^
		                        -addoninstall pscanrulesAlpha ^
		                        -addoninstall pscanrulesBeta ^
		                        -addoninstall retire ^
		                        -addoninstall fuzzer ^
		                        -addoninstall openapi ^
		                        -addoninstall graphql ^
		                        -addoninstall log4shell
		
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

    post {
        always {
            script {
                runCmd 'docker stop demo_app_running || exit 0'
                runCmd 'docker stop suricata || exit 0'
                runCmd 'docker network rm network1 || exit 0'
            }

            publishHTML([
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'reports',
                reportFiles: 'index.html, trivy_report.html, snyk_source_report.html, snyk_container_report.html, zap_full_report.html, grype_report.txt,eve_report.html',
                reportName: 'Security Reports'
            ])
        }
    }
}
