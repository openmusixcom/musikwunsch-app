# Automatisches Deployment-Tool

Dieses Tool automatisiert alle Deployments auf die Hostinger VPS und kann beliebig oft verwendet werden.

## Installation

### Voraussetzungen
- Python 3.7+
- `sshpass` für SSH-Passwort-Authentifizierung
- Git lokal installiert

### Setup (einmalig)

```bash
# Auf Windows/Mac/Linux:
pip install pexpect  # Optional, für bessere SSH-Handling

# sshpass installieren (falls nicht vorhanden):
# macOS:
brew install sshpass

# Linux (Debian/Ubuntu):
sudo apt-get install sshpass

# Windows (Git Bash):
# sshpass ist in Git Bash enthalten
```

## Verwendung

### Einfach: Mit deploy.sh
```bash
./deploy.sh
```

### Oder direkt mit Python
```bash
python3 auto_deploy.py
```

Das Tool wird dann:
1. ✅ Neuesten Code von GitHub pullen (lokal)
2. ✅ VPS vorbereiten
3. ✅ Code auf VPS deployen
4. ✅ Docker Images bauen
5. ✅ Container starten
6. ✅ Migrations ausführen
7. ✅ Health Check machen
8. ✅ Detailliertes Log erstellen

## Was das Tool automatisch macht

### Schritt 1: Code-Update (lokal)
- Holt neuesten Code von GitHub
- Prüft ob das Repo aktuell ist

### Schritt 2: VPS-Vorbereitung
- Erstellt Verzeichnis falls nötig
- Initialisiert Git Repo
- Setzt Git Remote auf GitHub

### Schritt 3: Code auf VPS
- Pullt neuesten Code
- Verifyifiert den Commit

### Schritt 4: Docker Setup
- Prüft ob Docker installiert ist
- Installiert Docker falls nötig
- Prüft ob Docker Compose installiert ist
- Installiert Docker Compose falls nötig

### Schritt 5: Deployment
- Stoppt alte Container
- Baut neue Docker Images (mit `--no-cache`)
- Startet neue Container
- Wartet auf Services

### Schritt 6: Konfiguration
- Führt Migrations aus
- Lädt Sample Songs in DB
- Verifyifiert dass alle Container laufen

### Schritt 7: Verifizierung
- Health Check der API
- Detailliertes Deployment-Log

## Output & Logs

Nach jedem Deploy wird ein Log-Datei erstellt:
```
deployment_20260529_021234.log
```

Diese enthält:
- Alle ausgeführten Befehle
- Output jedes Schritts
- Fehler und Warnings
- Erfolgs-/Fehler-Zusammenfassung
- Deployment-Dauer

### Log prüfen
```bash
# Neuestes Log anschauen
tail -f deployment_*.log

# Fehler suchen
grep ERROR deployment_*.log

# Erfolgs-Status
grep SUCCESS deployment_*.log
```

## Konfiguration

Das Tool ist in `auto_deploy.py` konfiguriert. Falls Sie Änderungen brauchen:

```python
CONFIG = {
    "vps_host": "187.124.20.215",           # VPS IP/Hostname
    "vps_user": "root",                     # SSH User
    "vps_password": "Extra01#1234",         # SSH Password
    "deploy_dir": "/var/www/musikwunsch-app-docker",  # Deploy-Verzeichnis
    "repo_url": "https://github.com/openmusixcom/musikwunsch-app.git",
    "repo_branch": "main",                  # Git Branch
    "api_health_url": "http://87.106.215.187.nip.io/api/health",
}
```

## Workflow für Updates

### Typischer Workflow:

1. **Code ändern und committen**
   ```bash
   git add .
   git commit -m "Fix: Login issue"
   ```

2. **Zu GitHub pushen**
   ```bash
   git push origin main
   ```

3. **Auf VPS deployen**
   ```bash
   python3 auto_deploy.py
   # oder
   ./deploy.sh
   ```

4. **Testen**
   ```bash
   curl http://87.106.215.187.nip.io/api/health
   ```

## Troubleshooting

