#!/usr/bin/env python3
"""
Deploy Phase 2 updates to Hostinger VPS and load sample songs
"""

import os
import sys
import subprocess
import json

# Configuration
VPS_HOST = "187.124.20.215"
VPS_USER = "root"
VPS_DIR = "/var/www/musikwunsch-app-docker"
GIT_URL = "https://github.com/cwoll/DJapp.git"

def run_command(cmd, cwd=None, shell=False):
    """Run a command and return output"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"

def main():
    print("🚀 Deploying Phase 2 to Hostinger VPS\n")

    # Step 1: Push to GitHub
    print("1️⃣  Pushing changes to GitHub...")
    code, stdout, stderr = run_command(["git", "push", "origin", "main"])
    if code != 0:
        print(f"❌ Git push failed: {stderr}")
        return False
    print("✅ Changes pushed to GitHub\n")

    # Step 2: Create SSH deployment script
    print("2️⃣  Creating SSH deployment script...")

    deploy_script = f"""#!/bin/bash
set -e

echo "Updating code from GitHub..."
cd {VPS_DIR}
git pull origin main

echo "Rebuilding Docker images..."
docker-compose build

echo "Restarting containers..."
docker-compose down
docker-compose up -d

echo "Waiting for containers to be ready..."
sleep 10

echo "Running migrations..."
docker exec musikwunsch-api npm run migrate

echo "✅ Phase 2 deployment complete!"
docker-compose ps
"""

    with open("deploy_phase2_vps.sh", "w") as f:
        f.write(deploy_script)

    print("✅ Deployment script created\n")

    # Step 3: Create sample songs loading script
    print("3️⃣  Creating sample songs loading script...")

    songs_script = """#!/bin/bash
docker exec musikwunsch-db psql -U musikwunsch -d musikwunsch << 'ENDSQL'
INSERT INTO songs (title, artist, album, duration, genre) VALUES
('Hello', 'Adele', '25', 295, 'Pop'),
('Shape of You', 'Ed Sheeran', '÷', 233, 'Pop'),
('Blinding Lights', 'The Weeknd', 'After Hours', 200, 'Synthwave'),
('As It Was', 'Harry Styles', 'Harry''s House', 167, 'Pop'),
('Like a Rolling Stone', 'Bob Dylan', 'Bringing It All Back Home', 369, 'Rock'),
('Imagine', 'John Lennon', 'Imagine', 183, 'Rock'),
('Bohemian Rhapsody', 'Queen', 'A Night at the Opera', 354, 'Rock'),
('Stairway to Heaven', 'Led Zeppelin', 'Led Zeppelin IV', 482, 'Rock'),
('Smells Like Teen Spirit', 'Nirvana', 'Nevermind', 301, 'Grunge'),
('Purple Haze', 'Jimi Hendrix', 'Are You Experienced', 175, 'Rock'),
('Sweet Home Chicago', 'Robert Johnson', 'King of the Delta Blues', 225, 'Blues'),
('All Along the Watchtower', 'Bob Dylan', 'John Wesley Harding', 231, 'Rock'),
('Layla', 'Eric Clapton', 'Layla and Other Assorted Love Songs', 390, 'Rock'),
('Black Magic Woman', 'Santana', 'Abraxas', 251, 'Latin Rock'),
('Smooth', 'Santana ft. Rob Thomas', 'Supernatural', 293, 'Latin Pop'),
('Yesterday', 'The Beatles', 'Help!', 123, 'Rock'),
('Let It Be', 'The Beatles', 'Let It Be', 243, 'Rock'),
('A Day in the Life', 'The Beatles', 'Sgt. Pepper''s', 327, 'Rock'),
('Strawberry Fields Forever', 'The Beatles', 'Strawberry Fields', 247, 'Rock'),
('Hallelujah', 'Leonard Cohen', 'Various Positions', 310, 'Rock');
ENDSQL
echo "✅ Sample songs loaded"
"""

    with open("load_sample_songs.sh", "w") as f:
        f.write(songs_script)

    print("✅ Sample songs script created\n")

    # Print instructions
    print("=" * 60)
    print("📋 DEPLOYMENT INSTRUCTIONS")
    print("=" * 60)
    print("""
1. SSH into the VPS and run the deployment script:
   ssh root@187.124.20.215
   cd /var/www/musikwunsch-app-docker
   bash deploy_phase2_vps.sh

2. Or use scp to transfer and run the script:
   scp deploy_phase2_vps.sh root@187.124.20.215:/tmp/
   ssh root@187.124.20.215 'bash /tmp/deploy_phase2_vps.sh'

3. After deployment, load sample songs:
   scp load_sample_songs.sh root@187.124.20.215:/tmp/
   ssh root@187.124.20.215 'bash /tmp/load_sample_songs.sh'

4. Test Phase 2 endpoints:
   See PHASE2_TESTING.md for detailed API testing instructions

5. Access the application:
   - Frontend: http://87.106.215.187.nip.io
   - Guest App: http://87.106.215.187.nip.io/guest
""")
    print("=" * 60)

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
