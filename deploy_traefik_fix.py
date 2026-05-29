#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deploy Traefik routing fix to Musikwunsch VPS
Pulls latest code and restarts containers with new configuration
"""

import subprocess
import sys
import time
from datetime import datetime

CONFIG = {
    "vps_host": "87.106.215.187",
    "vps_user": "root",
    "deploy_dir": "/var/www/musikwunsch-app-docker",
}

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}")

def run_cmd(cmd, description):
    log(f"Executing: {description}")
    log(f"Command: {cmd}", "DEBUG")

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)

        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                log(f"  > {line}", "OUTPUT")

        if result.returncode != 0:
            log(f"ERROR: {description} failed", "ERROR")
            if result.stderr:
                log(f"Details: {result.stderr}", "ERROR")
            return False

        log(f"OK: {description}", "SUCCESS")
        return True
    except Exception as e:
        log(f"Exception: {str(e)}", "ERROR")
        return False

def main():
    print("""
    ╔══════════════════════════════════════════╗
    ║ MUSIKWUNSCH TRAEFIK ROUTING FIX DEPLOY   ║
    ╚══════════════════════════════════════════╝
    """)

    print("NOTE: This script requires SSH access to the VPS.")
    print("If you don't have sshpass installed, install it first:")
    print("  Windows: Download from https://github.com/alebcay/sshpass")
    print("  Linux:   sudo apt-get install sshpass")
    print("  macOS:   brew install esolitos/ipa/sshpass")
    print()

    # Check if we can SSH
    test_cmd = f'sshpass -p "Extra01#1234" ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@{CONFIG["vps_host"]} "echo OK" 2>&1'
    log("Testing SSH connectivity...", "INFO")

    result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        log("SSH connection failed. Cannot proceed.", "ERROR")
        log("Ensure sshpass is installed and SSH credentials are correct.", "ERROR")
        return 1

    log("SSH connection OK", "SUCCESS")

    # Deployment steps
    steps = [
        (
            f'sshpass -p "Extra01#1234" ssh -o StrictHostKeyChecking=no root@{CONFIG["vps_host"]} "cd {CONFIG["deploy_dir"]} && git fetch origin main && git reset --hard origin/main && git log -1 --oneline"',
            "Pull latest code from GitHub",
        ),
        (
            f'sshpass -p "Extra01#1234" ssh -o StrictHostKeyChecking=no root@{CONFIG["vps_host"]} "cd {CONFIG["deploy_dir"]} && docker-compose down"',
            "Stop containers",
        ),
        (
            f'sshpass -p "Extra01#1234" ssh -o StrictHostKeyChecking=no root@{CONFIG["vps_host"]} "cd {CONFIG["deploy_dir"]} && docker-compose up -d"',
            "Start containers with new Traefik configuration",
        ),
        (
            f'sshpass -p "Extra01#1234" ssh -o StrictHostKeyChecking=no root@{CONFIG["vps_host"]} "sleep 15 && cd {CONFIG["deploy_dir"]} && docker-compose ps"',
            "Wait for services and verify container status",
        ),
    ]

    log("Starting deployment...", "INFO")
    log("=" * 70, "INFO")

    for cmd, description in steps:
        if not run_cmd(cmd, description):
            log("Deployment failed at critical step", "ERROR")
            return 1
        time.sleep(2)

    log("=" * 70, "INFO")
    log("Deployment complete!", "SUCCESS")

    print("\n" + "=" * 70)
    print("NEXT STEPS - Test the new configuration:")
    print("=" * 70)
    print()
    print("Test HTTP → HTTPS redirect:")
    print('  curl -i http://musikwunsch.87-106-215-187.nip.io/api/health')
    print()
    print("Test HTTPS with Let\'s Encrypt certificate:")
    print('  curl -i https://musikwunsch.87-106-215-187.nip.io/api/health')
    print()
    print("Test login endpoint:")
    print('  curl -X POST -H "Content-Type: application/json" \\')
    print('    -d \'{"email":"admin@test.local","password":"testpass123"}\' \\')
    print('    https://musikwunsch.87-106-215-187.nip.io/api/auth/login')
    print()
    print("=" * 70)

    return 0

if __name__ == "__main__":
    sys.exit(main())