### "sshpass: command not found"
```bash
# macOS
brew install sshpass

# Linux
sudo apt-get install sshpass

# Windows Git Bash - sollte funktionieren, eventuell:
# Mit Windows native Python (nicht Git Bash Python)
python auto_deploy.py
```

### "Command timed out"
Das bedeutet, dass Docker Images zu lange zu bauen dauern. Das ist normal beim ersten Mal (5-10 Minuten). Beim zweiten Mal geht es schneller.

### "Git not found" lokal
Stellen Sie sicher, dass Git installiert ist und im PATH ist:
```bash
git --version
```

### "Docker build failed on VPS"
Das Tool zeigt den Fehler im Log. Häufige Gründe:
- Package nicht installiert (wird meist vom Dockerfile fixed)
- Nicht genug Speicher auf VPS
- Netzwerkproblem beim Package-Download

Lösung: Log prüfen, Problem beheben, nochmal deployen.

### API gibt 301 Redirect
Das war das vorherige Problem. Wenn das noch passiert:
1. Prüfen: `curl http://87.106.215.187.nip.io/api/health`
2. Deploy nochmal: `python3 auto_deploy.py`
3. Falls weiter problem: `docker exec musikwunsch-web nginx -t` prüfen

## Automatisierung (Optional)

Sie können das Deployment auch automatisieren mit Cron:

```bash
# Alle Tage um 3 Uhr morgens deployen
crontab -e
# Hinzufügen:
0 3 * * * cd /path/to/musikwunsch && ./deploy.sh >> deployment_cron.log 2>&1
```

Oder mit GitHub Actions (würde weitere Konfiguration brauchen).

## Rollback

Falls ein Deployment fehlschlägt, können Sie zum vorherigen Commit zurückkehren:

```bash
ssh root@187.124.20.215
cd /var/www/musikwunsch-app-docker
git log --oneline | head -5          # Letzten Commits sehen
git reset --hard COMMIT_HASH         # Zu altem Commit zurück
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Häufig verwendete Befehle

```bash
# Nur deployen
python3 auto_deploy.py

# Container Status prüfen
ssh root@187.124.20.215 'docker-compose ps'

# Logs ansehen
ssh root@187.124.20.215 'docker-compose logs -f musikwunsch-api'

# Migrations manuell ausführen
ssh root@187.124.20.215 'cd /var/www/musikwunsch-app-docker && docker-compose exec -T musikwunsch-api npm run migrate'

# Datenbankinhalt prüfen
ssh root@187.124.20.215 'docker-compose exec -T musikwunsch-db psql -U postgres -d musikwunsch -c "SELECT COUNT(*) FROM users;"'
```

## Support

Falls das Deployment fehlschlägt:

1. **Log überprüfen**: `deployment_*.log` anschauen
2. **Manuell prüfen**: Mit SSH auf VPS gehen und Status prüfen
3. **Nochmal versuchen**: Oft funktioniert ein zweiter Deploy-Versuch
4. **Rollback**: Zu letztem bekannt guten Commit zurück

## Sicherheit

⚠️ **Wichtig:**
- Das Passwort ist in der `auto_deploy.py` hardcodiert (nur für diese VPS)
- Verwenden Sie für Production starke SSH-Keys statt Passwörter
- Für Public Repositories ist das OK, für privat sollten Sie SSH-Keys verwenden

Für bessere Sicherheit später:
```bash
# SSH-Key generieren
ssh-keygen -t ed25519 -f ~/.ssh/vps_key

# Auf VPS kopieren
ssh-copy-id -i ~/.ssh/vps_key.pub root@187.124.20.215

# Tool updaten um Keys zu verwenden statt Passwort
```

## Zusammenfassung

✅ **Dieses Tool erspart Ihnen:**
- Manuelle SSH-Befehle
- Fehler durch Copy-Paste
- Zeit beim Deployen
- Komplexe Fehlerbehandlung

✅ **Was es automatisiert:**
- Git-Synchronisation
- Docker-Setup
- Image Building
- Container Management
- Migrations
- Health Checks
- Detailliertes Logging

**Einfach nutzen:** `python3 auto_deploy.py`
