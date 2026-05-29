#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Hostinger Git Repository - Automates STEP 1 of deployment
Creates bare git repository on Hostinger server and configures local remote
"""

import paramiko
import subprocess
import sys
import io
import os

# Fix encoding for Windows
if os.name == 'nt':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
HOST = "187.124.20.215"
PORT = 22
USERNAME = "root"
PASSWORD = "Extra01#1234"
GIT_REPO_PATH = "/var/repos/musikwunsch.git"

def setup_remote_git():
    """Create bare git repository on Hostinger server"""
    print(f"🔗 Connecting to {HOST}...")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(HOST, PORT, USERNAME, PASSWORD)
        print("✅ SSH connection established\n")

        # Create bare repository
        commands = [
            f"mkdir -p {GIT_REPO_PATH}",
            f"cd {GIT_REPO_PATH} && git init --bare",
        ]

        print(f"📂 Creating bare git repository at {GIT_REPO_PATH}...")
        for cmd in commands:
            stdin, stdout, stderr = client.exec_command(cmd)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()

            if output:
                print(f"   {output}")
            if error and "Initialized empty Git repository" not in error:
                print(f"   ⚠️  {error}")

        print("✅ Bare repository created on Hostinger\n")
        client.close()

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

    return True

def setup_local_git():
    """Configure local git remote pointing to Hostinger"""
    repo_url = f"ssh://root@{HOST}{GIT_REPO_PATH}"

    print(f"📌 Configuring local git remote...")
    print(f"   Remote URL: {repo_url}\n")

    try:
        # Remove existing remote if it exists
        subprocess.run(["git", "remote", "remove", "origin"],
                      capture_output=True, text=True)

        # Add new remote
        result = subprocess.run(["git", "remote", "add", "origin", repo_url],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Git remote 'origin' configured\n")
        else:
            print(f"❌ Failed to add remote: {result.stderr}")
            return False

        # Ensure we're on main branch
        subprocess.run(["git", "branch", "-M", "main"],
                      capture_output=True, text=True)

        print("📤 Pushing code to Hostinger...\n")
        result = subprocess.run(["git", "push", "-u", "origin", "main"],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Code pushed to Hostinger!\n")
        else:
            print(f"⚠️  Push output:\n{result.stdout}")
            if "password" in result.stderr.lower():
                print("💡 Git needs SSH access. You may be prompted for server password.\n")

        return True

    except Exception as e:
        print(f"❌ Git operation failed: {e}")
        return False

def update_deploy_script():
    """Update deploy.py with correct git URL and domain"""
    print("📝 Updating deploy.py configuration...\n")

    repo_url = f"ssh://root@{HOST}{GIT_REPO_PATH}"
    domain = "87.106.215.187.nip.io"

    try:
        with open("deploy.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Update REPO_URL
        content = content.replace(
            'REPO_URL = "https://github.com/yourusername/musikwunsch-app.git"',
            f'REPO_URL = "{repo_url}"'
        )

        # Update DOMAIN
        content = content.replace(
            'DOMAIN = "musikwunsch.example.com"',
            f'DOMAIN = "{domain}"'
        )

        with open("deploy.py", "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ deploy.py updated:")
        print(f"   REPO_URL = {repo_url}")
        print(f"   DOMAIN = {domain}\n")

        return True

    except Exception as e:
        print(f"❌ Failed to update deploy.py: {e}")
        return False

def main():
    """Main setup flow"""
    print("""
╔════════════════════════════════════════════════════════╗
║      🎵 HOSTINGER GIT SETUP - MUSIKWUNSCH APP         ║
╚════════════════════════════════════════════════════════╝
    """)

    # Step 1: Create bare repository on Hostinger
    if not setup_remote_git():
        sys.exit(1)

    # Step 2: Configure local git remote
    if not setup_local_git():
        sys.exit(1)

    # Step 3: Update deploy.py
    if not update_deploy_script():
        sys.exit(1)

    # Summary
    print("="*60)
    print("✅ SETUP COMPLETE!\n")
    print("Next step: Run deployment")
    print("   $ python deploy.py\n")
    print("="*60)

if __name__ == "__main__":
    main()
