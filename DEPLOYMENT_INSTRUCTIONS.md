# Musikwunsch Traefik Routing Fix - Deployment Instructions

## Overview
The previous Traefik configuration used catch-all routing rules (`PathPrefix('/')`) which conflicted with other services on the shared Traefik instance, causing HTTPS requests to fail with 404 errors.

**Solution**: Switched to hostname-based routing using `musikwunsch.87-106-215-187.nip.io`

## Changes Made
- ✅ Updated `docker-compose.yml` with hostname-based Traefik labels
- ✅ Added HTTP → HTTPS redirect middleware
- ✅ Committed to GitHub (commit: 3fcafd0)
- ✅ Pushed to GitHub main branch

## Deployment to VPS

### Option 1: Manual SSH (Recommended for Windows without sshpass)

**Step 1: SSH into the VPS**
```powershell
# Windows PowerShell - use any SSH client (PuTTY, Windows Terminal, etc.)
# Host: 87.106.215.187
# User: root
# Password: Extra01#1234
```

**Step 2: Pull latest code**
```bash
cd /var/www/musikwunsch-app-docker
git fetch origin main
git reset --hard origin/main
git log -1 --oneline  # Verify commit 3fcafd0 is deployed
```

**Step 3: Restart containers with new configuration**
```bash
docker-compose down
docker-compose up -d
```

**Step 4: Verify deployment**
```bash
sleep 15
docker-compose ps    # All containers should be Up
```

---

### Option 2: Automated Python Script

If you have `sshpass` installed:

```bash
python deploy_traefik_fix.py
```

On Windows, install sshpass:
1. Download: https://github.com/alebcay/sshpass/releases
2. Extract to `C:\Program Files\sshpass` or add to PATH
3. Run: `deploy_traefik_fix.py`

---

### Option 3: Manual via Web Shell (Hostinger)

If SSH is not available:
1. Log into Hostinger control panel
2. Find "Konsole" or "Web Shell" option for the VPS
3. Run the same commands as Option 1

---

## Verification Tests

After deployment, test the configuration using these commands:

### Test 1: HTTP → HTTPS Redirect
```bash
curl -i http://musikwunsch.87-106-215-187.nip.io/api/health
```

**Expected Output**:
```
HTTP/1.1 301 Moved Permanently
Location: https://musikwunsch.87-106-215-187.nip.io/api/health
```

---

### Test 2: HTTPS Health Check
```bash
curl -i https://musikwunsch.87-106-215-187.nip.io/api/health
```

**Expected Output** (after Let's Encrypt certificate is issued, 20-30 seconds after deployment):
```
HTTP/1.1 200 OK
Content-Type: application/json

{"status":"ok"}
```

⚠️ **Note**: First request may fail while Let's Encrypt certificate is being generated. Wait 20-30 seconds.

---

### Test 3: Login Endpoint
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"email":"admin@test.local","password":"testpass123"}' \
  https://musikwunsch.87-106-215-187.nip.io/api/auth/login
```

**Expected Output**:
```json
{
  "token": "eyJhbGc...",
  "user": {
    "id": "...",
    "email": "admin@test.local",
    "role": "admin"
  }
}
```

---

### Test 4: Frontend Access
```bash
curl -i https://musikwunsch.87-106-215-187.nip.io/
```

**Expected Output**:
```
HTTP/1.1 200 OK
Content-Type: text/html
```

---

### Test 5: Direct Port 8080 (If Firewall Allows)
```bash
curl -i http://87.106.215.187:8080/api/health
```

**Expected**: HTTP 200 OK (if firewall rules are configured)

If this times out, port 8080 is not accessible externally. Use the Traefik hostname instead.

---

## Troubleshooting

### Certificate Generation Delay
**Problem**: HTTPS returns `SSL certificate problem` for first 20-30 seconds

**Solution**: Wait 30 seconds for Let's Encrypt certificate generation, then retry

```bash
sleep 30
curl -i https://musikwunsch.87-106-215-187.nip.io/api/health
```

---

### Still Getting 404 on HTTPS
**Problem**: HTTPS returns 404 from nginx/1.29.3

**Possible Causes**:
1. Old containers still running (didn't stop properly)
2. Traefik labels not picked up
3. Docker daemon restart needed

**Solutions**:
```bash
# Force remove all containers and recreate
docker-compose down --remove-orphans
docker-compose up -d

# Or restart Docker daemon
systemctl restart docker
docker-compose up -d
```

---

### 301 Redirect Loop
**Problem**: curl gets redirected infinitely between HTTP and HTTPS

**Cause**: Middleware not applied correctly

**Solution**:
```bash
# Check current labels
docker inspect musikwunsch-web | grep traefik

# Should include: traefik.http.routers.musikwunsch-http.middlewares=redirect-https

# If missing, restart containers
docker-compose restart frontend
```

---

### Traefik not recognizing labels
**Problem**: Traefik logs don't show Musikwunsch services

**Solution**:
```bash
# Check Traefik logs
docker logs traefik --tail 50 | grep musikwunsch

# Force Docker to reload services
docker-compose down
docker network prune -f
docker-compose up -d
```

---

## Monitoring

### Check Traefik Dashboard
If Traefik has a web dashboard (usually port 8081):
```
http://87.106.215.187:8081
```

Look for:
- **Routers**: `musikwunsch-http` and `musikwunsch-https` listed
- **Services**: `musikwunsch` showing as "healthy" and routing to port 80
- **Certificates**: Let's Encrypt certificate for `musikwunsch.87-106-215-187.nip.io`

---

### View Container Logs
```bash
# Traefik logs
docker logs traefik --tail 50 -f

# Musikwunsch frontend logs
docker logs musikwunsch-web --tail 50 -f

# Musikwunsch API logs
docker logs musikwunsch-api --tail 50 -f
```

---

## Rollback Instructions

If the new configuration causes problems:

```bash
# Revert to previous commit
cd /var/www/musikwunsch-app-docker
git reset --hard 83eeaa5

# Restart containers with old configuration
docker-compose down
docker-compose up -d
```

---

## Summary

| Component | Status | URL |
|-----------|--------|-----|
| HTTP | ✅ Redirects to HTTPS | `http://musikwunsch.87-106-215-187.nip.io` |
| HTTPS | ✅ With Let's Encrypt | `https://musikwunsch.87-106-215-187.nip.io` |
| API Endpoints | ✅ Routed via Traefik | `https://musikwunsch.87-106-215-187.nip.io/api/*` |
| Direct Port 8080 | ⚠️ Firewall dependent | `http://87.106.215.187:8080` |
| Traefik Routing | ✅ Hostname-based (no conflicts) | Shared instance |

---

## Next Steps

1. ✅ Deploy to VPS (manually via SSH or using deployment script)
2. ✅ Wait 30 seconds for Let's Encrypt certificate
3. ✅ Run verification tests above
4. ✅ Access application at `https://musikwunsch.87-106-215-187.nip.io`
5. ✅ Test login with admin@test.local / testpass123
6. ✅ Test guest app via QR code functionality
