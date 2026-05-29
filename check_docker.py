#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check if Docker is available on Hostinger
"""

import paramiko
import sys
import io
import os

if os.name == 'nt':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HOST = "187.124.20.215"
PORT = 22
USERNAME = "root"
PASSWORD = "Extra01#1234"

def check():
    print("🐳 Checking Docker availability...\n")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, PORT, USERNAME, PASSWORD)

    commands = [
        ("docker --version", "Docker"),
        ("docker-compose --version", "Docker Compose"),
        ("docker ps", "Docker running"),
    ]

    for cmd, desc in commands:
        print(f"🔍 Checking {desc}...")
        stdin, stdout, stderr = client.exec_command(cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()

        if output and "command not found" not in error.lower():
            print(f"   ✅ {output.strip()}\n")
        else:
            print(f"   ❌ Not installed\n")

    client.close()

if __name__ == "__main__":
    check()
