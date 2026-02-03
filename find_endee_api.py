"""Find the actual Endee API endpoints."""

import urllib.request
import json

def test_api_path(base_url, path):
    """Test if a path returns JSON (API) instead of HTML."""
    url = f"{base_url}{path}"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            content_type = response.headers.get('Content-Type', '')
            content = response.read().decode()
            
            # Check if it's JSON
            if 'application/json' in content_type or content.strip().startswith('{'):
                try:
                    parsed = json.loads(content)
                    return True, parsed
                except:
                    pass
            
            # Check if it's not HTML
            if not content.strip().startswith('<!doctype html>') and not content.strip().startswith('<html'):
                return True, content
                
        return False, None
    except Exception as e:
        return False, str(e)

def main():
    """Find Endee API endpoints."""
    base_url = "http://localhost:8080"
    
    print("🔍 Finding Endee API Endpoints")
    print("=" * 50)
    
    # Try common API prefixes
    api_prefixes = [
        "/api",
        "/api/v1", 
        "/v1",
        "/rest",
        "/rest/v1"
    ]
    
    # Try common endpoints
    endpoints = [
        "/health",
        "/collections",
        "/indexes", 
        "/vectors",
        "/search"
    ]
    
    found_apis = []
    
    # Test root API paths
    for prefix in api_prefixes:
        print(f"\n🔍 Testing prefix: {prefix}")
        
        is_api, response = test_api_path(base_url, prefix)
        if is_api:
            print(f"   ✅ {prefix} -> API response")
            found_apis.append(prefix)
            if isinstance(response, dict):
                print(f"      {response}")
        else:
            print(f"   ❌ {prefix} -> HTML/Error")
        
        # Test endpoints under this prefix
        for endpoint in endpoints:
            full_path = f"{prefix}{endpoint}"
            is_api, response = test_api_path(base_url, full_path)
            if is_api:
                print(f"   ✅ {full_path} -> API response")
                found_apis.append(full_path)
                if isinstance(response, dict):
                    print(f"      {response}")
    
    # Also test direct endpoints (no prefix)
    print(f"\n🔍 Testing direct endpoints:")
    for endpoint in endpoints:
        is_api, response = test_api_path(base_url, endpoint)
        if is_api:
            print(f"   ✅ {endpoint} -> API response")
            found_apis.append(endpoint)
            if isinstance(response, dict):
                print(f"      {response}")
        else:
            print(f"   ❌ {endpoint} -> HTML/Error")
    
    # Try different ports
    print(f"\n🔍 Testing different ports:")
    for port in [8081, 8082, 9000, 3000]:
        test_url = f"http://localhost:{port}"
        try:
            with urllib.request.urlopen(f"{test_url}/health", timeout=2) as response:
                content_type = response.headers.get('Content-Type', '')
                if 'application/json' in content_type:
                    print(f"   ✅ Port {port} has JSON API")
                else:
                    print(f"   ⚠️  Port {port} responds but not JSON")
        except:
            print(f"   ❌ Port {port} not accessible")
    
    print(f"\n📋 Summary:")
    if found_apis:
        print(f"Found {len(found_apis)} API endpoints:")
        for api in found_apis:
            print(f"   {base_url}{api}")
    else:
        print("❌ No JSON API endpoints found")
        print("💡 Endee might be running in UI-only mode or use a different API structure")

if __name__ == "__main__":
    main()