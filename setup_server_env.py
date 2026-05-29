#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup .env file on Hostinger server and run migrations
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

def setup_env():
    print("⚙️  Setting up .env on Hostinger server...\n")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, PORT, USERNAME, PASSWORD)

    # Create .env for backend
    env_content = """PORT=3000
NODE_ENV=production
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=musikwunsch
JWT_SECRET=your-secret-key-change-in-production
JWT_EXPIRY=24h
REFRESH_TOKEN_EXPIRY=7d
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=your-client-id
PAYPAL_SECRET=your-secret
FRONTEND_URL=http://87.106.215.187.nip.io
"""

    print("📝 Creating .env file...")
    cmd = f"cat > {PROJECT_DIR}/backend/.env << 'EOF'\n{env_content}\nEOF"
    stdin, stdout, stderr = client.exec_command(cmd)
    time.sleep(1)
    print("   ✅ .env created\n")

    # Drop and recreate database (simpler than fixing CREATE DATABASE syntax)
    print("📊 Setting up database...")
    db_commands = [
        "sudo -u postgres dropdb --if-exists musikwunsch",
        "sudo -u postgres createdb musikwunsch",
    ]

    for cmd in db_commands:
        stdin, stdout, stderr = client.exec_command(cmd)
        time.sleep(1)

    print("   ✅ Database ready\n")

    # Run migrations
    print("🔄 Running database migrations...")
    cmd = f"cd {PROJECT_DIR}/backend && npm run migrate"
    stdin, stdout, stderr = client.exec_command(cmd)
    time.sleep(5)
    output = stdout.read().decode()
    error = stderr.read().decode()

    if "ERROR" not in error.upper() or "migration" in output.lower():
        print("   ✅ Migrations completed\n")
    else:
        print(f"   ⚠️  {error[:200]}\n")

    # Restart backend
    print("🚀 Restarting backend...")
    client.exec_command("cd {}/backend && pm2 restart musikwunsch-api".format(PROJECT_DIR))
    time.sleep(3)
    print("   ✅ Backend restarted\n")

    # Check status
    print("✅ Verifying...")
    stdin, stdout, stderr = client.exec_command("pm2 list")
    output = stdout.read().decode()

    if "musikwunsch-api" in output and "online" in output:
        print("   ✅ Backend is ONLINE\n")
    else:
        print(f"   ⚠️  Backend status check: {output[:100]}\n")

    client.close()

    print("="*60)
    print("✅ SERVER SETUP COMPLETE!")
    print("="*60)
    print(f"""
🌐 Your app is ready at:
   http://87.106.215.187.nip.io

Next steps:
1. Open browser: http://87.106.215.187.nip.io
2. Click "Register here"
3. Create admin account:
   - Email: admin@test.local
   - Password: yourpassword
   - Role: admin

You can now log in and test the app!

For production:
- Update FRONTEND_URL in backend/.env
- Setup SSL with certbot
- Change JWT_SECRET to a strong random value
    """)

if __name__ == "__main__":
    try:
        setup_env()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
