def runCmd(cmd) {
    if (isUnix()) { sh(script: cmd) }
    else { bat(script: cmd) }
}

pipeline {
    agent any

    environment {
        GRYPE_PATH = "C:\\Program Files\\Grype"
        PATH = "${GRYPE_PATH};C:\\trivy_0.67.2_windows-64bit;C:\\Program Files\\Snyk;${env.PATH}"
}

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
                    bat 'rmdir /S /Q reports || echo "no reports"'
                    bat 'mkdir reports'

                    bat '''
                        trivy image --format json ^
                        -o reports\\trivy_report.json ^
                        --severity MEDIUM,HIGH,CRITICAL ^
                        sreyassharma/signed_images_jenkins:1.0.1 ^
                        || exit 0
                    '''

                    bat '''
                        trivy image --format template ^
                        --template "@tplFormat\\html.tpl" ^
                        -o reports\\trivy_report.html ^
                        --severity MEDIUM,HIGH,CRITICAL ^
                        sreyassharma/signed_images_jenkins:1.0.1 ^
                        || exit 0
                    '''
                }
            }
        }

        stage("Snyk SAST Scan") {
            steps {
                script {
                    bat "if not exist reports mkdir reports"

                    withCredentials([string(credentialsId: 'SnykToken', variable: 'SNYK_TOKEN')]) {

                        echo "Authenticating Snyk..."
                        bat "snyk auth %SNYK_TOKEN%"

                        echo "Running Snyk SAST..."
                        bat "snyk code test --json > reports\\snyk_source_report.json || exit 0"

                        echo "Running Snyk Container Scan..."
                        bat "snyk container test sreyassharma/signed_images_jenkins:1.0.1 --json > reports\\snyk_container_report.json || exit 0"

                        echo "Generating HTML Reports..."
                        bat "npx snyk-to-html -i reports\\snyk_source_report.json -o reports\\snyk_source_report.html || exit 0"
                        bat "npx snyk-to-html -i reports\\snyk_container_report.json -o reports\\snyk_container_report.html || exit 0"
                    }
                }
            }

            post {
                always {
                    archiveArtifacts artifacts: 'reports/snyk_*', fingerprint: true

                    publishHTML([
                        allowMissing: true,
                        keepAll: true,
                        alwaysLinkToLastBuild: true,
                        reportDir: 'reports',
                        reportFiles: 'snyk_source_report.html',
                        reportName: 'Snyk SAST Report'
                    ])

                    publishHTML([
                        allowMissing: true,
                        keepAll: true,
                        alwaysLinkToLastBuild: true,
                        reportDir: 'reports',
                        reportFiles: 'snyk_container_report.html',
                        reportName: 'Snyk Container Report'
                    ])
                }
            }
        }

        stage("Grype Scan") {
            steps {
                script {
                    echo "Running Grype vulnerability scan on Docker image..."

                    bat "if not exist reports mkdir reports"
                    
                    bat """
                        grype sreyassharma/signed_images_jenkins:1.0.1 ^
                        -o json > reports\\grype_report.json || exit 0
                    """

                    bat """
                        grype sreyassharma/signed_images_jenkins:1.0.1 ^
                        -o table > reports\\grype_report.txt || exit 0
                    """
                }
            }

            post {
                always {
                    echo "Publishing Grype Reports..."

                    archiveArtifacts artifacts: 'reports/grype_*', fingerprint: true

                    publishHTML([
                        allowMissing: true,
                        keepAll: true,
                        alwaysLinkToLastBuild: true,
                        reportDir: 'reports',
                        reportFiles: 'grype_report.txt',
                        reportName: 'Grype Vulnerability Report'
                    ])
                }
            }
        }
  

        stage("Push Docker Image") {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'Docker', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        bat "echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin"
                        bat "docker push sreyassharma/signed_images_jenkins:1.0.1"
                    }
                }
            }
        }

        stage("Sign Docker Image") {
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'CosignPrivateKey', variable: 'COSIGN_KEY'),
                        string(credentialsId: 'CosignPassword', variable: 'COSIGN_PASSWORD')
                    ]) {
                        bat '''
                            echo %COSIGN_KEY% > cosign.key
                            cosign sign --key cosign.key --pass-env COSIGN_PASSWORD docker.io/sreyassharma/signed_images_jenkins:1.0.1
                            del cosign.key
                        '''
                    }
                }
            }
        }

        stage("Create Network") {
            steps {
                script {
                    bat 'docker network inspect network1 >nul 2>&1 || docker network create network1'
                }
            }
        }

        stage("Run App Container") {
            steps {
                script {
                    bat '''
                        docker run -d --rm ^
                        --network network1 ^
                        --name demo_app_running ^
                        -p 8123:80 ^
                        sreyassharma/signed_images_jenkins:1.0.1
                    '''
                    bat "ping -n 8 127.0.0.1 >nul"
                }
            }
        }

        stage("OWASP ZAP Scan") {
            steps {
                script {
                    bat '''
                        docker run --rm ^
                        --network network1 ^
                        -v %cd%\\reports:/zap/wrk/ ^
                        ghcr.io/zaproxy/zaproxy:stable zap-full-scan.py ^
                            -t http://demo_app_running:80 ^
                            -r zap_full_report.html ^
                            -J zap_full_report.json ^
                            -a || exit 0
                    '''
                }
            }
        }
    }

    post {
        always {
            script {
                bat 'docker stop demo_app_running || exit 0'
                bat 'docker network rm network1 || exit 0'
            }

            publishHTML([
                allowMissing: true,
                keepAll: true,
                alwaysLinkToLastBuild: true,
                reportDir: 'reports',
                reportFiles: 'trivy_report.html,zap_full_report.html',
                reportName: 'Security Reports'
            ])
        }
    }
}
