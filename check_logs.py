#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check backend logs to see registration error
"""

import paramiko
import sys
import io
import os

if os.name == 'nt':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HOST = "187.124.20.215"
PORT = 22
USERNAME = "root"
PASSWORD = "Extra01#1234"

def check_logs():
    print("🔍 Checking backend logs...\n")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, PORT, USERNAME, PASSWORD)

    # Check PM2 logs
    print("📋 PM2 Logs (Backend):")
    print("="*60)
    stdin, stdout, stderr = client.exec_command("pm2 logs musikwunsch-api --nostream --lines 50")
    output = stdout.read().decode()
    print(output)

    print("\n" + "="*60)
    print("\n📊 Backend Status:")
    print("="*60)
    stdin, stdout, stderr = client.exec_command("pm2 status")
    output = stdout.read().decode()
    print(output)

    print("\n" + "="*60)
    print("\n🔗 Check API Health:")
    print("="*60)
    stdin, stdout, stderr = client.exec_command("curl -s http://localhost:3000/api/health | head -100")
    output = stdout.read().decode()
    print(output)

    print("\n" + "="*60)
    print("\n⚙️  Database Connection Test:")
    print("="*60)
    stdin, stdout, stderr = client.exec_command("sudo -u postgres psql -d musikwunsch -c 'SELECT NOW();'")
    output = stdout.read().decode()
    error = stderr.read().decode()
    if output:
        print(f"✅ Database is connected: {output}")
    if error:
        print(f"Error: {error}")

    print("\n" + "="*60)
    print("\n📁 Project Files Check:")
    print("="*60)
    stdin, stdout, stderr = client.exec_command("ls -la /var/www/musikwunsch-app/backend/")
    output = stdout.read().decode()
    print(output[:500])

    client.close()

if __name__ == "__main__":
    try:
        check_logs()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
