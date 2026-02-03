"""Embedding generation service using OpenAI."""

import logging
from typing import List, Dict, Any
import asyncio
import openai
from openai import OpenAI
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Handles embedding generation using OpenAI's embedding models."""
    
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.embedding_dimension = self._get_embedding_dimension()
        
    def _get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings for the current model."""
        model_dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536
        }
        return model_dimensions.get(self.model, 1536)
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            # Clean and prepare text
            cleaned_text = self._clean_text(text)
            
            if not cleaned_text:
                logger.warning("Empty text provided for embedding")
                return [0.0] * self.embedding_dimension
            
            response = self.client.embeddings.create(
                model=self.model,
                input=cleaned_text
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding with dimension: {len(embedding)}")
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process in each batch
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self._process_batch(batch)
            embeddings.extend(batch_embeddings)
            
            logger.info(f"Processed batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
        
        return embeddings
    
    def _process_batch(self, texts: List[str]) -> List[List[float]]:
        """Process a batch of texts for embedding generation."""
        try:
            # Clean all texts in the batch
            cleaned_texts = [self._clean_text(text) for text in texts]
            
            # Filter out empty texts but keep track of indices
            valid_texts = []
            valid_indices = []
            
            for idx, text in enumerate(cleaned_texts):
                if text:
                    valid_texts.append(text)
                    valid_indices.append(idx)
            
            if not valid_texts:
                logger.warning("No valid texts in batch")
                return [[0.0] * self.embedding_dimension] * len(texts)
            
            # Generate embeddings for valid texts
            response = self.client.embeddings.create(
                model=self.model,
                input=valid_texts
            )
            
            # Reconstruct full results with empty embeddings for invalid texts
            embeddings = []
            valid_iter = iter(response.data)
            
            for idx in range(len(texts)):
                if idx in valid_indices:
                    embeddings.append(next(valid_iter).embedding)
                else:
                    embeddings.append([0.0] * self.embedding_dimension)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to process batch: {e}")
            # Return zero embeddings for the entire batch
            return [[0.0] * self.embedding_dimension] * len(texts)
    
    def generate_embeddings_for_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for document chunks.
        
        Args:
            chunks: List of chunk dictionaries from document processor
            
        Returns:
            List of chunks with embeddings added
        """
        logger.info(f"Generating embeddings for {len(chunks)} chunks")
        
        # Extract texts from chunks
        texts = [chunk["text"] for chunk in chunks]
        
        # Generate embeddings in batches
        embeddings = self.generate_embeddings_batch(texts)
        
        # Add embeddings to chunks
        enriched_chunks = []
        for chunk, embedding in zip(chunks, embeddings):
            enriched_chunk = chunk.copy()
            enriched_chunk["embedding"] = embedding
            enriched_chunk["embedding_model"] = self.model
            enriched_chunk["embedding_dimension"] = len(embedding)
            enriched_chunks.append(enriched_chunk)
        
        logger.info(f"Successfully generated embeddings for {len(enriched_chunks)} chunks")
        return enriched_chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean and prepare text for embedding generation."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        cleaned = " ".join(text.split())
        
        # Truncate if too long (OpenAI has token limits)
        max_tokens = 8000  # Conservative limit for text-embedding models
        words = cleaned.split()
        
        if len(words) > max_tokens:
            cleaned = " ".join(words[:max_tokens])
            logger.warning(f"Text truncated to {max_tokens} words")
        
        return cleaned
    
    async def generate_embedding_async(self, text: str) -> List[float]:
        """
        Async version of embedding generation.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        # Run the synchronous method in a thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate_embedding, text)
    
    def cosine_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score between -1 and 1
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)