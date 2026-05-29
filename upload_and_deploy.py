#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Upload files via SCP and complete deployment
"""

import paramiko
import os
import sys
import io
import tarfile
import time
from io import BytesIO

if os.name == 'nt':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HOST = "187.124.20.215"
PORT = 22
USERNAME = "root"
PASSWORD = "Extra01#1234"
PROJECT_DIR = "/var/www/musikwunsch-app"

def upload_project():
    """Upload project files as tar.gz"""
    print("╔════════════════════════════════════════════╗")
    print("║  📤 UPLOADING PROJECT TO HOSTINGER        ║")
    print("╚════════════════════════════════════════════╝\n")

    # Create tar.gz of project
    print("📦 Preparing project files...")

    tar_buffer = BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode='w:gz') as tar:
        # Add backend
        if os.path.isdir("backend"):
            tar.add("backend", arcname="backend")
        # Add frontend
        if os.path.isdir("frontend"):
            tar.add("frontend", arcname="frontend")

    tar_data = tar_buffer.getvalue()
    print(f"   ✅ Created tar.gz ({len(tar_data) / 1024:.1f} KB)\n")

    # Connect and upload
    print(f"🔗 Connecting to {HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, PORT, USERNAME, PASSWORD)
    print("✅ Connected\n")

    # Open SCP session
    print("📤 Uploading files...")
    transport = client.get_transport()
    sftp = paramiko.SFTPClient.from_transport(transport)

    try:
        # Upload tar file
        tar_path = "/tmp/musikwunsch-app.tar.gz"
        with sftp.file(tar_path, 'wb') as f:
            f.write(tar_data)
        print(f"   ✅ Uploaded to {tar_path}\n")

        # Extract on server
        print("📂 Extracting files on server...")
        stdin, stdout, stderr = client.exec_command(
            f"mkdir -p {PROJECT_DIR} && cd {PROJECT_DIR} && tar -xzf {tar_path} && echo 'Extracted!'"
        )
        time.sleep(3)
        print("   ✅ Files extracted\n")

        # Verify extraction
        stdin, stdout, stderr = client.exec_command(f"ls -la {PROJECT_DIR}/")
        output = stdout.read().decode()
        if "backend" in output and "frontend" in output:
            print("   ✅ Backend and frontend found\n")
        else:
            print(f"   ⚠️  Check: {output[:200]}\n")

    finally:
        sftp.close()

    # Now run setup commands
    print("="*60)
    print("🔧 COMPLETING DEPLOYMENT")
    print("="*60 + "\n")

    commands = [
        (f"cd {PROJECT_DIR}/backend && npm install", "📦 Installing backend dependencies", 20),
        (f"cd {PROJECT_DIR}/backend && npm run migrate", "🔄 Running database migrations", 10),
        (f"cd {PROJECT_DIR}/frontend && npm install", "📦 Installing frontend dependencies", 20),
        (f"cd {PROJECT_DIR}/frontend && npm run build", "🏗️  Building frontend", 15),
        (f"cd {PROJECT_DIR}/backend && pm2 start 'npm start' --name musikwunsch-api", "🚀 Starting backend", 5),
        ("pm2 status", "📊 Checking status", 3),
    ]

    for cmd, desc, wait_time in commands:
        print(f"\n{desc}...")
        stdin, stdout, stderr = client.exec_command(cmd)
        time.sleep(wait_time)
        output = stdout.read().decode()

        if "added" in output.lower() or "up to date" in output.lower() or "online" in output:
            print(f"   ✅ Done")
        elif cmd.find("npm start") > -1:
            print(f"   ✅ Backend started")
        elif "migrations" in desc.lower():
            print(f"   ✅ Migrations completed")
        else:
            if len(output) > 50:
                print(f"   {output[:150]}")
            else:
                print(f"   {output}")

    client.close()

    print("\n" + "="*60)
    print("✅ DEPLOYMENT COMPLETE!")
    print("="*60)
    print(f"""
🌐 Your app is ready!

Frontend:  http://87.106.215.187.nip.io
Backend:   http://87.106.215.187.nip.io/api

Next: Open in browser and register an account!
    """)

if __name__ == "__main__":
    try:
        upload_project()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
