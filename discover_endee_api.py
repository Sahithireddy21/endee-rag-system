"""Discover Endee API endpoints by testing common paths."""

import urllib.request
import json

def test_endpoint(base_url, path, method="GET", data=None):
    """Test an API endpoint."""
    url = f"{base_url}{path}"
    
    try:
        if method == "GET":
            with urllib.request.urlopen(url, timeout=5) as response:
                status = response.status
                try:
                    content = response.read().decode()
                    if content:
                        try:
                            parsed = json.loads(content)
                            return status, parsed
                        except:
                            return status, content
                    else:
                        return status, "Empty response"
                except:
                    return status, "Could not read response"
        else:
            # For POST requests
            req_data = json.dumps(data).encode('utf-8') if data else None
            req = urllib.request.Request(
                url, 
                data=req_data,
                headers={'Content-Type': 'application/json'} if req_data else {}
            )
            req.get_method = lambda: method
            
            with urllib.request.urlopen(req, timeout=5) as response:
                status = response.status
                content = response.read().decode()
                try:
                    parsed = json.loads(content)
                    return status, parsed
                except:
                    return status, content
                    
    except urllib.error.HTTPError as e:
        return e.code, f"HTTP Error: {e.reason}"
    except Exception as e:
        return None, f"Error: {e}"

def discover_api():
    """Discover Endee API endpoints."""
    base_url = "http://localhost:8080"
    
    print("🔍 Discovering Endee API Endpoints")
    print("=" * 50)
    
    # Common API paths to test
    test_paths = [
        "/",
        "/health",
        "/status", 
        "/info",
        "/api",
        "/v1",
        "/collections",
        "/indexes",
        "/index",
        "/vectors",
        "/search",
        "/api/collections",
        "/api/indexes", 
        "/api/v1/collections",
        "/v1/collections",
        "/v1/indexes"
    ]
    
    working_endpoints = []
    
    for path in test_paths:
        print(f"Testing {path}...", end=" ")
        status, response = test_endpoint(base_url, path)
        
        if status and status < 400:
            print(f"✅ {status}")
            working_endpoints.append((path, status, response))
            if isinstance(response, dict) or (isinstance(response, str) and len(response) < 200):
                print(f"   Response: {response}")
        elif status == 404:
            print(f"❌ 404")
        elif status == 405:
            print(f"⚠️  405 (Method not allowed - might need POST)")
        else:
            print(f"❌ {status}: {response}")
    
    print(f"\n📋 Working Endpoints ({len(working_endpoints)}):")
    for path, status, response in working_endpoints:
        print(f"   {path} -> {status}")
    
    # Test POST on promising endpoints
    print(f"\n🔄 Testing POST methods on promising endpoints...")
    
    post_candidates = ["/collections", "/indexes", "/api/collections", "/v1/collections"]
    
    for path in post_candidates:
        if any(p[0] == path for p in working_endpoints):
            continue  # Skip if GET already worked
            
        print(f"Testing POST {path}...", end=" ")
        
        # Try creating a test collection
        test_data = {
            "name": "test_collection",
            "dimension": 384,
            "metric": "cosine"
        }
        
        status, response = test_endpoint(base_url, path, "POST", test_data)
        
        if status and status < 400:
            print(f"✅ {status}")
            print(f"   Response: {response}")
        elif status == 404:
            print(f"❌ 404")
        elif status == 405:
            print(f"❌ 405")
        else:
            print(f"❌ {status}: {response}")

if __name__ == "__main__":
    discover_api()