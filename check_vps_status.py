#!/usr/bin/env python3

import subprocess
import os

# Set up SSH options to avoid key checking
ssh_options = [
    '-o', 'StrictHostKeyChecking=no',
    '-o', 'UserKnownHostsFile=/dev/null',
    '-o', 'ConnectTimeout=5'
]

commands = [
    "docker ps",
    "docker logs musikwunsch-api 2>&1 | tail -30",
]

HOST = "187.124.20.215"
USER = "root"

# Try using expect or a script approach
script = """#!/bin/bash
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@187.124.20.215 << 'ENDSSH'
docker ps
echo "---"
docker logs musikwunsch-api 2>&1 | tail -20
ENDSSH
"""

with open('ssh_test.sh', 'w') as f:
    f.write(script)

os.chmod('ssh_test.sh', 0o755)
result = subprocess.run(['bash', 'ssh_test.sh'], capture_output=True, text=True, timeout=15)
print(result.stdout)
if result.stderr:
    print(f"STDERR: {result.stderr}")

