"""Check what Endee endpoints actually return."""

import urllib.request
import json

def get_endpoint_response(url):
    """Get response from an endpoint."""
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            content = response.read().decode()
            print(f"📡 {url}")
            print(f"   Status: {response.status}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
            print(f"   Content: {content[:200]}{'...' if len(content) > 200 else ''}")
            print()
            return content
    except Exception as e:
        print(f"❌ {url}: {e}")
        return None

def main():
    """Check key Endee endpoints."""
    base_url = "http://localhost:8080"
    
    print("🔍 Checking Endee API Responses")
    print("=" * 50)
    
    # Check key endpoints
    endpoints = [
        "/",
        "/health", 
        "/info",
        "/collections",
        "/indexes"
    ]
    
    for endpoint in endpoints:
        get_endpoint_response(f"{base_url}{endpoint}")

if __name__ == "__main__":
    main()