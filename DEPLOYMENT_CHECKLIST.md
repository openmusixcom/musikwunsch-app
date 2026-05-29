# 🚀 Deployment Checklist - Musikwunsch App

## Pre-Deployment Steps

### Step 1: Git Repository Setup (Choose ONE)

#### Option A: GitHub (Recommended for version control)
1. Create repository on GitHub.com (if you don't have account, sign up)
2. Push your code:
   ```bash
   git remote add origin https://github.com/yourusername/musikwunsch-app.git
   git branch -M main
   git push -u origin main
   ```
3. Update `deploy.py` line 16:
   ```python
   REPO_URL = "https://github.com/yourusername/musikwunsch-app.git"
   ```

#### Option B: Direct Hostinger Git Setup (Fastest)
1. SSH to Hostinger and create bare repository:
   ```bash
   ssh root@187.124.20.215
   mkdir -p /var/repos/musikwunsch.git
   cd /var/repos/musikwunsch.git
   git init --bare
   exit
   ```
2. Add Hostinger as remote:
   ```bash
   cd C:\Users\cwoll\Doku\Claude\DJapp
   git remote add origin ssh://root@187.124.20.215/var/repos/musikwunsch.git
   git branch -M main
   git push -u origin main
   ```
3. Update `deploy.py` line 16:
   ```python
   REPO_URL = "ssh://root@187.124.20.215/var/repos/musikwunsch.git"
   ```

---

### Step 2: Configure Domain (Required for SSL)

You need a domain name for SSL certificate. Options:

#### Option A: Use Hostinger's Domain
1. Log in to Hostinger control panel
2. Buy a domain or use subdomain (e.g., `musikwunsch.yourdomain.com`)
3. Point DNS A record to `187.124.20.215`
4. Update `deploy.py` line 18:
   ```python
   DOMAIN = "musikwunsch.yourdomain.com"
   ```

#### Option B: Temporary Testing
Use `87.106.215.187.nip.io` (temporary):
```python
DOMAIN = "87.106.215.187.nip.io"  # Maps to your Hostinger IP
```

#### Option C: Manual DNS Later
For now, use placeholder but remember to configure before deployment completes:
```python
DOMAIN = "musikwunsch.example.com"
```

---

### Step 3: Update deploy.py Configuration

Edit `deploy.py` and ensure these are set:

```python
# Line 12 - Already correct ✓
HOST = "187.124.20.215"

# Line 14 - Already correct ✓
USERNAME = "root"

# Line 15 - Already correct ✓
PASSWORD = "Extra01#1234"

# Line 16 - UPDATE with your Git repo URL
REPO_URL = "https://github.com/yourusername/musikwunsch-app.git"  # OR Option B URL

# Line 17 - Already correct ✓
PROJECT_DIR = "/var/www/musikwunsch-app"

# Line 18 - UPDATE with your domain
DOMAIN = "musikwunsch.yourdomain.com"  # OR nip.io OR example.com
```

---

### Step 4: Test Configuration

Before running deployment, verify:

```bash
# Check git remote is configured
git remote -v

# Should show:
# origin    https://github.com/yourusername/musikwunsch-app.git (fetch)
# origin    https://github.com/yourusername/musikwunsch-app.git (push)
```

---

## Deployment Execution

### Command 1: Run Deployment Script
```bash
cd C:\Users\cwoll\Doku\Claude\DJapp
python deploy.py
```

**Expected Output:**
```
╔════════════════════════════════════════════╗
║  🎵 MUSIKWUNSCH DJ APP - HOSTINGER DEPLOY  ║
╚════════════════════════════════════════════╝

🔗 Connecting to 187.124.20.215...
✅ SSH connection established
🔧 📦 Updating system packages
   $ apt-get update && apt-get upgrade -y
   [output...]
...
✅ DEPLOYMENT COMPLETE!
```

This takes **10-15 minutes**. The script will:
- ✅ Install Node.js 18 & PostgreSQL
- ✅ Create musikwunsch database
- ✅ Clone your repository
- ✅ Install dependencies
- ✅ Run migrations
- ✅ Build frontend
- ✅ Start backend with PM2
- ✅ Configure Nginx reverse proxy
- ⏳ Prepare SSL (manual step next)

---

## Post-Deployment Steps

### Step 1: Configure SSL Certificate

After deployment completes, you'll see:
```
⚠️  Run this command manually on server:
   $ certbot certonly --standalone -d musikwunsch.yourdomain.com
   Then restart Nginx: systemctl restart nginx
```

**Run these commands manually:**

```bash
# SSH into Hostinger
ssh root@187.124.20.215

# Get SSL certificate (interactive, answers domain questions)
certbot certonly --standalone -d musikwunsch.yourdomain.com

# Restart Nginx to apply SSL
systemctl restart nginx

# Verify SSL is working
curl https://musikwunsch.yourdomain.com

# Exit SSH
exit
```

### Step 2: Create Admin Account

```bash
# Open your app in browser
https://musikwunsch.yourdomain.com

# Click "Register here"
# Create admin account:
# - Email: admin@yourdomain.com
# - Password: strong-password-here
# - Role: admin

# You're logged in to admin panel! 🎉
```

### Step 3: Verify Deployment

Check that everything is running:

```bash
# SSH into server
ssh root@187.124.20.215

# Check backend API
pm2 status
# Should show: musikwunsch-api is online

# Check logs for errors
pm2 logs musikwunsch-api

# Check Nginx is running
systemctl status nginx

# Test backend health
curl http://localhost:3000/api/health
# Should respond with: {"status":"ok",...}

# Exit
exit
```

---

## Troubleshooting

### SSL Certificate Failed
If certbot fails, common causes:
- DNS not pointing to 187.124.20.215 yet
- Port 80 is blocked (firewall)
- Domain recently configured (DNS propagation delay, wait 10 min)

**Solution:**
```bash
ssh root@187.124.20.215
# Wait for DNS to propagate, then:
certbot certonly --standalone -d musikwunsch.yourdomain.com
systemctl restart nginx
```

### Backend Not Starting
```bash
ssh root@187.124.20.215
pm2 logs musikwunsch-api
# Check error messages
```

### Git Clone Failed
Verify REPO_URL in deploy.py is correct and accessible.

---

## What's Next?

✅ Phase 1 Complete: Core authentication & API

Next phases to implement:
- 🎭 Phase 2: Guest App (QR-code, music search, voting)
- 📊 Phase 3: DJ Dashboard
- 🔄 Phase 4: Real-time sync (WebSockets)
- 💳 Phase 5: PayPal integration
- 🔒 Phase 6: Security hardening

Each phase will be deployed using the same `deploy.py` script or git push → auto-deploy setup (optional).

---

## Quick Reference

| Component | URL |
|-----------|-----|
| Frontend | https://musikwunsch.yourdomain.com |
| Backend API | https://musikwunsch.yourdomain.com/api |
| Health Check | https://musikwunsch.yourdomain.com/api/health |
| Logs (SSH) | `pm2 logs musikwunsch-api` |
| Database | PostgreSQL @ 187.124.20.215:5432 |
| Process Manager | PM2 (manage with `pm2 restart all`) |

