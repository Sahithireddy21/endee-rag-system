"""Simple example without external dependencies."""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_imports():
    """Test if we can import our modules."""
    print("🧪 Testing Module Imports")
    print("=" * 40)
    
    try:
        from config import settings
        print("✅ Config module imported")
        print(f"   Endee URL: {settings.endee_url}")
        print(f"   OpenAI Model: {settings.openai_model}")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from document_processor import DocumentProcessor
        print("✅ Document processor imported")
        
        # Test basic functionality
        processor = DocumentProcessor()
        test_text = "This is a test document. It has multiple sentences. Each sentence will be processed."
        
        # Simulate document data structure
        doc_data = {
            "content": [{"page": 1, "text": test_text}],
            "metadata": {"source": "test.txt", "total_pages": 1, "extraction_method": "test"}
        }
        
        chunks = processor.split_text_into_chunks(doc_data)
        print(f"   Created {len(chunks)} chunks from test text")
        
    except Exception as e:
        print(f"❌ Document processor test failed: {e}")
        return False
    
    try:
        from endee_client import EndeeClient
        print("✅ Endee client imported")
        
        # Test connection (without making actual requests)
        client = EndeeClient()
        print(f"   Client configured for: {client.base_url}")
        
    except Exception as e:
        print(f"❌ Endee client test failed: {e}")
        return False
    
    return True

def test_document_processing():
    """Test document processing without external APIs."""
    print("\n📄 Testing Document Processing")
    print("=" * 40)
    
    try:
        from document_processor import DocumentProcessor
        
        processor = DocumentProcessor(chunk_size=100, chunk_overlap=20)
        
        # Sample text
        sample_text = """
        Artificial Intelligence and Machine Learning
        
        Artificial intelligence (AI) is a broad field of computer science focused on creating 
        systems that can perform tasks typically requiring human intelligence. Machine learning 
        is a subset of AI that enables computers to learn and improve from experience without 
        being explicitly programmed.
        
        Key applications include natural language processing, computer vision, robotics, and 
        predictive analytics. These technologies are transforming industries by enabling 
        automation and intelligent decision-making processes.
        """
        
        # Create document data structure
        doc_data = {
            "content": [{"page": 1, "text": sample_text}],
            "metadata": {
                "source": "ai_overview.txt",
                "total_pages": 1,
                "extraction_method": "text_input"
            }
        }
        
        # Process into chunks
        chunks = processor.split_text_into_chunks(doc_data)
        
        print(f"✅ Processed document into {len(chunks)} chunks")
        
        # Display chunks
        for i, chunk in enumerate(chunks):
            text_preview = chunk["text"][:80] + "..." if len(chunk["text"]) > 80 else chunk["text"]
            word_count = chunk["metadata"]["word_count"]
            print(f"   Chunk {i+1}: {word_count} words - {text_preview}")
        
        return True
        
    except Exception as e:
        print(f"❌ Document processing test failed: {e}")
        return False

def test_system_status():
    """Check overall system status."""
    print("\n🔍 System Status Check")
    print("=" * 40)
    
    # Check if Endee is running
    try:
        import urllib.request
        with urllib.request.urlopen("http://localhost:8080/api/v1/health", timeout=5) as response:
            if response.status == 200:
                print("✅ Endee database is running")
            else:
                print(f"⚠️  Endee responded with status: {response.status}")
    except Exception as e:
        print(f"❌ Endee not accessible: {e}")
        print("   Start with: docker-compose up endee")
    
    # Check environment file
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file exists")
        
        # Check for API key
        with open(".env", "r") as f:
            content = f.read()
            if "OPENAI_API_KEY=your-openai-api-key-here" in content:
                print("⚠️  OpenAI API key not set (using placeholder)")
            elif "OPENAI_API_KEY=" in content:
                print("✅ OpenAI API key configured")
            else:
                print("❌ OpenAI API key not found in .env")
    else:
        print("❌ .env file not found")
    
    # Check project structure
    required_files = [
        "src/config.py",
        "src/document_processor.py", 
        "src/endee_client.py",
        "src/rag_pipeline.py",
        "docker-compose.yml"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Missing {len(missing_files)} required files")
        return False
    else:
        print(f"\n✅ All required files present")
        return True

def main():
    """Run all tests."""
    print("🚀 RAG System Simple Test")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    if not imports_ok:
        print("\n❌ Import tests failed. Check your Python environment.")
        return
    
    # Test document processing
    processing_ok = test_document_processing()
    
    # Check system status
    system_ok = test_system_status()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    
    if imports_ok and processing_ok and system_ok:
        print("🎉 All tests passed! System is ready.")
        print("\n🚀 Next Steps:")
        print("1. Set your OpenAI API key in .env file")
        print("2. Run: venv\\Scripts\\python working_rag_demo.py")
        print("3. For full pipeline: venv\\Scripts\\python example_usage.py")
    else:
        print("⚠️  Some tests failed. Check the issues above.")
        
        if not imports_ok:
            print("   • Fix module import issues")
        if not processing_ok:
            print("   • Check document processing setup")
        if not system_ok:
            print("   • Ensure all required files are present")

if __name__ == "__main__":
    main()