import requests
import json

# Test URLs for the Sign2Text application
BASE_URL = "http://localhost:5000"

def test_status():
    """Test the status endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/status")
        if response.status_code == 200:
            data = response.json()
            print("Status endpoint working!")
            print(f"   Language: {data.get('language', 'N/A')}")
            print(f"   Last gesture: {data.get('last_gesture', 'N/A')}")
            print(f"   Available languages: {data.get('available_languages', [])}")
        else:
            print(f"Status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"Status endpoint error: {e}")

def test_set_language():
    """Test language switching"""
    languages = ["english", "hindi"]

    for lang in languages:
        try:
            response = requests.post(
                f"{BASE_URL}/set_language",
                json={"language": lang},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"Language set to {lang}: {data}")
            else:
                print(f"Failed to set language to {lang}: {response.status_code}")
        except Exception as e:
            print(f"Language setting error for {lang}: {e}")

def test_main_page():
    """Test main page accessibility"""
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("Main page accessible!")
            print(f"   Content length: {len(response.text)} characters")
            if "Sign2Text" in response.text:
                print("   Contains expected content")
            else:
                print("   May not contain expected content")
        else:
            print(f"Main page failed: {response.status_code}")
    except Exception as e:
        print(f"Main page error: {e}")

def test_docs():
    """Test API documentation"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("API docs accessible!")
        else:
            print(f"API docs failed: {response.status_code}")
    except Exception as e:
        print(f"API docs error: {e}")

def main():
    print("Testing Sign2Text Application URLs")
    print("=" * 50)

    print(f"\nBase URL: {BASE_URL}")
    print("\nAvailable endpoints:")
    print("   GET  /              - Main web application")
    print("   GET  /video_feed    - Live video streaming")
    print("   GET  /status        - Application status")
    print("   GET  /docs          - API documentation")
    print("   POST /set_language  - Change language")

    print("\nRunning tests...")

    test_main_page()
    test_status()
    test_set_language()
    test_docs()

    print("\n" + "=" * 50)
    print("If tests fail, make sure the application is running:")
    print("   Docker: docker-compose up --build")
    print("   Local:  pip install flask opencv-python mediapipe tensorflow && python web_app.py")
    print(f"   Then visit: {BASE_URL}")

if __name__ == "__main__":
    main()