"""Document processing utilities for PDF text extraction and chunking."""

import logging
from typing import List, Dict, Any
from pathlib import Path
import PyPDF2
import pdfplumber
from io import BytesIO

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles PDF text extraction and document chunking."""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text_from_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text from PDF file with metadata.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            # Try pdfplumber first (better for complex layouts)
            return self._extract_with_pdfplumber(file_path)
        except Exception as e:
            logger.warning(f"pdfplumber failed, trying PyPDF2: {e}")
            try:
                return self._extract_with_pypdf2(file_path)
            except Exception as e2:
                logger.error(f"Both PDF extraction methods failed: {e2}")
                raise ValueError(f"Could not extract text from PDF: {e2}")
    
    def _extract_with_pdfplumber(self, file_path: str) -> Dict[str, Any]:
        """Extract text using pdfplumber (preserves layout better)."""
        text_content = []
        metadata = {
            "source": Path(file_path).name,
            "total_pages": 0,
            "extraction_method": "pdfplumber"
        }
        
        with pdfplumber.open(file_path) as pdf:
            metadata["total_pages"] = len(pdf.pages)
            
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append({
                            "page": page_num,
                            "text": page_text.strip()
                        })
                except Exception as e:
                    logger.warning(f"Failed to extract page {page_num}: {e}")
                    continue
        
        return {
            "content": text_content,
            "metadata": metadata
        }
    
    def _extract_with_pypdf2(self, file_path: str) -> Dict[str, Any]:
        """Extract text using PyPDF2 (fallback method)."""
        text_content = []
        metadata = {
            "source": Path(file_path).name,
            "total_pages": 0,
            "extraction_method": "PyPDF2"
        }
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            metadata["total_pages"] = len(pdf_reader.pages)
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append({
                            "page": page_num,
                            "text": page_text.strip()
                        })
                except Exception as e:
                    logger.warning(f"Failed to extract page {page_num}: {e}")
                    continue
        
        return {
            "content": text_content,
            "metadata": metadata
        }
    
    def extract_text_from_bytes(self, pdf_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Extract text from PDF bytes (for uploaded files).
        
        Args:
            pdf_bytes: PDF file content as bytes
            filename: Original filename for metadata
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            # Try pdfplumber first
            return self._extract_bytes_with_pdfplumber(pdf_bytes, filename)
        except Exception as e:
            logger.warning(f"pdfplumber failed on bytes, trying PyPDF2: {e}")
            try:
                return self._extract_bytes_with_pypdf2(pdf_bytes, filename)
            except Exception as e2:
                logger.error(f"Both PDF extraction methods failed on bytes: {e2}")
                raise ValueError(f"Could not extract text from PDF bytes: {e2}")
    
    def _extract_bytes_with_pdfplumber(self, pdf_bytes: bytes, filename: str) -> Dict[str, Any]:
        """Extract text from bytes using pdfplumber."""
        text_content = []
        metadata = {
            "source": filename,
            "total_pages": 0,
            "extraction_method": "pdfplumber"
        }
        
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            metadata["total_pages"] = len(pdf.pages)
            
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append({
                            "page": page_num,
                            "text": page_text.strip()
                        })
                except Exception as e:
                    logger.warning(f"Failed to extract page {page_num}: {e}")
                    continue
        
        return {
            "content": text_content,
            "metadata": metadata
        }
    
    def _extract_bytes_with_pypdf2(self, pdf_bytes: bytes, filename: str) -> Dict[str, Any]:
        """Extract text from bytes using PyPDF2."""
        text_content = []
        metadata = {
            "source": filename,
            "total_pages": 0,
            "extraction_method": "PyPDF2"
        }
        
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        metadata["total_pages"] = len(pdf_reader.pages)
        
        for page_num, page in enumerate(pdf_reader.pages, 1):
            try:
                page_text = page.extract_text()
                if page_text:
                    text_content.append({
                        "page": page_num,
                        "text": page_text.strip()
                    })
            except Exception as e:
                logger.warning(f"Failed to extract page {page_num}: {e}")
                continue
        
        return {
            "content": text_content,
            "metadata": metadata
        }
    
    def split_text_into_chunks(self, document_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Split document text into overlapping chunks.
        
        Args:
            document_data: Document data from extract_text_from_pdf
            
        Returns:
            List of text chunks with metadata
        """
        chunks = []
        chunk_id = 0
        
        for page_data in document_data["content"]:
            page_text = page_data["text"]
            page_num = page_data["page"]
            
            # Split page text into sentences for better chunking
            sentences = self._split_into_sentences(page_text)
            
            current_chunk = ""
            current_sentences = []
            
            for sentence in sentences:
                # Check if adding this sentence would exceed chunk size
                test_chunk = current_chunk + " " + sentence if current_chunk else sentence
                
                if len(test_chunk.split()) <= self.chunk_size:
                    current_chunk = test_chunk
                    current_sentences.append(sentence)
                else:
                    # Save current chunk if it has content
                    if current_chunk:
                        chunks.append(self._create_chunk(
                            chunk_id, current_chunk, page_num, 
                            document_data["metadata"], current_sentences
                        ))
                        chunk_id += 1
                    
                    # Start new chunk with overlap
                    if self.chunk_overlap > 0 and current_sentences:
                        overlap_sentences = current_sentences[-self.chunk_overlap:]
                        current_chunk = " ".join(overlap_sentences) + " " + sentence
                        current_sentences = overlap_sentences + [sentence]
                    else:
                        current_chunk = sentence
                        current_sentences = [sentence]
            
            # Don't forget the last chunk
            if current_chunk:
                chunks.append(self._create_chunk(
                    chunk_id, current_chunk, page_num, 
                    document_data["metadata"], current_sentences
                ))
                chunk_id += 1
        
        logger.info(f"Split document into {len(chunks)} chunks")
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Simple sentence splitting (can be improved with NLTK/spaCy)."""
        import re
        
        # Basic sentence splitting on periods, exclamation marks, question marks
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:  # Filter very short fragments
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def _create_chunk(self, chunk_id: int, text: str, page_num: int, 
                     doc_metadata: Dict[str, Any], sentences: List[str]) -> Dict[str, Any]:
        """Create a chunk dictionary with metadata."""
        return {
            "chunk_id": chunk_id,
            "text": text.strip(),
            "metadata": {
                "source": doc_metadata["source"],
                "page": page_num,
                "chunk_index": chunk_id,
                "word_count": len(text.split()),
                "sentence_count": len(sentences),
                "extraction_method": doc_metadata["extraction_method"]
            }
        }