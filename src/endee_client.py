"""Endee vector database client for storing and retrieving embeddings."""

import logging
from typing import List, Dict, Any, Optional, Tuple
import httpx
import asyncio
import json
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class EndeeClient:
    """Client for interacting with Endee vector database."""
    
    def __init__(self, base_url: str = "http://localhost:8080", auth_token: Optional[str] = None):
        self.base_url = base_url.rstrip('/') + "/api/v1"
        self.auth_token = auth_token
        self.headers = self._build_headers()
        
    def _build_headers(self) -> Dict[str, str]:
        """Build HTTP headers for requests."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
            
        return headers
    
    async def health_check(self) -> bool:
        """
        Check if Endee database is healthy and accessible.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers=self.headers,
                    timeout=10.0
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def health_check_sync(self) -> bool:
        """Synchronous version of health check."""
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.base_url}/health",
                    headers=self.headers,
                    timeout=10.0
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def create_collection(self, collection_name: str, dimension: int) -> bool:
        """
        Create a new collection in Endee.
        
        Args:
            collection_name: Name of the collection
            dimension: Dimension of the vectors
            
        Returns:
            True if successful, False otherwise
        """
        try:
            payload = {
                "name": collection_name,
                "dimension": dimension,
                "metric": "cosine"  # Use cosine similarity
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/collections",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"Collection '{collection_name}' created successfully")
                    return True
                elif response.status_code == 409:
                    logger.info(f"Collection '{collection_name}' already exists")
                    return True
                else:
                    logger.error(f"Failed to create collection: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            return False
    
    def create_collection_sync(self, collection_name: str, dimension: int) -> bool:
        """Synchronous version of create_collection."""
        try:
            payload = {
                "name": collection_name,
                "dimension": dimension,
                "metric": "cosine"
            }
            
            with httpx.Client() as client:
                response = client.post(
                    f"{self.base_url}/collections",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"Collection '{collection_name}' created successfully")
                    return True
                elif response.status_code == 409:
                    logger.info(f"Collection '{collection_name}' already exists")
                    return True
                else:
                    logger.error(f"Failed to create collection: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            return False
    
    async def insert_vectors(self, collection_name: str, vectors_data: List[Dict[str, Any]]) -> bool:
        """
        Insert vectors with metadata into Endee collection.
        
        Args:
            collection_name: Name of the collection
            vectors_data: List of dictionaries containing vector data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare vectors for Endee format
            vectors = []
            for data in vectors_data:
                vector_entry = {
                    "id": data.get("id", str(uuid.uuid4())),
                    "vector": data["embedding"],
                    "metadata": data.get("metadata", {})
                }
                vectors.append(vector_entry)
            
            payload = {
                "vectors": vectors
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/collections/{collection_name}/vectors",
                    headers=self.headers,
                    json=payload,
                    timeout=60.0
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"Successfully inserted {len(vectors)} vectors into '{collection_name}'")
                    return True
                else:
                    logger.error(f"Failed to insert vectors: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error inserting vectors: {e}")
            return False
    
    def insert_vectors_sync(self, collection_name: str, vectors_data: List[Dict[str, Any]]) -> bool:
        """Synchronous version of insert_vectors."""
        try:
            vectors = []
            for data in vectors_data:
                vector_entry = {
                    "id": data.get("id", str(uuid.uuid4())),
                    "vector": data["embedding"],
                    "metadata": data.get("metadata", {})
                }
                vectors.append(vector_entry)
            
            payload = {
                "vectors": vectors
            }
            
            with httpx.Client() as client:
                response = client.post(
                    f"{self.base_url}/collections/{collection_name}/vectors",
                    headers=self.headers,
                    json=payload,
                    timeout=60.0
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"Successfully inserted {len(vectors)} vectors into '{collection_name}'")
                    return True
                else:
                    logger.error(f"Failed to insert vectors: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error inserting vectors: {e}")
            return False
    
    async def search_vectors(self, collection_name: str, query_vector: List[float], 
                           top_k: int = 5, threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in Endee collection.
        
        Args:
            collection_name: Name of the collection
            query_vector: Query vector for similarity search
            top_k: Number of top results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of similar vectors with metadata and scores
        """
        try:
            payload = {
                "vector": query_vector,
                "top_k": top_k,
                "threshold": threshold
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/collections/{collection_name}/search",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    results = response.json()
                    logger.info(f"Found {len(results.get('results', []))} similar vectors")
                    return results.get('results', [])
                else:
                    logger.error(f"Search failed: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            return []
    
    def search_vectors_sync(self, collection_name: str, query_vector: List[float], 
                          top_k: int = 5, threshold: float = 0.0) -> List[Dict[str, Any]]:
        """Synchronous version of search_vectors."""
        try:
            payload = {
                "vector": query_vector,
                "top_k": top_k,
                "threshold": threshold
            }
            
            with httpx.Client() as client:
                response = client.post(
                    f"{self.base_url}/collections/{collection_name}/search",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    results = response.json()
                    logger.info(f"Found {len(results.get('results', []))} similar vectors")
                    return results.get('results', [])
                else:
                    logger.error(f"Search failed: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            return []
    
    async def list_collections(self) -> List[str]:
        """
        List all collections in Endee.
        
        Returns:
            List of collection names
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/collections",
                    headers=self.headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    collections = response.json()
                    return [col.get('name', '') for col in collections.get('collections', [])]
                else:
                    logger.error(f"Failed to list collections: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []
    
    def list_collections_sync(self) -> List[str]:
        """Synchronous version of list_collections."""
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.base_url}/collections",
                    headers=self.headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    collections = response.json()
                    return [col.get('name', '') for col in collections.get('collections', [])]
                else:
                    logger.error(f"Failed to list collections: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []


class VectorStore:
    """High-level interface for vector storage operations."""
    
    def __init__(self, endee_client: EndeeClient, collection_name: str = "documents"):
        self.client = endee_client
        self.collection_name = collection_name
        self.initialized = False
    
    def initialize(self, embedding_dimension: int = 1536) -> bool:
        """
        Initialize the vector store with a collection.
        
        Args:
            embedding_dimension: Dimension of the embedding vectors
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if Endee is healthy
            if not self.client.health_check_sync():
                logger.error("Endee database is not accessible")
                return False
            
            # Create collection
            success = self.client.create_collection_sync(self.collection_name, embedding_dimension)
            if success:
                self.initialized = True
                logger.info(f"Vector store initialized with collection '{self.collection_name}'")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            return False
    
    def store_document_chunks(self, chunks_with_embeddings: List[Dict[str, Any]]) -> bool:
        """
        Store document chunks with embeddings in the vector database.
        
        Args:
            chunks_with_embeddings: List of chunks with embeddings from embedding service
            
        Returns:
            True if successful, False otherwise
        """
        if not self.initialized:
            logger.error("Vector store not initialized")
            return False
        
        try:
            # Prepare data for Endee
            vectors_data = []
            for chunk in chunks_with_embeddings:
                vector_data = {
                    "id": f"{chunk['metadata']['source']}_{chunk['chunk_id']}",
                    "embedding": chunk["embedding"],
                    "metadata": {
                        **chunk["metadata"],
                        "text": chunk["text"],
                        "created_at": datetime.utcnow().isoformat(),
                        "embedding_model": chunk.get("embedding_model", "unknown")
                    }
                }
                vectors_data.append(vector_data)
            
            # Insert vectors
            success = self.client.insert_vectors_sync(self.collection_name, vectors_data)
            
            if success:
                logger.info(f"Stored {len(vectors_data)} document chunks in vector database")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to store document chunks: {e}")
            return False
    
    def search_similar_chunks(self, query_embedding: List[float], 
                            top_k: int = 5, threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search for similar document chunks.
        
        Args:
            query_embedding: Query vector for similarity search
            top_k: Number of top results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of similar chunks with metadata and scores
        """
        if not self.initialized:
            logger.error("Vector store not initialized")
            return []
        
        try:
            results = self.client.search_vectors_sync(
                self.collection_name, query_embedding, top_k, threshold
            )
            
            # Format results for easier use
            formatted_results = []
            for result in results:
                formatted_result = {
                    "id": result.get("id"),
                    "score": result.get("score", 0.0),
                    "text": result.get("metadata", {}).get("text", ""),
                    "source": result.get("metadata", {}).get("source", ""),
                    "page": result.get("metadata", {}).get("page", 0),
                    "chunk_index": result.get("metadata", {}).get("chunk_index", 0),
                    "metadata": result.get("metadata", {})
                }
                formatted_results.append(formatted_result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search similar chunks: {e}")
            return []