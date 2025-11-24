pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "sreyassharma/signed_images_jenkins:1.0.1"
    }

    stages {

        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    bat """
                        docker build -t %DOCKER_IMAGE% .
                    """
                }
            }
        }

        stage('Cleanup Docker') {
            steps {
                script {
                    bat "docker image prune -f"
                }
            }
        }

        stage('Trivy Scan') {
            steps {
                script {

                    
                    bat '''
                        if exist reports rmdir /S /Q reports
                        mkdir reports
                    '''

                    
                    bat '''
                        trivy image --format json ^
                            -o reports\\trivy_report.json ^
                            --severity MEDIUM,HIGH,CRITICAL ^
                            %DOCKER_IMAGE% || exit 0
                    '''

                    
                    bat '''
                        npx trivy-to-html -i reports\\trivy_report.json -o reports\\trivy_report.html || exit 0
                    '''
                }
            }
        }

        stage('Snyk SAST Scan') {
            steps {
                withCredentials([string(credentialsId: 'SNYK_TOKEN', variable: 'SNYK_TOKEN')]) {
                    script {

                        bat """
                            if not exist reports mkdir reports
                        """

                        
                        bat "snyk auth %SNYK_TOKEN%"

                        
                        bat """
                            snyk code test --json 1>reports\\snyk_source_report.json || exit 0
                        """

                        
                        bat """
                            snyk container test %DOCKER_IMAGE% --json 1>reports\\snyk_container_report.json || exit 0
                        """

                        
                        bat """
                            npx snyk-to-html -i reports\\snyk_source_report.json -o reports\\snyk_source_report.html || exit 0
                        """
                        bat """
                            npx snyk-to-html -i reports\\snyk_container_report.json -o reports\\snyk_container_report.html || exit 0
                        """
                    }
                }
            }
        }

        stage('Grype Scan') {
            steps {
                script {

                    bat """
                        if not exist reports mkdir reports
                    """

                    
                    bat """
                        grype %DOCKER_IMAGE% -o json 1>reports\\grype_report.json || exit 0
                    """

                    
                    bat """
                        grype %DOCKER_IMAGE% -o table 1>reports\\grype_report.txt || exit 0
                    """

                    
                    bat """
                        findstr /I "CRITICAL HIGH" reports\\grype_report.json || exit 0
                    """
                }
            }
        }
    }

    post {
        always {

            
            archiveArtifacts artifacts: 'reports/**', fingerprint: true

        
            publishHTML([
                reportDir: 'reports',
                reportFiles: 'trivy_report.html',
                reportName: 'Trivy Vulnerability Report'
            ])

            publishHTML([
                reportDir: 'reports',
                reportFiles: 'snyk_source_report.html',
                reportName: 'Snyk SAST Report'
            ])

            publishHTML([
                reportDir: 'reports',
                reportFiles: 'snyk_container_report.html',
                reportName: 'Snyk Container Report'
            ])
        }
    }
}
