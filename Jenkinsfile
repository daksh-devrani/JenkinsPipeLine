def runCmd(cmd) {
    if (isUnix()) sh(script: cmd)
    else bat(script: cmd)
}

pipeline {
    agent any

    environment {
        FILE_SEP = isUnix() ? "/" : "\\"
        PWD_CMD = isUnix() ? "pwd" : "cd"
        REPORT_DIR = "reports"
    }

    stages {

        /* -----------------------------
              Build Docker Image
        ------------------------------*/
        stage("Build Docker Image") {
            steps {
                script {
                    runCmd "docker build -t sreyassharma/signed_images_jenkins:1.0.1 ."
                }
            }
        }

        /* -----------------------------
                Cleanup Docker
        ------------------------------*/
        stage("Cleanup Docker") {
            steps {
                script {
                    runCmd "docker image prune -f"
                }
            }
        }

        /* -----------------------------
                 TRIVY Scan
        ------------------------------*/
        stage("Trivy Scan") {
            steps {
                script {
                    // Remove reports folder
                    if (isUnix())
                        runCmd "rm -rf ${REPORT_DIR}"
                    else
                        runCmd "rmdir /S /Q ${REPORT_DIR} || echo no reports"

                    runCmd "mkdir ${REPORT_DIR}"

                    // JSON Report
                    runCmd """
                        trivy image --format json \
                        -o ${REPORT_DIR}${FILE_SEP}trivy_report.json \
                        --severity MEDIUM,HIGH,CRITICAL \
                        sreyassharma/signed_images_jenkins:1.0.1 || exit 0
                    """

                    // HTML Report
                    runCmd """
                        trivy image --format template \
                        --template @tplFormat/html.tpl \
                        -o ${REPORT_DIR}${FILE_SEP}trivy_report.html \
                        --severity MEDIUM,HIGH,CRITICAL \
                        sreyassharma/signed_images_jenkins:1.0.1 || exit 0
                    """
                }
            }
        }

        /* -----------------------------
                SNYK SAST & Container
        ------------------------------*/
        stage("Snyk SAST Scan") {
            steps {
                script {
                    runCmd "mkdir ${REPORT_DIR}"

                    withCredentials([string(credentialsId: 'SnykToken', variable: 'SNYK_TOKEN')]) {

                        // Authenticate
                        runCmd "snyk auth ${SNYK_TOKEN}"

                        // SAST
                        runCmd "snyk code test --json > ${REPORT_DIR}${FILE_SEP}snyk_source_report.json || exit 0"

                        // Container
                        runCmd "snyk container test sreyassharma/signed_images_jenkins:1.0.1 --json > ${REPORT_DIR}${FILE_SEP}snyk_container_report.json || exit 0"

                        // HTML Convert
                        runCmd "npx snyk-to-html -i ${REPORT_DIR}${FILE_SEP}snyk_source_report.json -o ${REPORT_DIR}${FILE_SEP}snyk_source_report.html"
                        runCmd "npx snyk-to-html -i ${REPORT_DIR}${FILE_SEP}snyk_container_report.json -o ${REPORT_DIR}${FILE_SEP}snyk_container_report.html"
                    }
                }
            }

            post {
                always {
                    archiveArtifacts artifacts: "${REPORT_DIR}/snyk_*", fingerprint: true
                    publishHTML([
                        allowMissing: true,
                        keepAll: true,
                        alwaysLinkToLastBuild: true,
                        reportDir: REPORT_DIR,
                        reportFiles: 'snyk_source_report.html',
                        reportName: 'Snyk SAST Report'
                    ])
                }
            }
        }

        /* -----------------------------
                GRYPE Scan
        ------------------------------*/
        stage("Grype Scan") {
            steps {
                script {
                    runCmd "mkdir ${REPORT_DIR}"

                    runCmd "grype sreyassharma/signed_images_jenkins:1.0.1 -o json > ${REPORT_DIR}${FILE_SEP}grype_report.json || exit 0"
                    runCmd "grype sreyassharma/signed_images_jenkins:1.0.1 -o table > ${REPORT_DIR}${FILE_SEP}grype_report.txt || exit 0"

                    // Check HIGH/CRITICAL
                    def checkCmd = isUnix() ?
                        "grep -Ei 'CRITICAL|HIGH' ${REPORT_DIR}${FILE_SEP}grype_report.json" :
                        "findstr /I \"CRITICAL HIGH\" ${REPORT_DIR}${FILE_SEP}grype_report.json"

                    def status = runCmd(checkCmd)

                    if (status == 0) {
                        echo "HIGH/CRITICAL vulnerabilities found → UNSTABLE"
                        currentBuild.result = "UNSTABLE"
                    }
                }
            }

            post {
                always {
                    archiveArtifacts artifacts: "${REPORT_DIR}/grype_*", fingerprint: true
                    publishHTML([
                        allowMissing: true,
                        keepAll: true,
                        alwaysLinkToLastBuild: true,
                        reportDir: REPORT_DIR,
                        reportFiles: 'grype_report.txt',
                        reportName: 'Grype Report'
                    ])
                }
            }
        }

        /* -----------------------------
                Docker Push
        ------------------------------*/
        stage("Push Docker Image") {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'Docker', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        runCmd "echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin"
                        runCmd "docker push sreyassharma/signed_images_jenkins:1.0.1"
                    }
                }
            }
        }

        /* -----------------------------
                Cosign Signing
        ------------------------------*/
        stage("Sign Docker Image") {
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'CosignPrivateKey', variable: 'COSIGN_KEY'),
                        string(credentialsId: 'CosignPassword', variable: 'COSIGN_PASSWORD')
                    ]) {
                        writeFile file: "cosign.key", text: COSIGN_KEY
                        runCmd "cosign sign --key cosign.key --pass-env COSIGN_PASSWORD docker.io/sreyassharma/signed_images_jenkins:1.0.1"
                        runCmd (isUnix() ? "rm cosign.key" : "del cosign.key")
                    }
                }
            }
        }

        /* -----------------------------
                Network Create
        ------------------------------*/
        stage("Create Network") {
            steps {
                script {
                    runCmd "docker network inspect network1 >/dev/null 2>&1 || docker network create network1"
                }
            }
        }

        /* -----------------------------
              Run Application
        ------------------------------*/
        stage("Run App Container") {
            steps {
                script {
                    runCmd "docker run -d --rm --network network1 --name demo_app_running -p 8123:80 sreyassharma/signed_images_jenkins:1.0.1"

                    // Sleep 8 seconds
                    runCmd (isUnix() ? "sleep 8" : "ping -n 8 127.0.0.1 >nul")
                }
            }
        }

        /* -----------------------------
                ZAP Scan
        ------------------------------*/
        stage("OWASP ZAP Scan") {
            steps {
                script {
                    // Cross-platform working directory
                    def currentDir = sh(script: "pwd", returnStdout: true).trim()
                    if (!isUnix()) currentDir = bat(script: "cd", returnStdout: true).trim()

                    runCmd """
                        docker run --rm \
                        --network network1 \
                        -v ${currentDir}${FILE_SEP}${REPORT_DIR}:/zap/wrk/ \
                        ghcr.io/zaproxy/zaproxy:stable zap-full-scan.py \
                            -t http://demo_app_running:80 \
                            -r zap_full_report.html \
                            -J zap_full_report.json \
                            -a || exit 0
                    """
                }
            }
        }
    }

    /* -----------------------------
                Final Cleanup
    ------------------------------*/
    post {
        always {
            script {
                runCmd "docker stop demo_app_running || exit 0"
                runCmd "docker network rm network1 || exit 0"
            }

            publishHTML([
                allowMissing: true,
                keepAll: true,
                alwaysLinkToLastBuild: true,
                reportDir: REPORT_DIR,
                reportFiles: "trivy_report.html,zap_full_report.html",
                reportName: "Security Reports"
            ])
        }
    }
}
