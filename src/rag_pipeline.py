"""Main RAG pipeline that orchestrates document processing, embedding, and storage."""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import uuid
from datetime import datetime

from .config import settings
from .document_processor import DocumentProcessor
from .embedding_service import EmbeddingService
from .endee_client import EndeeClient, VectorStore

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Main pipeline for RAG document processing and storage."""
    
    def __init__(self):
        """Initialize the RAG pipeline with all components."""
        self.document_processor = DocumentProcessor(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
        
        self.embedding_service = EmbeddingService(
            api_key=settings.openai_api_key,
            model=settings.openai_model
        )
        
        self.endee_client = EndeeClient(
            base_url=settings.endee_url,
            auth_token=settings.endee_auth_token
        )
        
        self.vector_store = VectorStore(
            endee_client=self.endee_client,
            collection_name="documents"
        )
        
        self.initialized = False
    
    def initialize(self) -> bool:
        """
        Initialize the RAG pipeline.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Initializing RAG pipeline...")
            
            # Initialize vector store
            embedding_dim = self.embedding_service.embedding_dimension
            success = self.vector_store.initialize(embedding_dim)
            
            if success:
                self.initialized = True
                logger.info("RAG pipeline initialized successfully")
            else:
                logger.error("Failed to initialize vector store")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG pipeline: {e}")
            return False
    
    def process_pdf_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process a PDF file through the complete RAG pipeline.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary with processing results and metadata
        """
        if not self.initialized:
            raise RuntimeError("RAG pipeline not initialized. Call initialize() first.")
        
        try:
            logger.info(f"Processing PDF file: {file_path}")
            
            # Step 1: Extract text from PDF
            logger.info("Step 1: Extracting text from PDF...")
            document_data = self.document_processor.extract_text_from_pdf(file_path)
            
            if not document_data["content"]:
                raise ValueError("No text content extracted from PDF")
            
            # Step 2: Split into chunks
            logger.info("Step 2: Splitting text into chunks...")
            chunks = self.document_processor.split_text_into_chunks(document_data)
            
            if not chunks:
                raise ValueError("No chunks created from document")
            
            # Step 3: Generate embeddings
            logger.info("Step 3: Generating embeddings...")
            chunks_with_embeddings = self.embedding_service.generate_embeddings_for_chunks(chunks)
            
            # Step 4: Store in vector database
            logger.info("Step 4: Storing in vector database...")
            storage_success = self.vector_store.store_document_chunks(chunks_with_embeddings)
            
            if not storage_success:
                raise RuntimeError("Failed to store chunks in vector database")
            
            # Prepare result
            result = {
                "success": True,
                "document_id": str(uuid.uuid4()),
                "file_path": file_path,
                "filename": Path(file_path).name,
                "processed_at": datetime.utcnow().isoformat(),
                "statistics": {
                    "total_pages": document_data["metadata"]["total_pages"],
                    "total_chunks": len(chunks),
                    "extraction_method": document_data["metadata"]["extraction_method"],
                    "embedding_model": self.embedding_service.model,
                    "embedding_dimension": self.embedding_service.embedding_dimension
                },
                "chunks_stored": len(chunks_with_embeddings)
            }
            
            logger.info(f"Successfully processed PDF: {result['statistics']}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process PDF file: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path,
                "processed_at": datetime.utcnow().isoformat()
            }
    
    def process_pdf_bytes(self, pdf_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Process PDF from bytes (for uploaded files).
        
        Args:
            pdf_bytes: PDF file content as bytes
            filename: Original filename
            
        Returns:
            Dictionary with processing results and metadata
        """
        if not self.initialized:
            raise RuntimeError("RAG pipeline not initialized. Call initialize() first.")
        
        try:
            logger.info(f"Processing PDF bytes: {filename}")
            
            # Step 1: Extract text from PDF bytes
            logger.info("Step 1: Extracting text from PDF bytes...")
            document_data = self.document_processor.extract_text_from_bytes(pdf_bytes, filename)
            
            if not document_data["content"]:
                raise ValueError("No text content extracted from PDF")
            
            # Step 2: Split into chunks
            logger.info("Step 2: Splitting text into chunks...")
            chunks = self.document_processor.split_text_into_chunks(document_data)
            
            if not chunks:
                raise ValueError("No chunks created from document")
            
            # Step 3: Generate embeddings
            logger.info("Step 3: Generating embeddings...")
            chunks_with_embeddings = self.embedding_service.generate_embeddings_for_chunks(chunks)
            
            # Step 4: Store in vector database
            logger.info("Step 4: Storing in vector database...")
            storage_success = self.vector_store.store_document_chunks(chunks_with_embeddings)
            
            if not storage_success:
                raise RuntimeError("Failed to store chunks in vector database")
            
            # Prepare result
            result = {
                "success": True,
                "document_id": str(uuid.uuid4()),
                "filename": filename,
                "processed_at": datetime.utcnow().isoformat(),
                "statistics": {
                    "total_pages": document_data["metadata"]["total_pages"],
                    "total_chunks": len(chunks),
                    "extraction_method": document_data["metadata"]["extraction_method"],
                    "embedding_model": self.embedding_service.model,
                    "embedding_dimension": self.embedding_service.embedding_dimension
                },
                "chunks_stored": len(chunks_with_embeddings)
            }
            
            logger.info(f"Successfully processed PDF bytes: {result['statistics']}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process PDF bytes: {e}")
            return {
                "success": False,
                "error": str(e),
                "filename": filename,
                "processed_at": datetime.utcnow().isoformat()
            }
    
    def search_documents(self, query: str, top_k: int = 5, threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search for relevant document chunks based on a query.
        
        Args:
            query: Search query text
            top_k: Number of top results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of relevant document chunks with metadata
        """
        if not self.initialized:
            raise RuntimeError("RAG pipeline not initialized. Call initialize() first.")
        
        try:
            logger.info(f"Searching documents for query: '{query[:100]}...'")
            
            # Generate embedding for the query
            query_embedding = self.embedding_service.generate_embedding(query)
            
            # Search similar chunks
            results = self.vector_store.search_similar_chunks(
                query_embedding, top_k, threshold
            )
            
            logger.info(f"Found {len(results)} relevant chunks")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            return []
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """
        Get the current status of the RAG pipeline.
        
        Returns:
            Dictionary with pipeline status information
        """
        try:
            endee_healthy = self.endee_client.health_check_sync()
            
            status = {
                "initialized": self.initialized,
                "endee_healthy": endee_healthy,
                "endee_url": settings.endee_url,
                "embedding_model": settings.openai_model,
                "chunk_size": settings.chunk_size,
                "chunk_overlap": settings.chunk_overlap,
                "collection_name": self.vector_store.collection_name
            }
            
            if endee_healthy:
                collections = self.endee_client.list_collections_sync()
                status["available_collections"] = collections
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get pipeline status: {e}")
            return {
                "initialized": False,
                "error": str(e)
            }


# Convenience functions for direct usage
def process_pdf_file(file_path: str) -> Dict[str, Any]:
    """
    Convenience function to process a PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Processing results
    """
    pipeline = RAGPipeline()
    
    if not pipeline.initialize():
        return {
            "success": False,
            "error": "Failed to initialize RAG pipeline"
        }
    
    return pipeline.process_pdf_file(file_path)


def search_documents(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Convenience function to search documents.
    
    Args:
        query: Search query
        top_k: Number of results to return
        
    Returns:
        Search results
    """
    pipeline = RAGPipeline()
    
    if not pipeline.initialize():
        return []
    
    return pipeline.search_documents(query, top_k)