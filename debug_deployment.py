#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug Deployment - Check server status
"""

import paramiko
import time
import sys
import io
import os

if os.name == 'nt':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HOST = "187.124.20.215"
PORT = 22
USERNAME = "root"
PASSWORD = "Extra01#1234"

def debug():
    print("🔍 Debugging Hostinger Server...\n")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, PORT, USERNAME, PASSWORD)

    commands = [
        ("pwd", "Current directory"),
        ("ls -la /var/repos/", "Git repos"),
        ("ls -la /var/www/", "Web directory"),
        ("git clone --help | head -5", "Git version"),
        ("ssh-keyscan localhost >> ~/.ssh/known_hosts 2>&1; echo 'SSH scan done'", "SSH keys"),
        ("GIT_SSH_COMMAND='ssh -o StrictHostKeyChecking=no' git clone ssh://root@127.0.0.1/var/repos/musikwunsch.git /tmp/test-clone 2>&1 | head -20", "Test clone"),
        ("ls -la /tmp/test-clone/ 2>&1 | head", "Clone test result"),
    ]

    for cmd, desc in commands:
        print(f"\n📌 {desc}")
        print(f"   $ {cmd}")
        stdin, stdout, stderr = client.exec_command(cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()

        # Show first 300 chars of output
        combined = (output + error)[:300]
        if combined:
            print(f"   {combined}")
        time.sleep(0.5)

    client.close()

if __name__ == "__main__":
    debug()
