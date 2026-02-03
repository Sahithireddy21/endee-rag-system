"""Working RAG demonstration with simulated components."""

import json
import os
import hashlib
from typing import List, Dict, Any
from pathlib import Path

class SimulatedEmbeddingService:
    """Simulated embedding service for demonstration."""
    
    def __init__(self):
        self.model = "simulated-embeddings"
        self.dimension = 384
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate a deterministic embedding based on text content."""
        # Create a hash-based embedding for consistency
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hash to numbers and normalize
        embedding = []
        for i in range(0, len(text_hash), 2):
            hex_pair = text_hash[i:i+2]
            value = int(hex_pair, 16) / 255.0  # Normalize to 0-1
            embedding.append(value)
        
        # Pad or truncate to desired dimension
        while len(embedding) < self.dimension:
            embedding.extend(embedding[:min(len(embedding), self.dimension - len(embedding))])
        
        return embedding[:self.dimension]
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)

class SimulatedVectorStore:
    """Simulated vector store for demonstration."""
    
    def __init__(self):
        self.vectors = []
        self.embedding_service = SimulatedEmbeddingService()
    
    def store_chunks(self, chunks: List[Dict[str, Any]]) -> bool:
        """Store document chunks with embeddings."""
        for chunk in chunks:
            if "embedding" not in chunk:
                chunk["embedding"] = self.embedding_service.generate_embedding(chunk["text"])
            
            self.vectors.append({
                "id": chunk.get("chunk_id", len(self.vectors)),
                "text": chunk["text"],
                "embedding": chunk["embedding"],
                "metadata": chunk.get("metadata", {})
            })
        
        print(f"✅ Stored {len(chunks)} chunks (total: {len(self.vectors)})")
        return True
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar chunks."""
        query_embedding = self.embedding_service.generate_embedding(query)
        
        results = []
        for vector in self.vectors:
            similarity = self.embedding_service.cosine_similarity(
                query_embedding, vector["embedding"]
            )
            
            results.append({
                "text": vector["text"],
                "similarity": similarity,
                "metadata": vector["metadata"]
            })
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

class DocumentProcessor:
    """Simple document processor."""
    
    def __init__(self, chunk_size: int = 200):
        self.chunk_size = chunk_size
    
    def process_text(self, text: str, source: str = "document.txt") -> List[Dict[str, Any]]:
        """Process text into chunks."""
        # Simple sentence-based chunking
        sentences = [s.strip() + "." for s in text.split('.') if s.strip()]
        
        chunks = []
        current_chunk = ""
        chunk_id = 0
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append({
                        "chunk_id": chunk_id,
                        "text": current_chunk.strip(),
                        "metadata": {
                            "source": source,
                            "chunk_index": chunk_id,
                            "word_count": len(current_chunk.split())
                        }
                    })
                    chunk_id += 1
                current_chunk = sentence
        
        # Add the last chunk
        if current_chunk:
            chunks.append({
                "chunk_id": chunk_id,
                "text": current_chunk.strip(),
                "metadata": {
                    "source": source,
                    "chunk_index": chunk_id,
                    "word_count": len(current_chunk.split())
                }
            })
        
        return chunks

