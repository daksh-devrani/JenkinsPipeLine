Secure CI/CD Pipeline with Jenkins, Docker, Trivy, Cosign, Snyk & OWASP ZAP

This repository demonstrates a Jenkins pipeline that builds, scans, signs, and runs a Dockerized application with integrated security checks.
A simple React demo project is used as the application under test.

🚀 Pipeline Overview

The Jenkins pipeline (Jenkinsfile) automates the following stages:

Build Docker Image

Builds the application image:
docker build -t sreyassharma/signed_images_jenkins:1.0.1 .

Cleanup Docker

Removes unused images to save space:
docker image prune -f

Trivy Scan

Runs Trivy
 vulnerability scans:

JSON report → reports/trivy_report.json

HTML report → reports/trivy_report.html

Scans for MEDIUM, HIGH, CRITICAL severity issues.

Snyk Security Scanning

Integrates Snyk
 to perform full security checks:

Snyk SAST (source code & dependency scanning)

Reports: reports/snyk_sast.json, reports/snyk_sast.html

Snyk Container Scan (Docker image vulnerability scanning)

Reports: reports/snyk_container.json, reports/snyk_container.html

Authenticates using Jenkins credentials (SnykToken).

Push Docker Image

Authenticates with Docker Hub using Jenkins credentials.

Pushes the image:
docker push sreyassharma/signed_images_jenkins:1.0.1

Sign Docker Image

Uses Cosign
 to sign the container image.

Credentials (CosignPrivateKey, CosignPassword) are securely injected.

Create Network

Creates a Docker network (network1) if it doesn’t already exist.

Run App Container

Runs the demo React app container on port 8123.

OWASP ZAP Scan

Executes OWASP ZAP
 baseline DAST scan against the running app.

Outputs:

HTML report → reports/zap_report.html

JSON report → reports/zap_report.json

Post Actions

Stops containers and removes the network.

Publishes all HTML reports in Jenkins under Security Reports.

📂 Reports Generated

reports/trivy_report.json

reports/trivy_report.html

reports/snyk_sast.json

reports/snyk_sast.html

reports/snyk_container.json

reports/snyk_container.html

reports/zap_report.json

reports/zap_report.html

All reports are published in Jenkins using the Publish HTML Reports plugin.

🛠️ Requirements

Jenkins with Docker installed

Plugins:

Pipeline

Publish HTML Reports

Tools installed on Jenkins agents:

Docker

Trivy

Cosign

Snyk CLI

Credentials configured in Jenkins:

Docker → Docker Hub username/password

CosignPrivateKey → Private key string

CosignPassword → Password for Cosign key

SnykToken → API token for Snyk authentication

🧪 Demo React Project

A simple React project is used to test the pipeline.
You can replace it with any application — just make sure the Dockerfile is present in the repository.

🔒 Security Highlights

Trivy → Container vulnerability scanning

Snyk SAST → Source code & dependency vulnerability analysis

Snyk Container Scan → Image-level security scanning

Cosign → Secure container image signing

OWASP ZAP → Automated DAST scanning

This pipeline integrates end-to-end DevSecOps practices directly into the CI/CD process.

▶️ Usage

Clone this repository.

Configure Jenkins with the required credentials.

Run the pipeline.

View results in Jenkins under Security Reports.

📌 Notes

The pipeline supports both Unix and Windows agents.

All security tools generate reports even if scans fail (|| true).

Temporary signing files (e.g., cosign.key) are securely deleted after use.

Snyk authentication requires a valid API token configured in Jenkins.

📖 License

This project is for demonstration purposes.
Feel free to adapt and extend it for your own CI/CD workflows.
