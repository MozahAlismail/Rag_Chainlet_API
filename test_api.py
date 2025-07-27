import requests
import json

def test_api():
    print("🧪 Testing RAG API...")
    
    # Test health check
    print("\n1. Testing health check endpoint...")
    try:
        response = requests.get("http://localhost:8000/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test chat endpoint with new format
    print("\n2. Testing chat endpoint (new format)...")
    try:
        response = requests.post(
            "http://localhost:8000/chat",
            json={"question": "What is AI governance?"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Chat endpoint failed: {e}")
    
    # Test legacy chat endpoint
    print("\n3. Testing legacy chat endpoint...")
    try:
        response = requests.post(
            "http://localhost:8000/chat-legacy",
            json={"question": "What is AI governance?"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Legacy chat endpoint failed: {e}")

if __name__ == "__main__":
    test_api()
