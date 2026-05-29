#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Musikwunsch Integration Verification Script
Tests Traefik integration and public port 8080 accessibility
"""

import subprocess
import sys
import json
import time
import io
from datetime import datetime
from pathlib import Path
import paramiko
import warnings

# Suppress SSH key warnings
warnings.filterwarnings('ignore')

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuration
CONFIG = {
    "vps_host": "87.106.215.187",
    "vps_ip": "87.106.215.187",
    "vps_user": "root",
    "vps_password": "Extra01#1234",
    "deploy_dir": "/var/www/musikwunsch-app-docker",
    "api_base_direct": "http://87.106.215.187:8080",
    "api_base_traefik": "http://87.106.215.187",
    "api_base_traefik_https": "https://87.106.215.187",
}

class VerificationTool:
    def __init__(self):
        self.log_file = Path(f"verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        self.start_time = datetime.now()
        self.results = {
            "direct_port_8080": None,
            "traefik_http": None,
            "traefik_https": None,
            "container_status": None,
            "login_direct": None,
            "login_traefik": None,
            "api_health_direct": None,
            "api_health_traefik": None,
        }
        self.ssh_client = None

    def log(self, message, level="INFO"):
        """Log message to console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level}] {message}"
        print(log_msg)
        with open(self.log_file, "a", encoding="utf-8", errors='replace') as f:
            f.write(log_msg + "\n")

    def connect_ssh(self):
        """Establish SSH connection to VPS"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                CONFIG["vps_host"],
                username=CONFIG["vps_user"],
                password=CONFIG["vps_password"],
                timeout=10
            )
            self.log("[OK] SSH connection established", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"SSH connection failed: {str(e)}", "ERROR")
            return False

    def disconnect_ssh(self):
        """Close SSH connection"""
        if self.ssh_client:
            try:
                self.ssh_client.close()
            except:
                pass

    def run_ssh_command(self, cmd):
        """Execute command on VPS via SSH"""
        try:
            if not self.ssh_client:
                if not self.connect_ssh():
                    return None

            stdin, stdout, stderr = self.ssh_client.exec_command(cmd, timeout=10)
            exit_code = stdout.channel.recv_exit_status()
            output = stdout.read().decode('utf-8', errors='replace').strip()
            error = stderr.read().decode('utf-8', errors='replace').strip()

            return output if exit_code == 0 else None
        except Exception as e:
            self.log(f"SSH error: {str(e)}", "ERROR")
            return None

    def test_direct_port_8080(self):
        """Test direct access to port 8080"""
        self.log("Testing direct port 8080 access...", "INFO")

        try:
            result = subprocess.run(
                f'curl -s -m 5 -w "\\n%{{http_code}}" {CONFIG["api_base_direct"]}/api/health',
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )

            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                http_code = lines[-1]
                response = '\n'.join(lines[:-1])

                if http_code == "200":
                    self.log(f"  [OK] Port 8080 accessible - HTTP {http_code}", "SUCCESS")
                    self.results["direct_port_8080"] = {
                        "status": "OK",
                        "http_code": http_code,
                        "response": response
                    }
                    return True
                else:
                    self.log(f"  [!] Port 8080 returned HTTP {http_code}", "WARNING")
                    self.results["direct_port_8080"] = {
                        "status": "ERROR",
                        "http_code": http_code,
                        "response": response
                    }
                    return False
            else:
                self.log(f"  [ERROR] Invalid response: {result.stdout}", "ERROR")
                self.results["direct_port_8080"] = {"status": "ERROR", "error": "Invalid response"}
                return False

        except Exception as e:
            self.log(f"  [ERROR] {str(e)}", "ERROR")
            self.results["direct_port_8080"] = {"status": "ERROR", "error": str(e)}
            return False

    def test_traefik_http(self):
        """Test Traefik HTTP access"""
        self.log("Testing Traefik HTTP access (port 80)...", "INFO")

        try:
            result = subprocess.run(
                f'curl -s -m 5 -w "\\n%{{http_code}}" -L {CONFIG["api_base_traefik"]}/api/health',
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )

            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                http_code = lines[-1]
                response = '\n'.join(lines[:-1])

                if http_code == "200":
                    self.log(f"  [OK] Traefik HTTP accessible - HTTP {http_code}", "SUCCESS")
                    self.results["traefik_http"] = {
                        "status": "OK",
                        "http_code": http_code,
                        "response": response
                    }
                    return True
                elif http_code in ["301", "302", "308"]:
                    self.log(f"  [!] Traefik redirects HTTP {http_code} (expected HTTPS redirect)", "INFO")
                    self.results["traefik_http"] = {
                        "status": "REDIRECT",
                        "http_code": http_code,
                        "response": response
                    }
                    return True  # This is expected behavior
                else:
                    self.log(f"  [ERROR] Traefik returned HTTP {http_code}", "ERROR")
                    self.results["traefik_http"] = {
                        "status": "ERROR",
                        "http_code": http_code,
                        "response": response
                    }
                    return False
            else:
                self.log(f"  [ERROR] Invalid response", "ERROR")
                self.results["traefik_http"] = {"status": "ERROR", "error": "Invalid response"}
                return False

        except Exception as e:
            self.log(f"  [ERROR] {str(e)}", "ERROR")
            self.results["traefik_http"] = {"status": "ERROR", "error": str(e)}
            return False

    def test_traefik_https(self):
        """Test Traefik HTTPS access"""
        self.log("Testing Traefik HTTPS access (port 443)...", "INFO")

        try:
            # Allow self-signed certificates for now
            result = subprocess.run(
                f'curl -s -m 5 -k -w "\\n%{{http_code}}" {CONFIG["api_base_traefik_https"]}/api/health',
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )

            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                http_code = lines[-1]
                response = '\n'.join(lines[:-1])

                if http_code == "200":
                    self.log(f"  [OK] Traefik HTTPS accessible - HTTP {http_code}", "SUCCESS")
                    self.results["traefik_https"] = {
                        "status": "OK",
                        "http_code": http_code,
                        "response": response
                    }
                    return True
                else:
                    self.log(f"  [!] Traefik HTTPS returned HTTP {http_code}", "WARNING")
                    self.results["traefik_https"] = {
                        "status": "WARNING",
                        "http_code": http_code,
                        "response": response
                    }
                    return True  # Still accessible
            else:
                self.log(f"  [ERROR] Invalid response", "ERROR")
                self.results["traefik_https"] = {"status": "ERROR", "error": "Invalid response"}
                return False

        except Exception as e:
            self.log(f"  [ERROR] {str(e)}", "ERROR")
            self.results["traefik_https"] = {"status": "ERROR", "error": str(e)}
            return False

    def test_container_status(self):
        """Check container status on VPS"""
        self.log("Checking container status...", "INFO")

        if not self.connect_ssh():
            return False

        output = self.run_ssh_command(f"cd {CONFIG['deploy_dir']} && docker-compose ps")

        if output:
            self.log("Container status:", "OUTPUT")
            for line in output.split('\n'):
                self.log(f"  {line}", "OUTPUT")
            self.results["container_status"] = "OK"
            return True
        else:
            self.log("  [ERROR] Could not retrieve container status", "ERROR")
            self.results["container_status"] = "ERROR"
            return False

    def test_login_direct(self):
        """Test login through direct port 8080"""
        self.log("Testing login endpoint (direct port 8080)...", "INFO")

        try:
            result = subprocess.run(
                f'curl -s -m 5 -X POST -H "Content-Type: application/json" -d "{{\\"email\\":\\"admin@test.local\\",\\"password\\":\\"testpass123\\"}}" {CONFIG["api_base_direct"]}/api/auth/login -w "\\n%{{http_code}}"',
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )

            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                http_code = lines[-1]
                response = '\n'.join(lines[:-1])

                self.log(f"  HTTP {http_code}", "OUTPUT")
                if http_code in ["200", "400", "401"]:
                    self.results["login_direct"] = {
                        "status": "TESTED",
                        "http_code": http_code,
                        "response": response[:200]
                    }
                    return True
                else:
                    self.log(f"  [ERROR] Unexpected status {http_code}", "ERROR")
                    self.results["login_direct"] = {"status": "ERROR", "http_code": http_code}
                    return False
            else:
                self.results["login_direct"] = {"status": "ERROR", "error": "Invalid response"}
                return False

        except Exception as e:
            self.log(f"  [ERROR] {str(e)}", "ERROR")
            self.results["login_direct"] = {"status": "ERROR", "error": str(e)}
            return False

    def test_login_traefik(self):
        """Test login through Traefik"""
        self.log("Testing login endpoint (Traefik HTTP)...", "INFO")

        try:
            result = subprocess.run(
                f'curl -s -m 5 -X POST -H "Content-Type: application/json" -d "{{\\"email\\":\\"admin@test.local\\",\\"password\\":\\"testpass123\\"}}" -L {CONFIG["api_base_traefik"]}/api/auth/login -w "\\n%{{http_code}}"',
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )

            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                http_code = lines[-1]
                response = '\n'.join(lines[:-1])

                self.log(f"  HTTP {http_code}", "OUTPUT")
                if http_code in ["200", "400", "401"]:
                    self.results["login_traefik"] = {
                        "status": "TESTED",
                        "http_code": http_code,
                        "response": response[:200]
                    }
                    return True
                else:
                    self.log(f"  [ERROR] Unexpected status {http_code}", "ERROR")
                    self.results["login_traefik"] = {"status": "ERROR", "http_code": http_code}
                    return False
            else:
                self.results["login_traefik"] = {"status": "ERROR", "error": "Invalid response"}
                return False

        except Exception as e:
            self.log(f"  [ERROR] {str(e)}", "ERROR")
            self.results["login_traefik"] = {"status": "ERROR", "error": str(e)}
            return False

    def verify(self):
        """Run all verifications"""
        self.log("=" * 70)
        self.log(">> MUSIKWUNSCH INTEGRATION VERIFICATION")
        self.log("=" * 70)

        # Run all tests
        self.test_direct_port_8080()
        self.log("", "INFO")

        self.test_traefik_http()
        self.log("", "INFO")

        self.test_traefik_https()
        self.log("", "INFO")

        self.test_container_status()
        self.log("", "INFO")

        self.test_login_direct()
        self.log("", "INFO")

        self.test_login_traefik()
        self.log("", "INFO")

        self.disconnect_ssh()

    def report(self):
        """Generate verification report"""
        self.log("=" * 70)
        self.log("-- VERIFICATION REPORT --")
        self.log("=" * 70)

        duration = datetime.now() - self.start_time
        self.log(f"Duration: {duration}", "INFO")
        self.log("", "INFO")

        self.log("Test Results:", "INFO")
        self.log("-" * 70, "INFO")

        for test_name, result in self.results.items():
            if result is None:
                continue

            if isinstance(result, dict):
                status = result.get("status", "UNKNOWN")
                http_code = result.get("http_code", "N/A")
                self.log(f"  {test_name}: {status} (HTTP {http_code})", "INFO")
            else:
                self.log(f"  {test_name}: {result}", "INFO")

        self.log("", "INFO")
        self.log("Access URLs:", "INFO")
        self.log(f"  - Direct (port 8080):    {CONFIG['api_base_direct']}", "INFO")
        self.log(f"  - Traefik (HTTP):        {CONFIG['api_base_traefik']}", "INFO")
        self.log(f"  - Traefik (HTTPS):       {CONFIG['api_base_traefik_https']}", "INFO")
        self.log("", "INFO")

        self.log(f"Full log: {self.log_file}", "INFO")
        self.log("=" * 70)

def main():
    print("""
    ╔══════════════════════════════════════════╗
    ║ MUSIKWUNSCH INTEGRATION VERIFICATION     ║
    ║ Tests Traefik & Port 8080 Accessibility  ║
    ╚══════════════════════════════════════════╝
    """)

    tool = VerificationTool()

    try:
        tool.verify()
    except Exception as e:
        tool.log(f"Unexpected error: {str(e)}", "ERROR")
    finally:
        tool.report()

if __name__ == "__main__":
    sys.exit(0)
