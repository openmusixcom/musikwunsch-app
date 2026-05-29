#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug registration issues
"""

import paramiko
import sys
import io
import os
import json

if os.name == 'nt':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HOST = "187.124.20.215"
PORT = 22
USERNAME = "root"
PASSWORD = "Extra01#1234"

def debug():
    print("🔍 Debugging Registration Issues...\n")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, PORT, USERNAME, PASSWORD)

    # Check 1: Backend logs
    print("📋 Recent backend logs:")
    print("="*60)
    stdin, stdout, stderr = client.exec_command("pm2 logs musikwunsch-api --nostream --lines 30")
    output = stdout.read().decode()
    print(output[-1000:])  # Last 1000 chars

    # Check 2: Test registration API directly
    print("\n\n🧪 Testing registration API:")
    print("="*60)
    cmd = """curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123","role":"dj"}' \
  2>/dev/null | head -500"""

    stdin, stdout, stderr = client.exec_command(cmd)
    response = stdout.read().decode()
    print(f"Response:\n{response}")

    # Check 3: Nginx configuration
    print("\n\n⚙️  Nginx configuration:")
    print("="*60)
    stdin, stdout, stderr = client.exec_command("cat /etc/nginx/sites-enabled/musikwunsch | head -50")
    output = stdout.read().decode()
    print(output)

    # Check 4: Backend files
    print("\n\n📁 Backend structure:")
    print("="*60)
    stdin, stdout, stderr = client.exec_command("ls -la /var/www/musikwunsch-app/backend/src/")
    output = stdout.read().decode()
    print(output)

    # Check 5: Frontend build
    print("\n\n📦 Frontend build:")
    print("="*60)
    stdin, stdout, stderr = client.exec_command("ls -la /var/www/musikwunsch-app/frontend/dist/ | head -20")
    output = stdout.read().decode()
    print(output)

    client.close()

if __name__ == "__main__":
    debug()
