# Secure CI/CD Pipeline with Jenkins, Docker, Trivy, Cosign & OWASP ZAP

This repository demonstrates a **Jenkins pipeline** that builds, scans, signs, and runs a Dockerized application with integrated security checks.  
A simple **React demo project** is used as the application under test.

---

## 🚀 Pipeline Overview

The Jenkins pipeline (`Jenkinsfile`) automates the following stages:

1. **Build Docker Image**
   - Builds the application image:  
     `docker build -t sreyassharma/signed_images_jenkins:1.0.1 .`

2. **Cleanup Docker**
   - Removes unused images to save space:  
     `docker image prune -f`

3. **Trivy Scan**
   - Runs [Trivy](https://aquasecurity.github.io/trivy/) vulnerability scans:
     - JSON report → `reports/trivy_report.json`
     - HTML report → `reports/trivy_report.html`
   - Scans for **MEDIUM, HIGH, CRITICAL** severity issues.

4. **Push Docker Image**
   - Authenticates with Docker Hub using Jenkins credentials.
   - Pushes the image:  
     `docker push sreyassharma/signed_images_jenkins:1.0.1`

5. **Sign Docker Image**
   - Uses [Cosign](https://github.com/sigstore/cosign) to sign the image.
   - Credentials (`CosignPrivateKey`, `CosignPassword`) are securely injected via Jenkins.

6. **Create Network**
   - Creates a Docker network (`network1`) if it doesn’t exist.

7. **Run App Container**
   - Runs the demo React app container on port `8123`.

8. **OWASP ZAP Scan**
   - Executes [OWASP ZAP](https://www.zaproxy.org/) baseline scan against the running app.
   - Outputs:
     - HTML report → `reports/zap_report.html`
     - JSON report → `reports/zap_report.json`

9. **Post Actions**
   - Stops containers and removes the network.
   - Publishes HTML reports in Jenkins under **Security Reports**.

---

## 📂 Reports Generated

- `reports/trivy_report.json`  
- `reports/trivy_report.html`  
- `reports/zap_report.json`  
- `reports/zap_report.html`  

These are published in Jenkins using the `publishHTML` plugin.

---

## 🛠️ Requirements

- Jenkins with Docker installed
- Plugins:
  - **Pipeline**
  - **Publish HTML Reports**
- Tools installed on Jenkins agents:
  - Docker
  - Trivy
  - Cosign
- Credentials configured in Jenkins:
  - `Docker` → Docker Hub username/password
  - `CosignPrivateKey` → Private key string
  - `CosignPassword` → Password for the key

---

## 🧪 Demo React Project

A simple React project is used to test the pipeline.  
You can replace it with any application — just ensure the `Dockerfile` is present in the repo.

---

## 🔒 Security Highlights

- **Trivy** → Container vulnerability scanning  
- **Cosign** → Image signing for supply chain security  
- **OWASP ZAP** → Automated web application security testing  

This pipeline integrates **DevSecOps practices** directly into CI/CD.

---

## ▶️ Usage

1. Clone this repository.
2. Configure Jenkins with required credentials.
3. Run the pipeline.
4. View results in Jenkins under **Security Reports**.

---

## 📌 Notes

- The pipeline supports both **Unix** and **Windows** agents.
- Reports are always generated, even if scans fail (pipeline continues with `|| true` / `exit /b 0`).
- Image signing uses a temporary `cosign.key` file which is deleted after use.

---

## 📖 License

This project is for demonstration purposes.  
Feel free to adapt and extend it for your own CI/CD workflows.
