#!/usr/bin/env python3

import subprocess
import json
import sys

# SSH credentials
HOST = '187.124.20.215'
USER = 'root'
PASSWORD = 'Extra01#1234'

# Test commands
commands = [
    # Check Docker containers
    "docker-compose -f /var/www/musikwunsch-app-docker/docker-compose.yml ps",
    # Check backend logs for errors
    "docker logs musikwunsch-api 2>&1 | tail -20",
    # Test health check
    "curl -s http://localhost:3000/api/health | head -50"
]

for cmd in commands:
    print(f"\n{'='*60}")
    print(f"Running: {cmd}")
    print(f"{'='*60}")
    
    full_cmd = f"sshpass -p '{PASSWORD}' ssh {USER}@{HOST} '{cmd}'"
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")

