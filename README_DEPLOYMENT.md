# 🚀 Musikwunsch DJ App - Deployment Guide

Your Musikwunsch app is ready to deploy to Hostinger! Follow one of these paths:

## ⚡ Option 1: Automated Setup (Recommended - 3 minutes)

Everything in one script. Run this:

```bash
cd C:\Users\cwoll\Doku\Claude\DJapp
python setup_hostinger_git.py
python deploy.py
```

**What it does:**
1. ✅ Creates git repository on Hostinger
2. ✅ Configures local git remote
3. ✅ Pushes your code
4. ✅ Updates deploy.py with correct values
5. ✅ Deploys entire stack to Hostinger

**Time:** ~15 minutes total (5 min setup + 10 min deployment)

---

## 📋 Option 2: Manual Step-by-Step (5 minutes)

Follow the steps in [`DEPLOY_NOW.txt`](DEPLOY_NOW.txt) with copy/paste commands.

---

## 📚 Option 3: Detailed Guide (15 minutes)

Read [`DEPLOYMENT_CHECKLIST.md`](DEPLOYMENT_CHECKLIST.md) for:
- Multiple deployment approaches (GitHub, Hostinger git, etc.)
- Troubleshooting
- Domain configuration
- SSL setup
- Post-deployment verification

---

## 🎯 What You'll Get

After deployment, your app will be:

| Component | Location |
|-----------|----------|
| **Frontend** | `https://87.106.215.187.nip.io` |
| **Backend API** | `https://87.106.215.187.nip.io/api` |
| **Database** | PostgreSQL on 187.124.20.215 |
| **Process Manager** | PM2 (auto-restart on crash) |
| **Reverse Proxy** | Nginx with SSL/TLS |

---

## 🔐 Credentials

```
Server: 187.124.20.215
SSH User: root
SSH Password: Extra01#1234
```

⚠️ **Note:** Save these securely. Consider changing after initial setup.

---

## 🛑 Prerequisites

Before deploying, ensure you have:

- [ ] Python 3.6+ installed
- [ ] Git installed and configured
- [ ] SSH client (built-in on Windows 10+)
- [ ] This project directory

Check:
```bash
python --version
git --version
```

---

## ⏭️ What's Next After Deployment

### 1. **Create Admin Account** (2 min)

Once deployed, open the app in browser and register:
- Email: `admin@yourname.com`
- Password: `strong-password`
- Role: `admin`

You're now in the admin panel! 🎉

### 2. **Configure Real Domain** (Optional, 10 min)

For production use:

1. Buy domain from Hostinger control panel
2. Point DNS A record to `187.124.20.215`
3. Update `deploy.py` line 18:
   ```python
   DOMAIN = "yourdomain.com"
   ```
4. Re-run deployment:
   ```bash
   python deploy.py
   ```

### 3. **Next Development Phases**

The app currently has **Phase 1 (Authentication)** working. Next phases:

- **Phase 2:** Guest App (QR-code access, music search, voting)
- **Phase 3:** DJ Dashboard (request management, controls)
- **Phase 4:** Real-time Sync (WebSockets, notifications)
- **Phase 5:** PayPal Integration (license management)
- **Phase 6:** Security Hardening

Each phase redeploys using the same process.

---

## 🐛 Troubleshooting

### "SSH connection failed"
- Check password: `Extra01#1234`
- Verify IP: `187.124.20.215`
- Try: `ping 187.124.20.215`

### "Git repository not found"
- Ensure `setup_hostinger_git.py` ran successfully
- Check git remote: `git remote -v`

### "Deploy script stuck"
- Check internet connection
- Check Hostinger server status
- Ctrl+C to stop and review logs

### "Application won't start"
```bash
# SSH to server and check logs
ssh root@187.124.20.215
pm2 logs musikwunsch-api
systemctl status nginx
exit
```

### "Database migration failed"
- PostgreSQL might need more time to start
- Wait 30 seconds and re-run `python deploy.py`

---

## 📊 Project Files

```
musikwunsch-app/
├── deploy.py                    ← Main deployment script
├── setup_hostinger_git.py       ← Git setup automation
├── DEPLOY_NOW.txt              ← Quick copy/paste guide
├── DEPLOYMENT_CHECKLIST.md     ← Comprehensive checklist
├── QUICK_START_DEPLOY.md       ← Fast version
├── README_DEPLOYMENT.md        ← This file
├── SETUP_GUIDE.md              ← Local development setup
├── backend/
│   ├── package.json
│   ├── src/
│   │   ├── server.js           ← Express entry point
│   │   ├── config/
│   │   │   ├── database.js     ← PostgreSQL connection
│   │   │   └── auth.js         ← Auth utilities
│   │   ├── middleware/
│   │   │   └── auth.js         ← JWT verification
│   │   ├── controllers/
│   │   │   └── authController.js
│   │   ├── routes/
│   │   │   └── auth.js         ← Auth endpoints
│   │   └── migrations/
│   │       ├── 001_initial_schema.sql
│   │       └── run.js
│   └── .env                    ← Configuration
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   └── pages/
│   │       ├── LoginPage.jsx
│   │       ├── RegisterPage.jsx
│   │       ├── GuestApp.jsx    ← Phase 2
│   │       ├── DJDashboard.jsx ← Phase 3
│   │       └── AdminPanel.jsx  ← Phase 5
│   └── vite.config.js
└── README.md
```

---

## 📞 Support

If you encounter issues:

1. **Check logs:**
   ```bash
   ssh root@187.124.20.215
   pm2 logs musikwunsch-api
   tail -f /var/log/nginx/error.log
   ```

2. **Review error messages** in deployment output

3. **Check prerequisites** - Python, Git, SSH client

---

## 🎉 Ready to Deploy?

**Start here:**

```bash
cd C:\Users\cwoll\Doku\Claude\DJapp
python setup_hostinger_git.py
python deploy.py
```

Or follow [`DEPLOY_NOW.txt`](DEPLOY_NOW.txt) for manual steps.

**Your app will be live in 15 minutes!** 🚀

---

## 📖 Additional Resources

- **Comprehensive Deployment:** See [`DEPLOYMENT_CHECKLIST.md`](DEPLOYMENT_CHECKLIST.md)
- **Local Development:** See [`SETUP_GUIDE.md`](SETUP_GUIDE.md)
- **Technical Specification:** See `MUSIKWUNSCH_SPEZIFIKATION.docx`
- **Backend API:** See `backend/README.md` (if exists)
- **Frontend Guide:** See `frontend/README.md` (if exists)

---

**Let's ship this! 🎵**

