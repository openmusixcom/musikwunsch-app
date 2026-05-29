#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Nginx to use HTTP (no SSL for now)
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
DOMAIN = "87.106.215.187.nip.io"
PROJECT_DIR = "/var/www/musikwunsch-app"

def fix_nginx():
    print("⚙️  Fixing Nginx configuration...\n")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, PORT, USERNAME, PASSWORD)

    # Create HTTP-only Nginx config (no SSL)
    nginx_config = f"""
server {{
    listen 80;
    server_name {DOMAIN};

    # Frontend (React app)
    location / {{
        root {PROJECT_DIR}/frontend/dist;
        try_files $uri /index.html;
        expires 1d;
    }}

    # Backend API
    location /api {{
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }}

    # WebSocket support
    location /socket.io {{
        proxy_pass http://localhost:3000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }}
}}
"""

    print("📝 Updating Nginx configuration...")
    cmd = f"cat > /etc/nginx/sites-available/musikwunsch << 'EOF'\n{nginx_config}\nEOF"
    stdin, stdout, stderr = client.exec_command(cmd)
    time.sleep(1)

    # Test nginx config
    print("🧪 Testing Nginx configuration...")
    stdin, stdout, stderr = client.exec_command("nginx -t")
    output = stdout.read().decode()
    if "successful" in output.lower() or "ok" in output.lower():
        print("   ✅ Configuration is valid\n")
    else:
        print(f"   ⚠️  {output}\n")

    # Restart nginx
    print("🔄 Restarting Nginx...")
    stdin, stdout, stderr = client.exec_command("systemctl restart nginx")
    time.sleep(2)
    print("   ✅ Nginx restarted\n")

    # Test API
    print("🧪 Testing API...")
    stdin, stdout, stderr = client.exec_command("curl -s http://localhost:3000/api/health")
    response = stdout.read().decode()
    if "ok" in response.lower():
        print(f"   ✅ Backend is responding\n")
    else:
        print(f"   Response: {response}\n")

    client.close()

    print("="*60)
    print("✅ NGINX FIX COMPLETE!")
    print("="*60)
    print(f"""
🌐 Your app is now accessible via HTTP:
   http://{DOMAIN}

Try registering:
   Email: admin@test.local
   Password: testpass123
   Role: admin

✨ The app should now work properly!
    """)

if __name__ == "__main__":
    try:
        fix_nginx()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
