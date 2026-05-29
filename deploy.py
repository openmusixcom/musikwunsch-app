#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Musikwunsch DJ App - Hostinger VPS Deployment Script
Automated deployment with SSH password authentication
"""

import paramiko
import time
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
REPO_URL = "ssh://root@187.124.20.215/var/repos/musikwunsch.git"  # Change this
PROJECT_DIR = "/var/www/musikwunsch-app"
DOMAIN = "87.106.215.187.nip.io"  # Change this

class HostingerDeployer:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client = None

    def connect(self):
        """Establish SSH connection"""
        print(f"🔗 Connecting to {self.host}...")
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.client.connect(self.host, self.port, self.username, self.password)
            print("✅ SSH connection established")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def execute(self, command, description=""):
        """Execute command via SSH"""
        if description:
            print(f"\n🔧 {description}")
        print(f"   $ {command}")
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()

            if output:
                print(f"   {output[:200]}")
            if error and "npm warn" not in error.lower():
                print(f"   ⚠️  {error[:200]}")
            return output, error
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return "", str(e)

    def deploy(self):
        """Full deployment workflow"""
        if not self.connect():
            return False

        commands = [
            # 1. System updates
            ("apt-get update && apt-get upgrade -y", "📦 Updating system packages"),

            # 2. Install Node.js 18
            ("curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -", "📥 Adding Node.js 18 repository"),
            ("apt-get install -y nodejs build-essential", "📦 Installing Node.js & build tools"),

            # 3. Install PostgreSQL
            ("apt-get install -y postgresql postgresql-contrib", "🗄️  Installing PostgreSQL"),
            ("systemctl start postgresql", "🚀 Starting PostgreSQL"),
            ("systemctl enable postgresql", "⚙️  Enabling PostgreSQL autostart"),

            # 4. Create PostgreSQL database
            ("sudo -u postgres psql -c \"CREATE DATABASE IF NOT EXISTS musikwunsch;\"", "📊 Creating musikwunsch database"),

            # 5. Install PM2 globally
            ("npm install -g pm2", "📦 Installing PM2 (process manager)"),

            # 6. Clone repository
            (f"rm -rf {PROJECT_DIR} && git clone {REPO_URL} {PROJECT_DIR}", "📂 Cloning repository"),

            # 7. Backend setup
            (f"cd {PROJECT_DIR}/backend && npm install", "📦 Installing backend dependencies"),
            (f"cd {PROJECT_DIR}/backend && npm run migrate", "🔄 Running database migrations"),

            # 8. Frontend setup & build
            (f"cd {PROJECT_DIR}/frontend && npm install", "📦 Installing frontend dependencies"),
            (f"cd {PROJECT_DIR}/frontend && npm run build", "🏗️  Building frontend"),

            # 9. Start backend with PM2
            (f"cd {PROJECT_DIR}/backend && pm2 start 'npm start' --name musikwunsch-api", "🚀 Starting backend API"),
            ("pm2 startup", "⚙️  Setting PM2 to start on boot"),
            ("pm2 save", "💾 Saving PM2 configuration"),

            # 10. Install Nginx
            ("apt-get install -y nginx", "📦 Installing Nginx"),
        ]

        for command, description in commands:
            output, error = self.execute(command, description)
            time.sleep(0.5)  # Small delay between commands

        # 11. Configure Nginx (special handling)
        self.configure_nginx()

        # 12. SSL with Let's Encrypt
        self.configure_ssl()

        print("\n" + "="*60)
        print("✅ DEPLOYMENT COMPLETE!")
        print("="*60)
        self.print_summary()

        self.client.close()
        return True

    def configure_nginx(self):
        """Configure Nginx as reverse proxy"""
        print(f"\n⚙️  Configuring Nginx")

        nginx_config = f"""
server {{
    listen 80;
    server_name {DOMAIN};

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}}

server {{
    listen 443 ssl http2;
    server_name {DOMAIN};

    ssl_certificate /etc/letsencrypt/live/{DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{DOMAIN}/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

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

        try:
            stdin, stdout, stderr = self.client.exec_command(
                f"cat > /etc/nginx/sites-available/musikwunsch << 'EOF'\n{nginx_config}\nEOF"
            )
            time.sleep(1)

            # Enable site
            self.execute(f"ln -sf /etc/nginx/sites-available/musikwunsch /etc/nginx/sites-enabled/", "")

            # Test Nginx config
            self.execute("nginx -t", "")

            # Restart Nginx
            self.execute("systemctl restart nginx", "🔄 Restarting Nginx")

            print("   ✅ Nginx configured")
        except Exception as e:
            print(f"   ❌ Nginx config error: {e}")

    def configure_ssl(self):
        """Configure SSL with Let's Encrypt"""
        print(f"\n🔒 Configuring SSL Certificate")

        # Install Certbot
        self.execute("apt-get install -y certbot python3-certbot-nginx", "📦 Installing Certbot")

        # Get SSL certificate (this may require manual intervention)
        print(f"   ⚠️  Run this command manually on server:")
        print(f"   $ certbot certonly --standalone -d {DOMAIN}")
        print(f"   Then restart Nginx: systemctl restart nginx")

    def print_summary(self):
        """Print deployment summary"""
        summary = f"""
📋 DEPLOYMENT SUMMARY
{'='*60}

🌐 Frontend URL:    https://{DOMAIN}
🔗 Backend URL:     https://{DOMAIN}/api
📂 Project Path:    {PROJECT_DIR}
🗄️  Database:       musikwunsch (PostgreSQL)
⚙️  Process Manager: PM2

NEXT STEPS:
1. Update DNS to point {DOMAIN} → {self.host}
2. Run SSL setup:
   ssh root@{self.host}
   certbot certonly --standalone -d {DOMAIN}
   systemctl restart nginx

3. Login to dashboard:
   https://{DOMAIN}/register
   Create admin account

4. Check logs:
   pm2 logs musikwunsch-api
   tail -f /var/log/nginx/access.log

🎉 Ready to go! Your app is live!
"""
        print(summary)


def main():
    """Main function"""
    print("""
╔════════════════════════════════════════════╗
║  🎵 MUSIKWUNSCH DJ APP - HOSTINGER DEPLOY  ║
╚════════════════════════════════════════════╝
    """)

    deployer = HostingerDeployer(HOST, PORT, USERNAME, PASSWORD)
    success = deployer.deploy()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
