import httpx
import time
import json
import uuid

BASE_URL = "http://localhost:8000/api/v1"

def test_api():
    print("🚀 Starting Book Management API End-to-End Test...")
    print("-" * 50)
    
    unique_suffix = str(uuid.uuid4())[:8]
    email = f"test_{unique_suffix}@example.com"
    password = "password123"
    
    # 1. Register User
    print(f"\n1. Registering new user ({email})...")
    try:
        response = httpx.post(f"{BASE_URL}/auth/register", json={
            "email": email,
            "password": password,
            "full_name": "Test User",
            "is_active": True
        }, timeout=10.0)
        print(f"   Status: {response.status_code}")
        if response.status_code not in [200, 201]:
            print(f"   Response: {response.text}")
            return
        print("   ✅ User registered successfully!")
    except Exception as e:
        print(f"   ❌ Failed to register: {e}")
        return

    # 2. Login
    print("\n2. Logging in to get access token...")
    try:
        # FastAPI OAuth2PasswordRequestForm uses form data (application/x-www-form-urlencoded)
        response = httpx.post(f"{BASE_URL}/auth/login", data={
            "username": email,
            "password": password
        }, timeout=10.0)
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Response: {response.text}")
            return
        
        token = response.json()["access_token"]
        print("   ✅ Logged in successfully!")
    except Exception as e:
        print(f"   ❌ Failed to login: {e}")
        return
        
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create Book
    print("\n3. Creating a new book record...")
    
    # Generate a mathematically valid ISBN-13
    import random
    prefix = "978"
    middle = f"{random.randint(100000000, 999999999)}"
    partial_isbn = prefix + middle
    total = sum(int(digit) * (1 if i % 2 == 0 else 3) for i, digit in enumerate(partial_isbn))
    check_digit = (10 - (total % 10)) % 10
    valid_isbn = partial_isbn + str(check_digit)
    
    try:
        response = httpx.post(f"{BASE_URL}/books/", headers=headers, json={
            "title": f"The Science of Testing {unique_suffix}",
            "author": "John Tester",
            "isbn": valid_isbn,
            "published_year": 2026,
            "genre": "Science",
            "available": True
        }, timeout=10.0)
        print(f"   Status: {response.status_code}")
        if response.status_code not in [200, 201]:
            print(f"   Response: {response.text}")
            return
        print("   ✅ Book created successfully!")
    except Exception as e:
        print(f"   ❌ Failed to create book: {e}")
        return

    # 4. Test AI Assistant
    print("\n4. Testing AI Assistant (Query: 'Find available science books by John')...")
    try:
        # Give the DB a tiny moment to commit (just in case)
        time.sleep(0.5)
        
        response = httpx.post(f"{BASE_URL}/ai/assistant", json={
            "query": "Find available science books by John"
        }, timeout=30.0)
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Response: {response.text}")
            return
            
        print("   ✅ AI Response received:")
        print("   " + "-" * 40)
        print("   " + json.dumps(response.json(), indent=2).replace('\n', '\n   '))
        print("   " + "-" * 40)
    except Exception as e:
        print(f"   ❌ Failed to query AI: {e}")
        return

    print("\n🎉 All endpoints are working perfectly!")

if __name__ == "__main__":
    test_api()
