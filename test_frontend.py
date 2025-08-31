#!/usr/bin/env python3
"""
Test script to verify the LotusHealth frontend and API are working
"""

import requests
import time
import sys

def test_api_health():
    """Test the API health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ API Health Check: PASSED")
            return True
        else:
            print(f"❌ API Health Check: FAILED - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API Health Check: FAILED - {e}")
        return False

def test_frontend_access():
    """Test if the frontend is accessible"""
    try:
        response = requests.get("http://localhost/")
        if response.status_code == 200 and "LotusHealth" in response.text:
            print("✅ Frontend Access: PASSED")
            return True
        else:
            print(f"❌ Frontend Access: FAILED - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend Access: FAILED - {e}")
        return False

def test_api_process_note():
    """Test the process_note API endpoint"""
    try:
        test_data = {
            "session_id": "test_session_001",
            "note": "Patient presents with chest pain and shortness of breath."
        }
        
        response = requests.post("http://localhost:8000/process_note", json=test_data)
        if response.status_code == 200:
            print("✅ API Process Note: PASSED")
            return True
        else:
            print(f"❌ API Process Note: FAILED - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API Process Note: FAILED - {e}")
        return False

def main():
    print("🧪 Testing LotusHealth Frontend and API...")
    print("=" * 50)
    
    # Wait a bit for services to start
    print("⏳ Waiting for services to start...")
    time.sleep(5)
    
    tests = [
        ("API Health Check", test_api_health),
        ("Frontend Access", test_frontend_access),
        ("API Process Note", test_api_process_note)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        if test_func():
            passed += 1
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your LotusHealth system is working correctly.")
        print("\n🌐 Access your application:")
        print("   Frontend: http://localhost")
        print("   API: http://localhost:8000")
        print("   API Docs: http://localhost/docs")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