class RAGSystem:
    """Complete RAG system demonstration."""
    
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.vector_store = SimulatedVectorStore()
        self.embedding_service = SimulatedEmbeddingService()
    
    def ingest_document(self, text: str, source: str = "document.txt") -> Dict[str, Any]:
        """Ingest a document into the RAG system."""
        print(f"📄 Processing document: {source}")
        
        # Process into chunks
        chunks = self.document_processor.process_text(text, source)
        print(f"   Created {len(chunks)} chunks")
        
        # Store in vector database
        success = self.vector_store.store_chunks(chunks)
        
        return {
            "success": success,
            "source": source,
            "chunks_created": len(chunks),
            "total_chunks": len(self.vector_store.vectors)
        }
    
    def ask_question(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        """Ask a question and get an answer with sources."""
        print(f"🔍 Question: {question}")
        
        # Search for relevant chunks
        results = self.vector_store.search(question, top_k)
        
        if not results:
            return {
                "question": question,
                "answer": "I don't have enough information to answer that question.",
                "sources": [],
                "confidence": 0.0
            }
        
        # Generate answer based on top results
        context_chunks = []
        for result in results:
            if result["similarity"] > 0.1:  # Minimum similarity threshold
                context_chunks.append(result["text"])
        
        if not context_chunks:
            answer = "I couldn't find relevant information to answer that question."
            confidence = 0.0
        else:
            # Simple answer generation (in real implementation, this would use an LLM)
            context = " ".join(context_chunks)
            answer = f"Based on the available information: {context[:300]}..."
            confidence = max(r["similarity"] for r in results)
        
        return {
            "question": question,
            "answer": answer,
            "sources": [
                {
                    "text": r["text"],
                    "similarity": r["similarity"],
                    "source": r["metadata"].get("source", "unknown")
                }
                for r in results
            ],
            "confidence": confidence
        }

def demo_rag_system():
    """Demonstrate the RAG system with sample documents."""
    print("🚀 RAG System Demonstration")
    print("=" * 60)
    
    # Initialize RAG system
    rag = RAGSystem()
    
    # Sample documents
    documents = {
        "machine_learning.txt": """
        Machine learning is a subset of artificial intelligence that enables computers to learn 
        and make decisions from data without being explicitly programmed for every task. 
        It involves algorithms that can identify patterns in data and make predictions or 
        decisions based on those patterns.
        
        There are three main types of machine learning: supervised learning, unsupervised learning, 
        and reinforcement learning. Supervised learning uses labeled training data to learn a 
        mapping from inputs to outputs. Unsupervised learning finds hidden patterns in data 
        without labeled examples. Reinforcement learning learns through interaction with an 
        environment using rewards and penalties.
        
        Neural networks are a key component of machine learning, inspired by the structure 
        and function of biological neural networks. Deep learning, which uses neural networks 
        with multiple layers, has achieved remarkable success in areas like image recognition, 
        natural language processing, and game playing.
        """,
        
        "ai_applications.txt": """
        Artificial intelligence has numerous practical applications across various industries. 
        In healthcare, AI helps with medical diagnosis, drug discovery, and personalized treatment 
        plans. Computer vision systems can analyze medical images to detect diseases like cancer 
        at early stages.
        
        In transportation, autonomous vehicles use AI for navigation, obstacle detection, and 
        decision-making. Natural language processing enables chatbots, language translation, 
        and voice assistants like Siri and Alexa.
        
        In finance, AI is used for fraud detection, algorithmic trading, and risk assessment. 
        Recommendation systems powered by machine learning help platforms like Netflix and 
        Amazon suggest content and products to users based on their preferences and behavior.
        
        AI also plays a crucial role in robotics, enabling robots to perform complex tasks 
        in manufacturing, exploration, and service industries.
        """,
        
        "data_science.txt": """
        Data science is an interdisciplinary field that combines statistics, computer science, 
        and domain expertise to extract insights from data. It involves collecting, cleaning, 
        analyzing, and interpreting large datasets to solve real-world problems.
        
        The data science process typically includes data collection, data preprocessing, 
        exploratory data analysis, feature engineering, model building, and model evaluation. 
        Data scientists use various tools and programming languages like Python, R, SQL, 
        and specialized libraries for data manipulation and analysis.
        
        Big data technologies like Hadoop and Spark enable processing of massive datasets 
        that traditional tools cannot handle. Data visualization tools help communicate 
        findings effectively to stakeholders and decision-makers.
        
        Predictive analytics uses historical data to forecast future trends and outcomes, 
        while prescriptive analytics recommends actions based on data-driven insights.
        """
    }
    
    # Ingest documents
    print("📚 Ingesting Documents...")
    for filename, content in documents.items():
        result = rag.ingest_document(content, filename)
        print(f"   {filename}: {result['chunks_created']} chunks")
    
    print(f"\n📊 Total chunks in system: {len(rag.vector_store.vectors)}")
    
    # Ask questions
    questions = [
        "What is machine learning?",
        "How is AI used in healthcare?",
        "What are neural networks?",
        "What tools do data scientists use?",
        "How does reinforcement learning work?",
        "What is computer vision used for?"
    ]
    
    print("\n🤖 Asking Questions...")
    print("=" * 60)
    
    for question in questions:
        print(f"\n❓ {question}")
        print("-" * 40)
        
        response = rag.ask_question(question)
        
        print(f"🎯 Answer: {response['answer']}")
        print(f"📊 Confidence: {response['confidence']:.3f}")
        
        if response['sources']:
            print("📚 Sources:")
            for i, source in enumerate(response['sources'][:2], 1):
                similarity = source['similarity']
                text = source['text'][:100] + "..." if len(source['text']) > 100 else source['text']
                source_file = source['source']
                print(f"   {i}. [{similarity:.3f}] {source_file}")
                print(f"      {text}")
        
        print()

def main():
    """Run the RAG demonstration."""
    demo_rag_system()
    
    print("🎉 RAG System Demo Complete!")
    print("\n✅ Demonstrated Features:")
    print("   • Document ingestion and chunking")
    print("   • Text embedding generation")
    print("   • Vector storage and indexing")
    print("   • Similarity search")
    print("   • Question answering with sources")
    print("   • Confidence scoring")
    
    print("\n🔧 Technical Implementation:")
    print("   • Simulated embeddings (hash-based)")
    print("   • In-memory vector storage")
    print("   • Cosine similarity search")
    print("   • Sentence-based text chunking")
    
    print("\n🚀 Next Steps for Production:")
    print("   • Replace with real OpenAI embeddings")
    print("   • Integrate with actual Endee API")
    print("   • Add LLM for answer generation")
    print("   • Implement PDF processing")
    print("   • Add FastAPI endpoints")

if __name__ == "__main__":
    main()