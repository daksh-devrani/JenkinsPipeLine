def runCmd(cmd) {
    if (isUnix()) { sh(script: cmd) }
    else { bat(script: cmd) }
}

pipeline {
    agent any

    environment {
        TRIVY_PATH = "C:\\trivy_0.67.2_windows-64bit"
        GRYPE_PATH = "C:\\grype_0.104.0_windows_amd64"
        SNYK_PATH  = "C:\\Program Files\\Snyk"

        PATH = "${TRIVY_PATH};${GRYPE_PATH};${SNYK_PATH};${env.PATH}"
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

                        bat "snyk auth %SNYK_TOKEN%"
                        bat "snyk code test --json > reports\\snyk_source_report.json || exit 0"
                        bat "snyk container test sreyassharma/signed_images_jenkins:1.0.1 --json > reports\\snyk_container_report.json || exit 0"
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

                    bat "if not exist reports mkdir reports"

                    def grypeStatus = bat(returnStatus: true, script: 'where grype')
                    if (grypeStatus != 0) {
                        echo "WARNING: Grype not found on PATH. Make sure Grype is installed on the Jenkins agent."
                    }

                    bat "%COMSPEC% /C grype sreyassharma/signed_images_jenkins:1.0.1 -o json > \"%cd%\\reports\\grype_report.json\" || exit 0"
                    bat "%COMSPEC% /C grype sreyassharma/signed_images_jenkins:1.0.1 -o table > \"%cd%\\reports\\grype_report.txt\" || exit 0"

                    def foundHigh = bat(returnStatus: true, script: '%COMSPEC% /C findstr /I "CRITICAL HIGH" "%cd%\\reports\\grype_report.json"')
                    if (foundHigh == 0) {
                        echo "Grype found HIGH or CRITICAL vulnerabilities. Marking build UNSTABLE."
                        currentBuild.result = 'UNSTABLE'
                    } else {
                        echo "No HIGH/CRITICAL vulnerabilities discovered by simple string check."
                    }
                }
            }

            post {
                always {

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

        
    }
}
