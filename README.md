# Jenkins Pipeline for Secure Docker Image Build & Scan 🔐🐳

This repository contains a **Jenkins pipeline script** that automates the process of building, scanning, signing, and deploying Docker images with multiple security tools integrated. It ensures that container images are thoroughly tested for vulnerabilities before being pushed and signed.

---

## 📋 Features

- **Cross-platform support**: Works on both Unix (Linux/macOS) and Windows agents.
- **Docker build & cleanup**: Builds the application image and prunes unused images.
- **Security Scans**:
  - **Trivy**: Scans Docker images for vulnerabilities and generates JSON/HTML reports.
  - **Snyk**: Performs dependency and container scans with HTML/JSON reports.
  - **Grype**: Scans images for vulnerabilities with JSON and table outputs.
- **Image Signing**:
  - Uses **Cosign** to sign Docker images with private keys and passwords stored in Jenkins credentials.
- **Network & Monitoring**:
  - Creates a custom Docker network.
  - Runs the application container.
  - Deploys **Suricata IDS** for monitoring traffic and logs events (`eve.json`).
- **Dynamic Application Security Testing (DAST)**:
  - Runs **OWASP ZAP** scans against the running container.
  - Generates HTML and JSON reports.
- **Automated Cleanup**:
  - Stops containers, removes networks, and publishes reports after pipeline execution.
- **Report Publishing**:
  - Consolidates all security reports into Jenkins via `publishHTML`.

---

## 🛠️ Requirements

- Jenkins with Docker installed on agents.
- Installed tools:
  - [Trivy](https://aquasecurity.github.io/trivy/)
  - [Snyk](https://snyk.io/)
  - [Grype](https://github.com/anchore/grype)
  - [Cosign](https://github.com/sigstore/cosign)
- Docker Hub account (for pushing signed images).
- Jenkins plugins:
  - **Pipeline**
  - **Publish HTML Reports**
- Credentials configured in Jenkins:
  - `Docker` → Username & Password for Docker Hub.
  - `SnykToken_Text` → Snyk API token.
  - `CosignPrivateKey` → Cosign private key.
  - `CosignPassword` → Cosign key password.

---

## 📂 Pipeline Stages Overview

| Stage                  | Description                                                                 |
|-------------------------|-----------------------------------------------------------------------------|
| **Build Docker Image**  | Builds the application Docker image.                                        |
| **Cleanup Docker**      | Removes unused Docker images.                                               |
| **Trivy Scan**          | Runs Trivy vulnerability scan (JSON + HTML reports).                        |
| **Snyk Security Scan**  | Runs Snyk dependency & container scans (JSON + HTML reports).                |
| **Grype Scan**          | Runs Grype vulnerability scan (JSON + TXT reports).                         |
| **Push Docker Image**   | Pushes the image to Docker Hub.                                             |
| **Sign Docker Image**   | Signs the image using Cosign.                                               |
| **Create Network**      | Creates a Docker network for containers.                                    |
| **Run App Container**   | Runs the application container on port `8123`.                              |
| **Suricata Monitoring** | Deploys Suricata IDS to monitor traffic and logs events.                    |
| **OWASP ZAP Scan**      | Runs OWASP ZAP full scan against the running app (HTML + JSON reports).     |
| **Post Actions**        | Stops containers, removes networks, and publishes reports in Jenkins.       |

---

## 📊 Reports Generated

All reports are stored in the `reports/` directory and published in Jenkins:

- `trivy_report.html` / `trivy_report.json`
- `snyk_source_report.html` / `snyk_source_report.json`
- `snyk_container_report.html` / `snyk_container_report.json`
- `grype_report.txt` / `grype_report.json`
- `zap_full_report.html` / `zap_full_report.json`
- `eve.json` (Suricata logs)

---

## 🚀 Usage

1. Clone this repository into your Jenkins workspace.
2. Configure required credentials in Jenkins.
3. Ensure Docker and security tools are installed on the agent.
4. Run the pipeline from Jenkins.
5. View consolidated **Security Reports** in Jenkins under the build results.

---

## ⚠️ Notes

- The pipeline is designed to **continue execution even if vulnerabilities are found** (using `|| true` or `exit /b 0`).
- You can modify the pipeline to **fail builds on critical vulnerabilities** by uncommenting the relevant logic in the Grype stage.
- Ensure proper permissions for mounted volumes when running OWASP ZAP and Suricata.

---

## 📜 License
This project is for demonstration purposes.  
Feel free to adapt and extend it for your own CI/CD workflows.
