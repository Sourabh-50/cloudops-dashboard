# CloudOps Dashboard 
**An End-to-End DevOps Deployment Pipeline Project**  
*Developed & Deployed by [Sourabh](https://github.com/Sourabh-50)*

This repository contains a professional, high-fidelity cloud operations and infrastructure monitoring dashboard built to demonstrate production-level DevOps engineering practices. The project showcases containerization, environment variable configurations, automated GitOps CI/CD pipelines, and cloud hosting on AWS EC2.

---

## Key Features

*   **Glassmorphic Dark-Mode UI**: Built with modern CSS using glassmorphic cards, glowing element rings, and smooth rotating animation gauges.
*   **Infrastructure Telemetry**: Automatically queries the host operating system to display server hostname, internal IP, OS type (e.g., Windows/Ubuntu), and dynamic resource loads (CPU and RAM).
*   **Container Status Console**: A visual monitor displaying running containers (like reverse proxies, database, cache) simulating a microservice stack.
*   **Active Uptime & Liveness Probes**: Exposes production-ready `/health` and `/api/info` endpoints returning clean JSON payloads for load-balancer health checks.
*   **Twelve-Factor Configuration**: Fully configured to read settings from the host environment (`ENVIRONMENT`, `APP_VERSION`, `BUILD_NUMBER`, `CLOUD_PROVIDER`).
*   **Docker Containerization**: Custom Docker recipe built using a lightweight `python:3.11-slim` base image and configured to run securely as a non-privileged `appuser`.
*   **Automated CI/CD**: Built with GitHub Actions to automate code checks, Docker builds, caching, and registry pushes.

---

##  Project Structure

```text
cloudops-dashboard/
├── .github/
│   └── workflows/
│       └── deploy.yml       # GitHub Actions CI/CD pipeline
├── static/
│   └── style.css            # Custom CSS (Glassmorphism & animations)
├── templates/
│   └── index.html           # Dashboard layout
├── .dockerignore            # Excluded files from Docker build context
├── app.py                   # Flask server application
├── Dockerfile               # Security-focused container recipe
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

---

##  Tech Stack & Concepts

*   **Application**: Python 3.13, Flask, Gunicorn
*   **Styling**: HTML5, Vanilla CSS3 (CSS Grid, Flexbox, Custom Properties, Keyframe Animations)
*   **Containerization**: Docker
*   **CI/CD Pipeline**: GitHub Actions
*   **Cloud Infrastructure**: AWS EC2 (Ubuntu 24.04 LTS), Security Groups
*   **Security Best Practices**: Non-root container execution, Git ignored environments, secure environment variables

---

##  Step-by-Step Setup Guide

### 1. Local Run (Development Environment)

1.  Clone the repository and enter the directory:
    ```bash
    git clone https://github.com/Sourabh-50/cloudops-dashboard.git
    cd cloudops-dashboard
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  Run the application:
    ```bash
    python app.py
    ```

4.  Access the endpoints:
    *   Dashboard: [http://localhost:5000](http://localhost:5000)
    *   Health probe: [http://localhost:5000/health](http://localhost:5000/health)
    *   API metadata: [http://localhost:5000/api/info](http://localhost:5000/api/info)

---

### 2. Override Configurations (Environment Variables)

Test configuration management locally by running the application with custom environment parameters:

*   **On Windows (PowerShell):**
    ```powershell
    $env:ENVIRONMENT="Staging"
    $env:APP_VERSION="1.2.0"
    $env:BUILD_NUMBER="085"
    $env:CLOUD_PROVIDER="AWS EC2"
    python app.py
    ```
*   **On Linux / macOS:**
    ```bash
    ENVIRONMENT="Production" APP_VERSION="1.2.0" BUILD_NUMBER="085" CLOUD_PROVIDER="AWS EC2" python app.py
    ```

---

### 3. Build & Run with Docker

1.  **Build the Docker image**:
    ```bash
    docker build -t cloudops-dashboard .
    ```

2.  **Run the container** (running in the background on port 5000):
    ```bash
    docker run -d -p 5000:5000 --name cloudops-app cloudops-dashboard
    ```

3.  **Run with production environment configuration**:
    ```bash
    docker run -d -p 5000:5000 --name cloudops-prod -e ENVIRONMENT="Production" -e CLOUD_PROVIDER="AWS EC2" -e BUILD_NUMBER="109" cloudops-dashboard
    ```

---

### 4. Git & GitHub Actions CI/CD Pipeline

The `.github/workflows/deploy.yml` pipeline compiles and pushes the Docker container automatically to Docker Hub on every commit to `main`.

**GitHub Actions Setup**:
1.  Add two secrets to your GitHub Repository Settings (`Settings -> Secrets and variables -> Actions`):
    *   `DOCKER_USERNAME`: Your Docker Hub username.
    *   `DOCKER_PASSWORD`: Your Docker Hub Access Token.
2.  Push code to trigger the build:
    ```bash
    git add .
    git commit -m "feat: setup automation"
    git push origin main
    ```

---

### 5. Production Cloud Deployment (AWS EC2)

1.  **Launch Instance**: Spin up an Ubuntu 24.04 LTS instance (t2.micro - Free Tier).
2.  **Open Firewall Ports**: Configure the Security Group to allow SSH (port 22) and HTTP (port 80).
3.  **Install Docker on EC2**:
    ```bash
    sudo apt update
    sudo apt install docker.io -y
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker ubuntu
    ```
    *(Note: Disconnect and reconnect via SSH to refresh groups)*
4.  **Deploy Container**: Pull your image and serve it on port `80` (HTTP):
    ```bash
    docker pull YOUR_DOCKER_USERNAME/cloudops-dashboard:latest
    docker run -d -p 80:5000 --name webapp -e ENVIRONMENT="Production" -e CLOUD_PROVIDER="AWS EC2 (t2.micro)" YOUR_DOCKER_USERNAME/cloudops-dashboard:latest
    ```
5.  **Verify Webpage**: Open a browser and visit your EC2 Public IP address (`http://your-ec2-public-ip`).

---

## 📈 Telemetry, Monitoring & Infrastructure

This project is configured with a high-fidelity monitoring and GitOps delivery stack:

### 1. Real-Time Resource Telemetry
*   **AWS CloudWatch Agent**: Installed via snap on the EC2 host. The configuration script publishes CPU, memory (`mem_used_percent`), and disk utilization (`disk_used_percent`) metrics back to the `CWAgent` namespace.
*   **Dynamic Telemetry Polling**: The Flask dashboard backend queries CloudWatch API statistics using `boto3` (automatically resolving EC2 Instance IDs via AWS Metadata endpoints).
*   **Fallback Agent**: In local/unconfigured environments, the app falls back to local machine resource monitoring using `psutil` and displays status flags directly in the UI.

### 2. AWS CloudWatch Snap Installation
Run the automated installation script inside your EC2 terminal:
```bash
chmod +x infrastructure/install_cloudwatch.sh
sudo ./infrastructure/install_cloudwatch.sh
```

### 3. CI/CD Redeployment Trigger
*   Clicking **Trigger Real CI/CD Deployment** in the web dashboard makes an authenticated API call to the GitHub Actions REST API, triggering a manual `workflow_dispatch` run of the CI/CD pipeline.
*   The pipeline builds and pushes the updated Docker container, then connects via secure SSH keys to the EC2 host to perform image pulls and container recycling.

