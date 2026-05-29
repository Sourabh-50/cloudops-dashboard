#!/usr/bin/env bash
set -e

echo "==========================================="
echo " Installing AWS CloudWatch Agent via Snap  "
echo "==========================================="

# Install the agent via snap as requested
sudo snap install amazon-cloudwatch-agent

# Create the configuration directories
sudo mkdir -p /opt/aws/amazon-cloudwatch-agent/etc/

# Copy the configuration file to the expected directory
SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
sudo cp "${SCRIPT_DIR}/amazon-cloudwatch-agent.json" /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json

# Fetch configuration and start the agent
echo "Starting CloudWatch Agent..."
sudo /snap/amazon-cloudwatch-agent/current/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json \
  -s

echo "CloudWatch Agent setup complete and service started!"
