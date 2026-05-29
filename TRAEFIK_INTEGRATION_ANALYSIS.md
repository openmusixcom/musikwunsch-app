# Musikwunsch Traefik Integration Analysis

## Current Status

### Test Results

| Endpoint | Result | Details |
|----------|--------|---------|
| `http://87.106.215.187:8080/api/health` | ❌ TIMEOUT | Port 8080 not accessible externally (firewall blocked) |
| `http://87.106.215.187/api/health` | ➡️ 301 REDIRECT | Traefik redirects HTTP to HTTPS (working) |
| `https://87.106.215.187/api/health` | ❌ 404 | Nginx 404 error - routing issue |

## Problems Identified

### 1. Port 8080 Not Publicly Accessible
**Status**: ❌ NOT RESOLVED

The port 8080 mapping in docker-compose.yml is only accessible from localhost, not from external IPs.

**Current Configuration**:
```yaml
ports:
  - "8080:80"
```

**Issue**: This only exposes port 8080 on the host machine, but if there's a firewall or the Hostinger VPS environment blocks direct port access, it won't be accessible externally.

**Solution**: Either:
- Configure firewall rules at Hostinger to allow port 8080 inbound
- Or rely ONLY on Traefik (remove port mapping and use reverse proxy)

### 2. HTTPS Routing Failure
**Status**: ❌ NOT RESOLVED

Traefik is receiving HTTPS requests correctly (port 443 is open), but routing them incorrectly. The 404 response from nginx/1.29.3 indicates:
- Traefik forwards to Nginx
- Nginx doesn't have `/api` route configured for HTTPS

**Root Cause**: The Traefik labels use catch-all routing `PathPrefix('/')`, which may conflict with other services also using catch-all rules on the shared Traefik instance.

**Evidence**:
- HTTP 301 works: Traefik intercepts and redirects
- HTTPS 404: Traefik forwards to wrong backend (likely the default/catch-all service)

### 3. Potential Traefik Configuration Conflict
**Status**: ⚠️ INVESTIGATING

On a shared Traefik instance, multiple Docker services can't all use:
```yaml
- "traefik.http.routers.musikwunsch-https.rule=PathPrefix(`/`)"
```

This creates an ambiguous routing rule. If another project also uses `PathPrefix('/')`, Traefik can't determine which service should handle the request.

## Recommended Solutions

### Solution A: Hostname-Based Routing (RECOMMENDED)
Use a dedicated subdomain for Musikwunsch instead of catch-all path routing.

**Changes to docker-compose.yml**:
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.services.musikwunsch.loadbalancer.server.port=80"
  
  # HTTP router with hostname rule
  - "traefik.http.routers.musikwunsch-http.rule=Host(`musikwunsch.example.com`)"
  - "traefik.http.routers.musikwunsch-http.entrypoints=web"
  - "traefik.http.routers.musikwunsch-http.service=musikwunsch"
  
  # Redirect HTTP to HTTPS
  - "traefik.http.routers.musikwunsch-http.middlewares=redirect-https"
  - "traefik.http.middlewares.redirect-https.redirectscheme.scheme=https"
  
  # HTTPS router with hostname rule
  - "traefik.http.routers.musikwunsch-https.rule=Host(`musikwunsch.example.com`)"
  - "traefik.http.routers.musikwunsch-https.entrypoints=websecure"
  - "traefik.http.routers.musikwunsch-https.service=musikwunsch"
  - "traefik.http.routers.musikwunsch-https.tls=true"
  - "traefik.http.routers.musikwunsch-https.tls.certresolver=letsencrypt"
```

**Benefits**:
- No conflict with other services
- Each service can have its own hostname
- Clear routing rules
- Proper HTTPS support with Let's Encrypt

**Requires**: DNS entry for `musikwunsch.example.com` pointing to the Hostinger IP.

### Solution B: Path-Based Routing with Priority
Keep the catch-all approach but add a dedicated path prefix.

**Changes**:
```yaml
labels:
  - "traefik.http.routers.musikwunsch-https.rule=PathPrefix(`/musikwunsch`)"
  - "traefik.http.routers.musikwunsch-https.priority=100"
```

**Limitations**:
- Requires frontend URL changes (all API calls to `/musikwunsch/api`)
- More complex client-side changes
- Still requires priority values to resolve conflicts

### Solution C: Direct Port Mapping Only
Skip Traefik and use direct port mapping (current state).

**Requires**:
- Hostinger firewall rules allowing port 8080 inbound
- Users access via `http://87.106.215.187:8080`

**Status**: Currently not working (timeout suggests firewall blocks it).

## Immediate Action Items

### Priority 1: Verify Traefik is receiving requests properly
```bash
# SSH into VPS and check:
docker logs traefik --tail 50 | grep musikwunsch

# Should show request routing for Musikwunsch
```

### Priority 2: Check for routing conflicts
```bash
# Check what other services are registered with Traefik:
docker logs traefik --tail 100 | grep "rule="

# Look for multiple services using PathPrefix('/')
```

### Priority 3: Implement hostname-based routing
1. Choose a subdomain (e.g., `musikwunsch.87-106-215-187.nip.io`)
2. Update docker-compose.yml labels
3. Redeploy with `docker-compose down && docker-compose up -d`
4. Wait for Let's Encrypt certificate generation
5. Test with curl

### Priority 4: Configure Hostinger firewall (if using port 8080)
If insisting on port 8080 direct access:
1. Log into Hostinger control panel
2. Find firewall rules for the VPS
3. Add inbound rule: Allow port 8080/TCP from 0.0.0.0/0
4. Test with `curl http://87.106.215.187:8080/api/health`

## Current Status Summary

| Feature | Status | Blocker |
|---------|--------|---------|
| ✅ Traefik installed and running | YES | No |
| ✅ HTTP to HTTPS redirect | YES | No |
| ❌ HTTPS routing to Musikwunsch | NO | **Routing conflict** |
| ❌ Port 8080 external access | NO | **Firewall/config** |
| ⚠️ Hostname-based routing | NOT ATTEMPTED | Requires config change |

## Recommended Next Steps

1. **SSH to VPS** and check Traefik logs for routing errors
2. **Implement Solution A** (hostname-based routing) - this is the standard approach
3. **Configure DNS** for the chosen subdomain
4. **Redeploy** Musikwunsch with new labels
5. **Test** HTTPS access through the hostname

## Files to Modify

- `docker-compose.yml` - Update Traefik labels
- DNS configuration - Add hostname record (depends on DNS provider)

## Testing Commands

After implementing Solution A with `musikwunsch.87-106-215-187.nip.io`:

```bash
# Test HTTP redirect
curl -i http://musikwunsch.87-106-215-187.nip.io/api/health

# Test HTTPS (allow self-signed)
curl -i -k https://musikwunsch.87-106-215-187.nip.io/api/health

# Test login
curl -X POST -H "Content-Type: application/json" \
  -d '{"email":"admin@test.local","password":"testpass123"}' \
  https://musikwunsch.87-106-215-187.nip.io/api/auth/login
```
