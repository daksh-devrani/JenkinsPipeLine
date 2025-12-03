# 🛡️ Jenkins Security Pipeline

This repository contains a **Jenkins pipeline** that builds, scans, signs, and monitors Docker images with multiple security tools. It automates vulnerability detection, image signing, and runtime monitoring to ensure secure CI/CD workflows.

---

## 📑 Features

- **Docker Build & Cleanup**
  - Builds Docker images and prunes unused ones.
- **Security Scans**
  - **Trivy**: Scans container images for vulnerabilities (JSON + HTML reports).
  - **Snyk**: Scans dependencies and container images (JSON + HTML reports).
  - **Grype**: Scans container images for vulnerabilities (JSON + TXT reports).
- **Image Signing**
  - Uses **Cosign** to sign Docker images with private keys.
- **Runtime Monitoring**
  - **Suricata**: Network intrusion detection system (IDS) monitoring container traffic.
- **Dynamic Application Security Testing (DAST)**
  - **OWASP ZAP**: Performs automated penetration testing against the running container.
- **Report Generation**
  - Converts Suricata logs to HTML.
  - Combines all reports into a consolidated CVSS-based HTML report.
- **Automated Publishing**
  - Publishes reports in Jenkins using `publishHTML`.

---

## 📂 Pipeline Stages Overview

| Stage                  | Description                                                                 |
|-------------------------|-----------------------------------------------------------------------------|
| Build Docker Image      | Builds the application image.                                               |
| Cleanup Docker          | Removes unused Docker images.                                               |
| Trivy Scan              | Vulnerability scan with Trivy.                                              |
| Snyk Security Scan      | Dependency and container vulnerability scan with Snyk.                      |
| Grype Scan              | Vulnerability scan with Grype.                                              |
| Push Docker Image       | Pushes image to Docker Hub.                                                 |
| Sign Docker Image       | Signs image using Cosign.                                                   |
| Create Network          | Creates Docker network for containers.                                      |
| Run App Container       | Runs the application container.                                             |
| Suricata Monitoring     | Runs Suricata IDS to monitor traffic.                                       |
| Convert Suricata Report | Converts Suricata JSON logs to HTML.                                        |
| OWASP ZAP Scan          | Performs penetration testing with OWASP ZAP.                                |
| Combine Reports         | Generates consolidated CVSS and HTML reports.                               |

---

## ⚙️ Requirements

- Jenkins with Pipeline plugin
- Docker installed and accessible
- Security tools installed:
  - [Trivy](https://github.com/aquasecurity/trivy)
  - [Snyk](https://snyk.io/)
  - [Grype](https://github.com/anchore/grype)
  - [Cosign](https://github.com/sigstore/cosign)
  - [Suricata](https://suricata.io/)
  - [OWASP ZAP](https://www.zaproxy.org/)
- Python (for report conversion scripts)

---

## 📊 Reports Generated

- `trivy_report.json` / `trivy_report.html`
- `snyk_source_report.json` / `snyk_source_report.html`
- `snyk_container_report.json` / `snyk_container_report.html`
- `grype_report.json` / `grype_report.txt`
- `zap_full_report.json` / `zap_full_report.html`
- `eve.json` (Suricata raw logs)
- `eve_report.html` (Suricata converted report)
- `combined_report.html` (Consolidated CVSS-based report)

---

## 🚀 Usage

1. Clone this repository.
2. Configure Jenkins with required credentials:
   - **Docker Hub** (`Docker`)
   - **Snyk Token** (`SnykToken_Text`)
   - **Cosign Private Key** (`CosignPrivateKey`)
   - **Cosign Password** (`CosignPassword`)
3. Run the pipeline in Jenkins.
4. View generated reports in Jenkins under **Security Reports**.

---

## 📌 Notes

- Works on both **Unix** and **Windows** agents.
- Reports are stored in the `reports/` directory.
- The pipeline ensures builds are marked **UNSTABLE** if critical vulnerabilities are found (optional logic included).

---

## 🖼️ Example Jenkins Report Dashboard

After pipeline execution, Jenkins will display a **Security Reports** tab with:
- Trivy, Snyk, Grype results
- Suricata monitoring logs
- OWASP ZAP penetration test results
- Combined CVSS-based vulnerability summary

---

## 📜 License

This project is licensed under the MIT License.
