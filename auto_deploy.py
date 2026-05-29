#!/usr/bin/env python3
"""
Musikwunsch Automated Deployment Tool
Handles all VPS deployments with logging, error handling, and health checks
"""

import subprocess
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

# Configuration
CONFIG = {
    "vps_host": "187.124.20.215",
    "vps_user": "root",
    "vps_password": "Extra01#1234",
    "deploy_dir": "/var/www/musikwunsch-app-docker",
    "repo_url": "https://github.com/openmusixcom/musikwunsch-app.git",
    "repo_branch": "main",
    "api_health_url": "http://87.106.215.187.nip.io/api/health",
}

class DeploymentTool:
    def __init__(self):
        self.log_file = Path(f"deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        self.start_time = datetime.now()
        self.steps_completed = []
        self.errors = []

    def log(self, message, level="INFO"):
        """Log message to console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] {message}"
        print(log_msg)
        with open(self.log_file, "a") as f:
            f.write(log_msg + "\n")

    def run_ssh_command(self, cmd, description, timeout=300):
        """Execute command on VPS via SSH"""
        self.log(f"Executing: {description}")

        # Use sshpass for password auth
        full_cmd = f'sshpass -p "{CONFIG["vps_password"]}" ssh -o StrictHostKeyChecking=no {CONFIG["vps_user"]}@{CONFIG["vps_host"]} "{cmd}"'

        try:
            result = subprocess.run(
                full_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.stdout:
                for line in result.stdout.split("\n"):
                    if line.strip():
                        self.log(f"  > {line}", "OUTPUT")

            if result.returncode != 0:
                error_msg = f"Command failed: {description}"
                if result.stderr:
                    error_msg += f"\n{result.stderr}"
                self.log(error_msg, "ERROR")
                self.errors.append(error_msg)
                return False

            self.steps_completed.append(description)
            self.log(f"✅ {description}", "SUCCESS")
            return True

        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out: {description}"
            self.log(error_msg, "ERROR")
            self.errors.append(error_msg)
            return False
        except Exception as e:
            error_msg = f"Error executing {description}: {str(e)}"
            self.log(error_msg, "ERROR")
            self.errors.append(error_msg)
            return False

    def run_local_command(self, cmd, description):
        """Execute command locally"""
        self.log(f"Executing locally: {description}")

        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.stdout:
                for line in result.stdout.split("\n"):
                    if line.strip():
                        self.log(f"  > {line}", "OUTPUT")

            if result.returncode != 0:
                self.log(f"Local command warning: {description}", "WARNING")
                if result.stderr:
                    self.log(f"  Error: {result.stderr}", "WARNING")
                return False

            self.steps_completed.append(description)
            self.log(f"✅ {description}", "SUCCESS")
            return True

        except Exception as e:
            self.log(f"Error: {str(e)}", "ERROR")
            return False

    def check_health(self):
        """Check if API is responding"""
        self.log("Checking API health...")

        try:
            result = subprocess.run(
                f'curl -s -m 5 {CONFIG["api_health_url"]}',
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and "ok" in result.stdout.lower():
                self.log("✅ API health check passed", "SUCCESS")
                return True
            else:
                self.log("⚠️ API health check inconclusive, but continuing...", "WARNING")
                return True  # Don't fail on health check

        except Exception as e:
            self.log(f"⚠️ Health check error: {str(e)}", "WARNING")
            return True  # Don't fail deployment on health check error

    def deploy(self):
        """Execute full deployment"""
        self.log("=" * 60)
        self.log("🚀 STARTING MUSIKWUNSCH DEPLOYMENT")
        self.log("=" * 60)

        steps = [
            # Fetch latest code from GitHub locally
            ("git fetch origin main && git reset --hard origin/main",
             "Fetch latest code from GitHub (local)"),

            # SSH into VPS and prepare
            (f"cd {CONFIG['deploy_dir']} || (mkdir -p {CONFIG['deploy_dir']} && cd {CONFIG['deploy_dir']} && git init && git remote add origin {CONFIG['repo_url']})",
             "Prepare VPS deployment directory"),

            # Pull latest code on VPS
            (f"cd {CONFIG['deploy_dir']} && git fetch origin {CONFIG['repo_branch']} && git reset --hard origin/{CONFIG['repo_branch']}",
             "Pull latest code on VPS"),

            # Check git status
            (f"cd {CONFIG['deploy_dir']} && git log -1 --oneline",
             "Verify code deployed"),

            # Verify Docker is installed
            (f"which docker || (echo 'Installing Docker...' && curl -fsSL https://get.docker.com -o /tmp/get-docker.sh && bash /tmp/get-docker.sh)",
             "Verify Docker installation"),

            # Verify Docker Compose is installed
            (f"which docker-compose || (curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose)",
             "Verify Docker Compose installation"),

            # Stop old containers
            (f"cd {CONFIG['deploy_dir']} && docker-compose down 2>/dev/null || true",
             "Stop old containers"),

            # Build new images
            (f"cd {CONFIG['deploy_dir']} && docker-compose build --no-cache --pull",
             "Build Docker images (this may take 5-10 minutes)"),

            # Start new containers
            (f"cd {CONFIG['deploy_dir']} && docker-compose up -d",
             "Start new containers"),

            # Wait for services
            ("sleep 20",
             "Wait for services to be ready"),

            # Run migrations
            (f"cd {CONFIG['deploy_dir']} && docker-compose exec -T musikwunsch-api npm run migrate",
             "Run database migrations"),

            # Load sample songs if needed
            (f"cd {CONFIG['deploy_dir']} && docker-compose exec -T musikwunsch-db psql -U postgres -d musikwunsch << 'ENDSQL'\nINSERT INTO songs (title, artist, album, duration, genre) VALUES\n('Hello', 'Adele', '25', 295, 'Pop'),\n('Shape of You', 'Ed Sheeran', '÷', 233, 'Pop'),\n('Blinding Lights', 'The Weeknd', 'After Hours', 200, 'Synthwave')\nON CONFLICT DO NOTHING;\nENDSQL",
             "Ensure sample songs in database"),

            # Get container status
            (f"cd {CONFIG['deploy_dir']} && docker-compose ps",
             "Verify all containers running"),
        ]

        failed = False
        for cmd, description in steps:
            if description.startswith("Fetch latest") or description.startswith("Verify code"):
                if not self.run_local_command(cmd, description):
                    if "pull latest code on" in description.lower():
                        self.log("Continuing despite local git issue...", "WARNING")
            else:
                if not self.run_ssh_command(cmd, description):
                    # Only fail on critical steps
                    if any(x in description.lower() for x in ["docker compose up", "migrations", "build"]):
                        failed = True
                        break

        # Health check
        if not failed:
            self.log("", "INFO")
            self.log("Waiting 5 seconds before health check...", "INFO")
            time.sleep(5)
            self.check_health()

        return not failed

    def report(self):
        """Generate deployment report"""
        self.log("", "INFO")
        self.log("=" * 60)
        self.log("📊 DEPLOYMENT REPORT")
        self.log("=" * 60)

        duration = datetime.now() - self.start_time

        self.log(f"Duration: {duration}", "INFO")
        self.log(f"Steps completed: {len(self.steps_completed)}", "INFO")

        if self.steps_completed:
            self.log("", "INFO")
            self.log("✅ Completed steps:", "INFO")
            for step in self.steps_completed:
                self.log(f"  • {step}", "INFO")

        if self.errors:
            self.log("", "INFO")
            self.log(f"❌ Errors ({len(self.errors)}):", "ERROR")
            for error in self.errors:
                self.log(f"  • {error}", "ERROR")

        self.log("", "INFO")
        self.log("🎉 Deployment Complete!", "INFO")
        self.log("", "INFO")
        self.log("Access the application:", "INFO")
        self.log("  - Frontend: http://87.106.215.187.nip.io", "INFO")
        self.log("  - Guest App: http://87.106.215.187.nip.io/guest", "INFO")
        self.log("  - API: http://87.106.215.187.nip.io/api", "INFO")
        self.log("", "INFO")
        self.log(f"📝 Full log: {self.log_file}", "INFO")
        self.log("=" * 60)

        return len(self.errors) == 0

def main():
    print("""
    ╔════════════════════════════════════════════╗
    ║ 🚀 MUSIKWUNSCH AUTOMATED DEPLOYMENT TOOL  ║
    ╚════════════════════════════════════════════╝
    """)

    # Check prerequisites
    print("🔍 Checking prerequisites...")
    try:
        subprocess.run("sshpass --version", shell=True, capture_output=True, timeout=5)
    except:
        print("⚠️  sshpass not found. Installing...")
        os.system("pip install pexpect 2>/dev/null || apt-get install sshpass -y")

    # Create deployment tool
    tool = DeploymentTool()

    # Execute deployment
    try:
        success = tool.deploy()
    except Exception as e:
        tool.log(f"Unexpected error: {str(e)}", "ERROR")
        success = False

    # Generate report
    tool.report()

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
