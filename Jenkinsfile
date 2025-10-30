pipeline {
    agent any

    stages {
        stage("Hello") {
            steps {
                echo "hello World!"
            }
        }

        stage("trivy") {
            steps {
                sh "trivy image demo_app"
            }
        }
    }
}
