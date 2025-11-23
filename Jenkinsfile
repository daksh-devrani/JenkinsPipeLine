pipeline {
    agent any

    environment {
        PATH = "C:\\trivy_0.67.2_windows-64bit;C:\\Program Files\\Snyk;${env.PATH}"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout([$class: 'GitSCM',
                    branches: [[name: '*/master']],
                    userRemoteConfigs: [[
                        url: 'https://github.com/ShivangMangal/JenkinsPipeLineTry_01.git',
                        credentialsId: 'GitHub'
                    ]]
                ])
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    bat """
                        docker build -t sreyassharma/signed_images_jenkins:1.0.1 .
                    """
                }
            }
        }

        stage('Cleanup Docker') {
            steps {
                bat "docker image prune -f || exit 0"
            }
        }

        stage('Trivy Scan') {
            steps {
                script {
                    bat """
                        rmdir /S /Q reports || echo No reports
                        mkdir reports

                        echo Running Trivy...

                        trivy image --format json ^
                            -o reports\\trivy_report.json ^
                            --severity MEDIUM,HIGH,CRITICAL ^
                            sreyassharma/signed_images_jenkins:1.0.1 || exit 0

                        trivy image --format template ^
                            --template "@tplFormat\\html.tpl" ^
                            -o reports\\trivy_report.html ^
                            --severity MEDIUM,HIGH,CRITICAL ^
                            sreyassharma/signed_images_jenkins:1.0.1 || exit 0
                    """
                }
            }
        }

        stage('Snyk SAST Scan') {
            steps {
                withCredentials([string(credentialsId: 'SnykToken', variable: 'SNYK_TOKEN')]) {
                    script {
                        bat """
                            if not exist reports mkdir reports

                            echo Authenticating Snyk...
                            snyk auth %SNYK_TOKEN% || exit 0

                            echo Running Snyk SAST...
                            snyk code test --json > reports\\snyk_sast.json || exit 0

                            echo Running Snyk Container Scan...
                            snyk container test sreyassharma/signed_images_jenkins:1.0.1 --json > reports\\snyk_container.json || exit 0
                        """
                    }
                }
            }
        }

        stage('Push Docker Image') {
            when { expression { false } }
            steps { echo "Skipping push for now." }
        }

        stage('Sign Docker Image') {
            when { expression { false } }
            steps { echo "Skipping signing for now." }
        }

        stage('Create Network') {
            steps {
                bat "docker network create network1 || exit 0"
            }
        }

        stage('Run App Container') {
            steps {
                bat """
                    docker run -d --name demo_app_running --network network1 -p 8080:80 sreyassharma/signed_images_jenkins:1.0.1 || exit 0
                """
            }
        }

        stage('OWASP ZAP Scan') {
            when { expression { false } }
            steps { echo "Skipping ZAP for now." }
        }
    }

    post {
        always {
            script {
                bat "docker stop demo_app_running || exit 0"
                bat "docker rm demo_app_running || exit 0"
                bat "docker network rm network1 || exit 0"
            }

            archiveArtifacts artifacts: 'reports/**/*.*', fingerprint: true

            publishHTML([
                reportDir: 'reports',
                reportFiles: 'trivy_report.html',
                reportName: 'Trivy Vulnerability Report',
                keepAll: true,
                alwaysLinkToLastBuild: true
            ])

            publishHTML([
                reportDir: 'reports',
                reportFiles: 'snyk_sast.json',
                reportName: 'Snyk SAST Report',
                keepAll: true,
                alwaysLinkToLastBuild: true
            ])

            publishHTML([
                reportDir: 'reports',
                reportFiles: 'snyk_container.json',
                reportName: 'Snyk Container Report',
                keepAll: true,
                alwaysLinkToLastBuild: true
            ])
        }
    }
}
