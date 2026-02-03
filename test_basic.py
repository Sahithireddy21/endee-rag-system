"""Basic test script to verify the setup without heavy dependencies."""

import os
import sys
from pathlib import Path

def test_environment():
    """Test basic environment setup."""
    print("🔍 Testing Environment Setup")
    print("=" * 40)
    
    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file exists")
        
        # Check for required environment variables
        with open(".env", "r") as f:
            content = f.read()
            
        required_vars = ["OPENAI_API_KEY", "ENDEE_URL"]
        for var in required_vars:
            if var in content:
                print(f"✅ {var} found in .env")
            else:
                print(f"⚠️  {var} not found in .env")
    else:
        print("❌ .env file not found")
    
    # Check project structure
    print("\n📁 Project Structure:")
    src_dir = Path("src")
    if src_dir.exists():
        print("✅ src/ directory exists")
        
        expected_files = [
            "src/__init__.py",
            "src/config.py", 
            "src/document_processor.py",
            "src/embedding_service.py",
            "src/endee_client.py",
            "src/rag_pipeline.py"
        ]
        
        for file_path in expected_files:
            if Path(file_path).exists():
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path}")
    else:
        print("❌ src/ directory not found")
    
    # Check Docker files
    docker_files = ["docker-compose.yml", "Dockerfile", "requirements.txt"]
    print("\n🐳 Docker Files:")
    for file_path in docker_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")

def test_imports():
    """Test basic Python imports."""
    print("\n📦 Testing Basic Imports:")
    
    basic_modules = [
        "os", "sys", "pathlib", "json", "uuid", "datetime"
    ]
    
    for module in basic_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")

def test_endee_connection():
    """Test connection to Endee (if running)."""
    print("\n🔗 Testing Endee Connection:")
    
    try:
        import urllib.request
        import json
        
        # Try to connect to Endee health endpoint
        url = "http://localhost:8080/health"
        
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                if response.status == 200:
                    print("✅ Endee is running and accessible")
                else:
                    print(f"⚠️  Endee responded with status: {response.status}")
        except Exception as e:
            print(f"❌ Cannot connect to Endee: {e}")
            print("   Make sure to run: docker-compose up endee")
            
    except ImportError:
        print("❌ Cannot test connection (urllib not available)")

def main():
    """Run all tests."""
    print("🚀 RAG Project Setup Test")
    print("=" * 50)
    
    test_environment()
    test_imports()
    test_endee_connection()
    
    print("\n" + "=" * 50)
    print("📋 Next Steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Start Endee: docker-compose up endee")
    print("3. Install dependencies: venv\\Scripts\\pip install -r requirements_minimal.txt")
    print("4. Run example: venv\\Scripts\\python example_usage.py")

if __name__ == "__main__":
    main()