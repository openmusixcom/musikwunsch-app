#!/usr/bin/env python3
"""
Automated VPS Redeployment Script
Handles full deployment to Hostinger VPS
"""

import subprocess
import sys
import os

# VPS Configuration
VPS_HOST = "187.124.20.215"
VPS_USER = "root"
VPS_PASSWORD = "Extra01#1234"
DEPLOY_DIR = "/var/www/musikwunsch-app-docker"
REPO_URL = "https://github.com/cwoll/DJapp.git"

def run_ssh_command(cmd, description):
    """Execute command on VPS via SSH"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")

    # Create SSH command using sshpass (requires sshpass to be installed)
    full_cmd = f'sshpass -p "{VPS_PASSWORD}" ssh {VPS_USER}@{VPS_HOST} "{cmd}"'

    try:
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=120)

        if result.stdout:
            print(result.stdout)

        if result.returncode != 0:
            if result.stderr:
                print(f"❌ Error: {result.stderr}")
            return False

        print(f"✅ {description} - Success")
        return True

    except subprocess.TimeoutExpired:
        print(f"❌ Command timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main deployment flow"""

    print("""
    ╔════════════════════════════════════════╗
    ║ 🚀 MUSIKWUNSCH VPS REDEPLOYMENT SCRIPT ║
    ╚════════════════════════════════════════╝
    """)

    # Check if we have sshpass installed
    try:
        subprocess.run(["sshpass", "-V"], capture_output=True, timeout=5)
    except FileNotFoundError:
        print("⚠️  sshpass not found. Installing...")
        os.system("pip install pexpect")

    # Deployment steps
    steps = [
        ("mkdir -p /var/www && cd /var/www && git clone https://github.com/cwoll/DJapp.git musikwunsch-app-docker 2>/dev/null || true",
         "Cloning repository"),

        (f"cd {DEPLOY_DIR} && git fetch origin main && git reset --hard origin/main",
         "Fetching latest code"),

        ("command -v docker &> /dev/null || (curl -fsSL https://get.docker.com -o get-docker.sh && bash get-docker.sh && rm get-docker.sh)",
         "Installing Docker"),

        ("command -v docker-compose &> /dev/null || (curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose)",
         "Installing Docker Compose"),

        (f"cd {DEPLOY_DIR} && docker-compose down",
         "Stopping old containers"),

        (f"cd {DEPLOY_DIR} && docker-compose build --no-cache",
         "Building Docker images (this may take 5-10 minutes)"),

        (f"cd {DEPLOY_DIR} && docker-compose up -d",
         "Starting containers"),

        ("sleep 15",
         "Waiting for services to be ready"),

        (f"cd {DEPLOY_DIR} && docker-compose exec -T musikwunsch-api npm run migrate",
         "Running database migrations"),
    ]

    # Execute all steps
    failed_steps = []
    for cmd, desc in steps:
        if not run_ssh_command(cmd, desc):
            failed_steps.append(desc)
            if "critical" in desc.lower() or "migrate" in desc.lower():
                print(f"\n❌ Critical step failed. Stopping deployment.")
                break

    # Summary
    print(f"\n{'='*60}")
    print("📊 DEPLOYMENT SUMMARY")
    print(f"{'='*60}")

    if not failed_steps:
        print("✅ All steps completed successfully!\n")

        # Test the deployment
        print("🧪 Testing deployment...")
        test_cmd = f'sshpass -p "{VPS_PASSWORD}" ssh {VPS_USER}@{VPS_HOST} "curl -s http://localhost:3000/api/health"'

        try:
            result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True, timeout=10)
            if "timestamp" in result.stdout:
                print("✅ API Health Check: PASSED\n")
            else:
                print("⚠️  API Health Check: Waiting for backend to be ready\n")
        except:
            print("⚠️  API Health Check: Could not reach backend yet\n")

        print("🎉 Deployment Complete!\n")
        print("Access the application at:")
        print("  - Frontend: http://87.106.215.187.nip.io")
        print("  - Guest App: http://87.106.215.187.nip.io/guest")
        print("  - API: http://87.106.215.187.nip.io/api\n")
        print("Test Login with:")
        print('  curl -X POST http://87.106.215.187.nip.io/api/auth/login \\')
        print('    -H "Content-Type: application/json" \\')
        print('    -d \'{"email":"admin@test.local","password":"testpass123"}\'')

        return True
    else:
        print(f"\n❌ {len(failed_steps)} step(s) failed:")
        for step in failed_steps:
            print(f"  - {step}")

        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
