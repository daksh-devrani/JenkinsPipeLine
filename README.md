# Jenkins CI/CD Pipeline with Security Scanning and Signing

This repository contains a Jenkins pipeline (`Jenkinsfile`) that builds, scans, signs, and deploys Docker images with multiple security tools integrated. The pipeline ensures that container images are tested against vulnerabilities and monitored before being pushed to a registry.

---

## 📋 Features

- **Docker Build & Cleanup**
  - Builds a Docker image from the project source.
  - Cleans up unused Docker images to save space.

- **Security Scanning**
  - **Trivy**: Scans Docker images for vulnerabilities and generates JSON/HTML reports.
  - **Snyk**: Performs open-source dependency and container vulnerability scanning.
  - **Grype**: Scans Docker images for vulnerabilities with JSON and table outputs.
  - **OWASP ZAP**: Performs dynamic application security testing (DAST) against the running container.
  - **Suricata**: Monitors network traffic for suspicious activity.

- **Image Signing**
  - Uses **Cosign** to sign Docker images with private keys for supply chain security.

- **Deployment**
  - Pushes signed Docker images to Docker Hub.
  - Runs the application container in a custom Docker network.
  - Runs Suricata and OWASP ZAP containers for monitoring and scanning.

- **Reporting**
  - Publishes consolidated HTML reports in Jenkins (`PublishHTML` plugin).
  - Reports include results from Trivy, Grype, Snyk, OWASP ZAP, and Suricata.

---

## ⚙️ Prerequisites

- Jenkins with the following plugins:
  - **Pipeline**
  - **Snyk Security**
  - **Publish HTML Reports**
- Installed tools on Jenkins agent:
  - Docker
  - Trivy
  - Grype
  - Snyk CLI
  - Cosign
- Credentials configured in Jenkins:
  - `SnykToken` → Snyk API token
  - `Docker` → Docker Hub username/password
  - `CosignPrivateKey` → Cosign private key
  - `CosignPassword` → Cosign key password

---

## 🚀 Pipeline Stages

| Stage                | Description                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| **Build Docker Image** | Builds the application Docker image.                                       |
| **Cleanup Docker**     | Removes unused Docker images.                                              |
| **Trivy Scan**         | Scans image for vulnerabilities and generates reports.                     |
| **Snyk Security Scan** | Runs Snyk scan for open-source and container vulnerabilities.               |
| **Grype Scan**         | Scans image for vulnerabilities and outputs JSON/table reports.             |
| **Push Docker Image**  | Pushes the signed image to Docker Hub.                                     |
| **Sign Docker Image**  | Signs the image using Cosign with private key.                             |
| **Create Network**     | Creates a custom Docker network for containers.                            |
| **Run App Container**  | Runs the application container in the network.                             |
| **Suricata Monitoring**| Runs Suricata IDS to monitor network traffic.                              |
| **OWASP ZAP Scan**     | Performs DAST scan against the running app container.                      |
| **Publish Reports**    | Publishes consolidated security reports in Jenkins.                        |

---

## 📂 Reports Generated

- `reports/trivy_report.json`
- `reports/trivy_report.html`
- `reports/grype_report.json`
- `reports/grype_report.txt`
- `reports/snyk_source_report.html`
- `reports/snyk_container_report.html`
- `reports/zap_full_report.html`
- `reports/zap_full_report.json`
- `reports/eve.json` (Suricata logs)

---

## ▶️ Usage

1. Configure Jenkins with required plugins and credentials.
2. Place the provided `Jenkinsfile` in your repository root.
3. Trigger the pipeline from Jenkins.
4. View consolidated reports in Jenkins under **Security Reports**.

---

## 🔒 Security Notes

- Ensure your **Snyk API token** and **Cosign private key** are stored securely in Jenkins credentials.
- Regularly update Trivy, Grype, Snyk, and Cosign to their latest versions for accurate scanning.
- Review reports after each build to address vulnerabilities promptly.

---

## 📜 License

This pipeline is provided as-is for educational and security automation purposes. Modify and adapt it to fit your project needs.
