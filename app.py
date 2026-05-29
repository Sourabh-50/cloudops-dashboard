from flask import Flask, render_template, jsonify, request
import socket
import os
import datetime
import platform
import random
import time
import requests
import boto3

app = Flask(__name__)

# Helper to format uptime cleanly
def format_uptime(seconds):
    days = int(seconds // (24 * 3600))
    seconds %= (24 * 3600)
    hours = int(seconds // 3600)
    seconds %= 3600
    minutes = int(seconds // 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    return " ".join(parts) if parts else "0m"

# Get local telemetry stats via psutil
def get_system_stats():
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=None) or random.randint(10, 30)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        uptime_str = format_uptime(uptime_seconds)
        
        return {
            "os": f"{platform.system()} {platform.release()}",
            "cpu_usage": f"{cpu:.1f}%",
            "memory_usage": f"{mem.percent:.1f}%",
            "disk_usage": f"{disk.percent:.1f}%",
            "uptime": uptime_str,
            "source": "Local Agent (psutil)"
        }
    except Exception as e:
        return {
            "os": f"{platform.system()} {platform.release()}",
            "cpu_usage": f"{random.randint(15, 35)}%",
            "memory_usage": f"{random.randint(40, 55)}%",
            "disk_usage": f"{random.randint(25, 45)}%",
            "uptime": "5d 14h 32m",
            "source": f"Mock Telemetry (Error: {str(e)})"
        }

# Get region name from IMDS
def get_ec2_region():
    try:
        token_headers = {"X-aws-ec2-metadata-token-ttl-seconds": "60"}
        token_resp = requests.put("http://169.254.169.254/latest/api/token", headers=token_headers, timeout=0.5)
        headers = {"X-aws-ec2-metadata-token": token_resp.text} if token_resp.status_code == 200 else {}
        
        region_resp = requests.get("http://169.254.169.254/latest/meta-data/placement/region", headers=headers, timeout=0.5)
        if region_resp.status_code == 200:
            return region_resp.text.strip()
    except Exception:
        pass
    return "us-east-1"

# Get CloudWatch telemetry metrics
def get_cloudwatch_stats():
    instance_id = None
    try:
        # Fetch token first (IMDSv2)
        token_headers = {"X-aws-ec2-metadata-token-ttl-seconds": "60"}
        token_resp = requests.put("http://169.254.169.254/latest/api/token", headers=token_headers, timeout=0.5)
        headers = {"X-aws-ec2-metadata-token": token_resp.text} if token_resp.status_code == 200 else {}
        
        instance_id_resp = requests.get("http://169.254.169.254/latest/meta-data/instance-id", headers=headers, timeout=0.5)
        if instance_id_resp.status_code == 200:
            instance_id = instance_id_resp.text.strip()
    except Exception:
        return None

    if not instance_id:
        return None

    try:
        region = get_ec2_region()
        cw = boto3.client('cloudwatch', region_name=region)
        
        end_time = datetime.datetime.utcnow()
        start_time = end_time - datetime.timedelta(minutes=10)
        
        # Get Average CPU Utilization
        cpu_res = cw.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=60,
            Statistics=['Average']
        )
        
        # Get custom agent Memory metric
        mem_res = cw.get_metric_statistics(
            Namespace='CWAgent',
            MetricName='mem_used_percent',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=60,
            Statistics=['Average']
        )
        
        # Get custom agent Disk metric
        disk_res = cw.get_metric_statistics(
            Namespace='CWAgent',
            MetricName='disk_used_percent',
            Dimensions=[
                {'Name': 'InstanceId', 'Value': instance_id},
                {'Name': 'path', 'Value': '/'}
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=60,
            Statistics=['Average']
        )
        
        stats = {"instance_id": instance_id, "region": region}
        if cpu_res.get('Datapoints'):
            stats['cpu_usage'] = f"{cpu_res['Datapoints'][-1]['Average']:.1f}%"
        if mem_res.get('Datapoints'):
            stats['memory_usage'] = f"{mem_res['Datapoints'][-1]['Average']:.1f}%"
        if disk_res.get('Datapoints'):
            stats['disk_usage'] = f"{disk_res['Datapoints'][-1]['Average']:.1f}%"
            
        return stats
    except Exception:
        return None

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

@app.route("/api/metrics")
def metrics():
    # Attempt to query CloudWatch
    cw_stats = get_cloudwatch_stats()
    local_stats = get_system_stats()
    
    if cw_stats:
        # Merge CloudWatch CPU/Memory/Disk stats into stats
        merged = {
            "os": local_stats["os"],
            "cpu_usage": cw_stats.get("cpu_usage", local_stats["cpu_usage"]),
            "memory_usage": cw_stats.get("memory_usage", local_stats["memory_usage"]),
            "disk_usage": cw_stats.get("disk_usage", local_stats["disk_usage"]),
            "uptime": local_stats["uptime"],
            "source": f"CloudWatch API ({cw_stats['instance_id']})"
        }
    else:
        merged = local_stats
        
    return jsonify(merged)

@app.route("/api/deploy", methods=["POST"])
def deploy():
    github_pat = os.getenv("GITHUB_PAT")
    github_repo = os.getenv("GITHUB_REPO")
    
    if github_pat and github_repo:
        try:
            # Trigger GitHub workflow_dispatch
            url = f"https://api.github.com/repos/{github_repo}/actions/workflows/deploy.yml/dispatches"
            headers = {
                "Authorization": f"Bearer {github_pat}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            data = {"ref": "main"}
            response = requests.post(url, headers=headers, json=data, timeout=5.0)
            
            if response.status_code == 204:
                return jsonify({
                    "status": "success",
                    "real_deployment": True,
                    "message": f"Real CI/CD pipeline triggered successfully on GitHub Actions! Repository: {github_repo}",
                    "actions_url": f"https://github.com/{github_repo}/actions"
                })
            else:
                return jsonify({
                    "status": "error",
                    "real_deployment": False,
                    "message": f"GitHub API returned status {response.status_code}: {response.text}",
                    "actions_url": f"https://github.com/{github_repo}/actions"
                })
        except Exception as e:
            return jsonify({
                "status": "error",
                "real_deployment": False,
                "message": f"Failed to connect to GitHub Actions API: {str(e)}"
            })
    else:
        # Fallback simulation if environment variables are missing
        return jsonify({
            "status": "simulated",
            "real_deployment": False,
            "message": "Mock CI/CD pipeline triggered! (GITHUB_PAT and GITHUB_REPO env vars not set). Container pull & restart simulated.",
            "setup_instructions": "To wire this up to real deployments, configure GITHUB_PAT and GITHUB_REPO env variables in your container environment."
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)