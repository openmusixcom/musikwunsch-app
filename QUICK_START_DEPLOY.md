# ⚡ Quick Start Deployment (5 minutes)

## Fastest Path to Production

### Step 1: Set Up Git on Hostinger (2 min)

Run these commands in PowerShell:

```powershell
# Create bare repository on Hostinger server
$ssh_cmd = @"
mkdir -p /var/repos/musikwunsch.git
cd /var/repos/musikwunsch.git
git init --bare
"@

# Note: Can't run multi-line SSH from PowerShell easily.
# Instead, do this manually via SSH:
# ssh root@187.124.20.215
# Then paste these commands:

# mkdir -p /var/repos/musikwunsch.git
# cd /var/repos/musikwunsch.git  
# git init --bare
# exit
```

**Or use PuTTY/Terminal:**
```bash
ssh root@187.124.20.215
mkdir -p /var/repos/musikwunsch.git
cd /var/repos/musikwunsch.git
git init --bare
exit
```

### Step 2: Add Git Remote Locally (1 min)

```bash
cd C:\Users\cwoll\Doku\Claude\DJapp
git remote add origin ssh://root@187.124.20.215/var/repos/musikwunsch.git
git branch -M main
git push -u origin main
```

### Step 3: Update deploy.py (1 min)

**Edit `C:\Users\cwoll\Doku\Claude\DJapp\deploy.py` lines 16 & 18:**

Replace:
```python
REPO_URL = "https://github.com/yourusername/musikwunsch-app.git"  # Change this
DOMAIN = "musikwunsch.example.com"  # Change this
```

With:
```python
REPO_URL = "ssh://root@187.124.20.215/var/repos/musikwunsch.git"
DOMAIN = "87.106.215.187.nip.io"  # Temporary: maps to Hostinger IP
```

### Step 4: Deploy (1 min start, 10-15 min execution)

```bash
cd C:\Users\cwoll\Doku\Claude\DJapp
python deploy.py
```

**Watch the output.** When complete, you'll see:**
```
✅ DEPLOYMENT COMPLETE!

🌐 Frontend URL:    https://87.106.215.187.nip.io
🔗 Backend URL:     https://87.106.215.187.nip.io/api
```

### Step 5: Verify (2 min)

Open in browser:
```
https://87.106.215.187.nip.io
```

Click "Register here" and create admin account:
- Email: `admin@test.local`
- Password: `yourpassword`
- Role: `admin`

✅ **You're live!**

---

## After Testing: Use Real Domain

Once verified, set up real domain:

1. **Get domain from Hostinger:**
   - Log in to Hostinger control panel
   - Buy domain or create subdomain
   - Point DNS A record to `187.124.20.215`
   - Wait for DNS propagation (~10 minutes)

2. **Update SSL for new domain:**
   ```bash
   ssh root@187.124.20.215
   certbot certonly --standalone -d yourdomain.com
   systemctl restart nginx
   exit
   ```

3. **Your app is now live on real domain!**

---

## Troubleshooting

**"SSH: connection refused"**
→ Check credentials in deploy.py (password: `Extra01#1234`)

**"git: command not found on server"**
→ deploy.py installs it automatically

**"Database connection failed"**
→ Wait 30 seconds after migration completes, PostgreSQL may still be starting

**"Port 80/443 already in use"**
→ Hostinger firewall or existing service running. Deploy script handles this.

---

## Next Steps

- 🎉 App is live and authenticating users
- 📱 Phase 2: Implement guest app (music search, voting)
- 📊 Phase 3: Build DJ dashboard
- 🔄 Phase 4: Real-time WebSocket sync
- 💳 Phase 5: Add PayPal licensing

Each phase redeploys with: `git push origin main` (if auto-deploy set up) or run `python deploy.py` again.

