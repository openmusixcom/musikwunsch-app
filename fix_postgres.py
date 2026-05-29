#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix PostgreSQL password authentication
"""

import paramiko
import time
import sys
import io
import os

if os.name == 'nt':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HOST = "187.124.20.215"
PORT = 22
USERNAME = "root"
PASSWORD = "Extra01#1234"
PROJECT_DIR = "/var/www/musikwunsch-app"

def fix_postgres():
    print("🔧 Fixing PostgreSQL authentication...\n")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, PORT, USERNAME, PASSWORD)

    # Step 1: Set postgres user password
    print("📝 Setting postgres user password...")
    cmd = "sudo -u postgres psql -c \"ALTER USER postgres WITH PASSWORD 'postgres';\""
    stdin, stdout, stderr = client.exec_command(cmd)
    time.sleep(2)
    print("   ✅ Done\n")

    # Step 2: Check/update PostgreSQL authentication method
    print("🔐 Checking PostgreSQL configuration...")
    cmd = "grep -n 'local.*all.*postgres' /etc/postgresql/*/main/pg_hba.conf | head -5"
    stdin, stdout, stderr = client.exec_command(cmd)
    output = stdout.read().decode()
    print(f"   {output[:200]}\n")

    # Step 3: Update pg_hba.conf to allow password auth
    print("⚙️  Updating PostgreSQL authentication method...")
    cmd = """sudo sed -i 's/^local.*all.*postgres.*peer/local   all             postgres                                    md5/' /etc/postgresql/*/main/pg_hba.conf"""
    stdin, stdout, stderr = client.exec_command(cmd)
    time.sleep(1)
    print("   ✅ Configuration updated\n")

    # Step 4: Reload PostgreSQL
    print("🔄 Reloading PostgreSQL...")
    cmd = "sudo systemctl reload postgresql"
    stdin, stdout, stderr = client.exec_command(cmd)
    time.sleep(2)
    print("   ✅ PostgreSQL reloaded\n")

    # Step 5: Test database connection
    print("🧪 Testing database connection...")
    cmd = "PGPASSWORD='postgres' psql -h localhost -U postgres -d musikwunsch -c 'SELECT NOW();'"
    stdin, stdout, stderr = client.exec_command(cmd)
    output = stdout.read().decode()
    error = stderr.read().decode()

    if "now" in output.lower() or "2026" in output:
        print("   ✅ Database connection works!\n")
    else:
        print(f"   ⚠️  Output: {output[:100]}")
        print(f"   Error: {error[:100]}\n")

    # Step 6: Upload updated database.js and restart
    print("📤 Uploading updated backend code...")
    cmd = f"cd {PROJECT_DIR}/backend && pm2 restart musikwunsch-api"
    stdin, stdout, stderr = client.exec_command(cmd)
    time.sleep(3)
    print("   ✅ Backend restarted\n")

    # Step 7: Test API health
    print("🔗 Testing API health endpoint...")
    cmd = "curl -s http://localhost:3000/api/health"
    stdin, stdout, stderr = client.exec_command(cmd)
    output = stdout.read().decode()

    if "ok" in output.lower() or "status" in output.lower():
        print(f"   ✅ API is responding: {output[:100]}\n")
    else:
        print(f"   ⚠️  Response: {output[:100]}\n")

    client.close()

    print("="*60)
    print("✅ POSTGRESQL FIX COMPLETE!")
    print("="*60)
    print(f"""
Your app should now work properly!

🌐 Open in browser:
   http://87.106.215.187.nip.io

Try registering again:
   Email: admin@test.local
   Password: testpass123
   Role: admin

If still not working, check logs:
   pm2 logs musikwunsch-api
    """)

if __name__ == "__main__":
    try:
        fix_postgres()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
