#!/usr/bin/env python3
"""
Test login functionality
"""

import requests
import json

# Configuration
API_BASE = "http://87.106.215.187.nip.io"

def test_health():
    """Test API health"""
    print("1️⃣  Testing API health...")
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_login(email, password):
    """Test login"""
    print(f"\n2️⃣  Testing login with {email}...")
    try:
        response = requests.post(
            f"{API_BASE}/api/auth/login",
            json={"email": email, "password": password},
            timeout=5,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False

def test_register(email, password, role):
    """Test registration"""
    print(f"\n3️⃣  Testing registration with {email}...")
    try:
        response = requests.post(
            f"{API_BASE}/api/auth/register",
            json={"email": email, "password": password, "role": role},
            timeout=5,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 201
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🔍 Testing Musikwunsch Login")
    print("=" * 60)

    # Test health
    if not test_health():
        print("\n❌ API is not responding. Check if containers are running on VPS.")
        return

    # Test login with existing admin
    test_login("admin@test.local", "testpass123")

    # Test login with existing dj
    test_login("dj@test.local", "testpass123")

    # Try to register new admin
    print("\n" + "=" * 60)
    print("Trying to register new test user...")
    print("=" * 60)

    test_register("testadmin@test.local", "testpass123", "admin")

    # Try login with new user
    test_login("testadmin@test.local", "testpass123")

    print("\n" + "=" * 60)
    print("✅ Testing complete")
    print("=" * 60)

if __name__ == "__main__":
    main()
