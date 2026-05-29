#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deploy Musikwunsch App with Docker to Hostinger
"""

import paramiko
import time
import sys
import io
import os
import tarfile
from io import BytesIO

if os.name == 'nt':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HOST = "187.124.20.215"
PORT = 22
USERNAME = "root"
PASSWORD = "Extra01#1234"
PROJECT_DIR = "/var/www/musikwunsch-app-docker"

def deploy_docker():
    print("╔════════════════════════════════════════════╗")
    print("║  🐳 MUSIKWUNSCH - DOCKER DEPLOYMENT       ║")
    print("╚════════════════════════════════════════════╝\n")

    # Step 1: Create tar.gz of project
    print("📦 Preparing Docker project...")
    tar_buffer = BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode='w:gz') as tar:
        tar.add("backend", arcname="backend")
        tar.add("frontend", arcname="frontend")
        tar.add("docker-compose.yml", arcname="docker-compose.yml")
        tar.add("Dockerfile.backend", arcname="Dockerfile.backend")
        tar.add("Dockerfile.frontend", arcname="Dockerfile.frontend")
        tar.add("nginx.conf", arcname="nginx.conf")

    tar_data = tar_buffer.getvalue()
    print(f"   ✅ Created tar ({len(tar_data) / 1024:.1f} KB)\n")

    # Step 2: Connect and upload
    print(f"🔗 Connecting to {HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, PORT, USERNAME, PASSWORD)
    print("✅ Connected\n")

    # Step 3: Upload and extract
    print("📤 Uploading Docker files...")
    transport = client.get_transport()
    sftp = paramiko.SFTPClient.from_transport(transport)

    tar_path = f"{PROJECT_DIR}/docker.tar.gz"

    try:
        # Create project directory
        stdin, stdout, stderr = client.exec_command(f"mkdir -p {PROJECT_DIR}")
        time.sleep(1)

        # Upload tar
        with sftp.file(tar_path, 'wb') as f:
            f.write(tar_data)
        print(f"   ✅ Uploaded\n")

        # Extract
        print("📂 Extracting files...")
        stdin, stdout, stderr = client.exec_command(
            f"cd {PROJECT_DIR} && tar -xzf docker.tar.gz && ls -la"
        )
        time.sleep(2)
        print("   ✅ Extracted\n")

    finally:
        sftp.close()

    # Step 4: Stop old containers (if any)
    print("🛑 Stopping old containers...")
    stdin, stdout, stderr = client.exec_command(
        f"cd {PROJECT_DIR} && docker compose down 2>/dev/null || true"
    )
    time.sleep(3)
    print("   ✅ Done\n")

    # Step 5: Build and start with Docker
    print("🏗️  Building Docker images...")
    stdin, stdout, stderr = client.exec_command(
        f"cd {PROJECT_DIR} && docker compose build --no-cache"
    )
    time.sleep(30)  # Building takes time
    output = stdout.read().decode()
    print("   ✅ Images built\n")

    # Step 6: Start containers
    print("🚀 Starting containers...")
    stdin, stdout, stderr = client.exec_command(
        f"cd {PROJECT_DIR} && docker compose up -d"
    )
    time.sleep(10)
    output = stdout.read().decode()
    print("   ✅ Containers started\n")

    # Step 7: Check status
    print("✅ Checking container status...")
    stdin, stdout, stderr = client.exec_command(
        f"cd {PROJECT_DIR} && docker compose ps"
    )
    status = stdout.read().decode()
    print(f"{status}\n")

    # Step 8: Test
    print("🧪 Testing application...")
    time.sleep(5)
    stdin, stdout, stderr = client.exec_command(
        "curl -s http://localhost/api/health | head -100"
    )
    response = stdout.read().decode()
    if "ok" in response.lower():
        print(f"   ✅ API is responding\n")
    else:
        print(f"   Response: {response[:100]}\n")

    client.close()

    print("="*60)
    print("✅ DOCKER DEPLOYMENT COMPLETE!")
    print("="*60)
    print(f"""
🌐 Your app is ready at:
   http://87.106.215.187.nip.io

🐳 Docker containers running:
   - musikwunsch-db (PostgreSQL)
   - musikwunsch-api (Node.js Backend)
   - musikwunsch-web (Nginx Frontend)

📊 Useful Docker commands:

   View logs:
   docker logs musikwunsch-api

   Stop all:
   docker-compose -f {PROJECT_DIR}/docker-compose.yml down

   Restart:
   docker-compose -f {PROJECT_DIR}/docker-compose.yml restart

🎉 Try registering now:
   Email: admin@test.local
   Password: testpass123
   Role: admin
    """)

if __name__ == "__main__":
    try:
        deploy_docker()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
