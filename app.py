from flask import Flask, render_template, jsonify
import socket
import os
import datetime
import platform
import random

app = Flask(__name__)

def get_system_stats():
    # Provide system information using standard library
    stats = {
        "os": f"{platform.system()} {platform.release()}",
        "cpu_usage": f"{random.randint(15, 45)}%",
        "memory_usage": f"{random.randint(35, 60)}%",
        "uptime": "5d 14h 32m"
    }
    return stats

def get_mock_containers():
    # Return mock container statuses for DevOps dashboard demonstration
    return [
        {"name": "nginx-reverse-proxy", "status": "running", "port": "80:80", "uptime": "5 days"},
        {"name": "cloudops-dashboard", "status": "running", "port": "5000:5000", "uptime": "3 hours"},
        {"name": "postgres-db", "status": "running", "port": "5432:5432", "uptime": "5 days"},
        {"name": "redis-cache", "status": "running", "port": "6379:6379", "uptime": "5 days"}
    ]

@app.route("/")
def home():
    stats = get_system_stats()
    containers = get_mock_containers()
    
    # Secure environment variables list for display (only safe ones)
    safe_env = {
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "Development"),
        "APP_VERSION": os.getenv("APP_VERSION", "1.0.0"),
        "BUILD_NUMBER": os.getenv("BUILD_NUMBER", "001"),
        "CLOUD_PROVIDER": os.getenv("CLOUD_PROVIDER", "Localhost"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO")
    }
    
    return render_template(
        "index.html",
        hostname=socket.gethostname(),
        ip_address=socket.gethostbyname(socket.gethostname()),
        environment=safe_env["ENVIRONMENT"],
        version=safe_env["APP_VERSION"],
        build=safe_env["BUILD_NUMBER"],
        cloud_provider=safe_env["CLOUD_PROVIDER"],
        deployed=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        stats=stats,
        containers=containers,
        safe_env=safe_env
    )

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "CloudOps Dashboard",
        "timestamp": datetime.datetime.now().isoformat(),
        "database": "connected"
    })

@app.route("/api/info")
def info():
    return jsonify({
        "hostname": socket.gethostname(),
        "ip_address": socket.gethostbyname(socket.gethostname()),
        "environment": os.getenv("ENVIRONMENT", "Development"),
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "build": os.getenv("BUILD_NUMBER", "001"),
        "cloud_provider": os.getenv("CLOUD_PROVIDER", "Localhost")
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)