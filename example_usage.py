"""Example usage of the RAG pipeline for PDF processing and document search."""

import os
import logging
from pathlib import Path
from src.rag_pipeline import RAGPipeline, process_pdf_file, search_documents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main example demonstrating the RAG pipeline usage."""
    
    # Example 1: Using the convenience function
    print("=== Example 1: Using convenience function ===")
    
    # Make sure you have a PDF file to test with
    pdf_path = "sample_document.pdf"  # Replace with your PDF path
    
    if Path(pdf_path).exists():
        result = process_pdf_file(pdf_path)
        
        if result["success"]:
            print(f"✅ Successfully processed: {result['filename']}")
            print(f"📊 Statistics: {result['statistics']}")
        else:
            print(f"❌ Failed to process: {result['error']}")
    else:
        print(f"⚠️  PDF file not found: {pdf_path}")
    
    # Example 2: Using the full pipeline class
    print("\n=== Example 2: Using RAGPipeline class ===")
    
    # Initialize pipeline
    pipeline = RAGPipeline()
    
    if not pipeline.initialize():
        print("❌ Failed to initialize RAG pipeline")
        return
    
    print("✅ RAG pipeline initialized successfully")
    
    # Check pipeline status
    status = pipeline.get_pipeline_status()
    print(f"📋 Pipeline Status: {status}")
    
    # Example 3: Process PDF bytes (simulating file upload)
    print("\n=== Example 3: Processing PDF from bytes ===")
    
    if Path(pdf_path).exists():
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        result = pipeline.process_pdf_bytes(pdf_bytes, "uploaded_document.pdf")
        
        if result["success"]:
            print(f"✅ Successfully processed bytes: {result['filename']}")
            print(f"📊 Statistics: {result['statistics']}")
        else:
            print(f"❌ Failed to process bytes: {result['error']}")
    
    # Example 4: Search documents
    print("\n=== Example 4: Searching documents ===")
    
    search_queries = [
        "What is machine learning?",
        "How does artificial intelligence work?",
        "Explain neural networks",
        "What are the benefits of automation?"
    ]
    
    for query in search_queries:
        print(f"\n🔍 Query: '{query}'")
        results = pipeline.search_documents(query, top_k=3)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"  {i}. Score: {result['score']:.3f}")
                print(f"     Source: {result['source']} (Page {result['page']})")
                print(f"     Text: {result['text'][:200]}...")
                print()
        else:
            print("  No results found")


def test_individual_components():
    """Test individual components of the RAG pipeline."""
    
    print("=== Testing Individual Components ===")
    
    # Test 1: Document Processor
    print("\n1. Testing Document Processor...")
    from src.document_processor import DocumentProcessor
    
    processor = DocumentProcessor(chunk_size=256, chunk_overlap=25)
    
    # Test with a sample PDF (if available)
    pdf_path = "sample_document.pdf"
    if Path(pdf_path).exists():
        try:
            doc_data = processor.extract_text_from_pdf(pdf_path)
            print(f"   ✅ Extracted text from {doc_data['metadata']['total_pages']} pages")
            
            chunks = processor.split_text_into_chunks(doc_data)
            print(f"   ✅ Created {len(chunks)} chunks")
            
            if chunks:
                print(f"   📝 First chunk preview: {chunks[0]['text'][:100]}...")
        except Exception as e:
            print(f"   ❌ Document processing failed: {e}")
    else:
        print(f"   ⚠️  No PDF file found for testing: {pdf_path}")
    
    # Test 2: Embedding Service
    print("\n2. Testing Embedding Service...")
    from src.embedding_service import EmbeddingService
    from src.config import settings
    
    try:
        embedding_service = EmbeddingService(
            api_key=settings.openai_api_key,
            model=settings.openai_model
        )
        
        test_text = "This is a test sentence for embedding generation."
        embedding = embedding_service.generate_embedding(test_text)
        
        print(f"   ✅ Generated embedding with dimension: {len(embedding)}")
        print(f"   📊 Embedding preview: {embedding[:5]}...")
        
    except Exception as e:
        print(f"   ❌ Embedding generation failed: {e}")
    
    # Test 3: Endee Client
    print("\n3. Testing Endee Client...")
    from src.endee_client import EndeeClient
    
    try:
        client = EndeeClient(
            base_url=settings.endee_url,
            auth_token=settings.endee_auth_token
        )
        
        # Health check
        healthy = client.health_check_sync()
        print(f"   {'✅' if healthy else '❌'} Endee health check: {healthy}")
        
        if healthy:
            # List collections
            collections = client.list_collections_sync()
            print(f"   📋 Available collections: {collections}")
            
    except Exception as e:
        print(f"   ❌ Endee client test failed: {e}")


def create_sample_pdf():
    """Create a sample PDF for testing (requires reportlab)."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        filename = "sample_document.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        
        # Add some sample content
        c.drawString(100, 750, "Sample Document for RAG Testing")
        c.drawString(100, 720, "This is a sample PDF document created for testing the RAG pipeline.")
        c.drawString(100, 690, "")
        c.drawString(100, 660, "Machine Learning Overview:")
        c.drawString(100, 630, "Machine learning is a subset of artificial intelligence that enables")
        c.drawString(100, 600, "computers to learn and make decisions from data without being")
        c.drawString(100, 570, "explicitly programmed for every task.")
        c.drawString(100, 540, "")
        c.drawString(100, 510, "Neural Networks:")
        c.drawString(100, 480, "Neural networks are computing systems inspired by biological")
        c.drawString(100, 450, "neural networks. They consist of interconnected nodes that")
        c.drawString(100, 420, "process information and learn patterns from data.")
        
        c.showPage()
        
        # Second page
        c.drawString(100, 750, "Page 2: Applications of AI")
        c.drawString(100, 720, "Artificial intelligence has numerous applications including:")
        c.drawString(100, 690, "- Natural language processing")
        c.drawString(100, 660, "- Computer vision")
        c.drawString(100, 630, "- Robotics and automation")
        c.drawString(100, 600, "- Predictive analytics")
        c.drawString(100, 570, "- Recommendation systems")
        
        c.save()
        print(f"✅ Created sample PDF: {filename}")
        
    except ImportError:
        print("⚠️  reportlab not installed. Cannot create sample PDF.")
        print("   Install with: pip install reportlab")
    except Exception as e:
        print(f"❌ Failed to create sample PDF: {e}")


if __name__ == "__main__":
    # Check if we have required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set")
        print("   Please set your OpenAI API key in the .env file")
        exit(1)
    
    # Create a sample PDF if it doesn't exist
    if not Path("sample_document.pdf").exists():
        print("📄 Creating sample PDF for testing...")
        create_sample_pdf()
    
    # Run the main example
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Example failed: {e}")
    
    # Optionally run component tests
    print("\n" + "="*50)
    response = input("Run individual component tests? (y/n): ")
    if response.lower() == 'y':
        test_individual_components()