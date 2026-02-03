# System Design Document

## Architecture Overview

The RAG-based Document QA system follows a microservices architecture with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client/UI     │    │   FastAPI       │    │   Endee Vector  │
│                 │◄──►│   Backend       │◄──►│   Database      │
│   (Web/API)     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   LLM Service   │
                       │  (OpenAI/Local) │
                       └─────────────────┘
```

## Component Design

### 1. Document Processing Service
**Responsibility**: Handle document ingestion and preprocessing

**Components**:
- `DocumentProcessor`: Main orchestrator
- `PDFExtractor`: Extract text from PDF files
- `TextSplitter`: Split documents into chunks
- `EmbeddingGenerator`: Generate vector embeddings

**Flow**:
1. Receive uploaded document
2. Extract text content
3. Split into overlapping chunks (512 tokens)
4. Generate embeddings for each chunk
5. Store in Endee with metadata

### 2. Vector Storage Service
**Responsibility**: Manage vector operations with Endee

**Components**:
- `EndeeClient`: Wrapper for Endee operations
- `VectorStore`: High-level vector operations
- `MetadataManager`: Handle document metadata

**Operations**:
- Store vectors with metadata
- Similarity search
- Vector retrieval
- Index management

### 3. Question Answering Service
**Responsibility**: Process questions and generate answers

**Components**:
- `QuestionProcessor`: Parse and validate questions
- `RetrievalEngine`: Find relevant document chunks
- `AnswerGenerator`: Generate contextual answers
- `ResponseFormatter`: Structure API responses

**Flow**:
1. Receive user question
2. Generate question embedding
3. Search similar vectors in Endee
4. Retrieve top-k relevant chunks
5. Construct prompt with context
6. Generate answer using LLM
7. Return structured response

### 4. API Layer
**Responsibility**: Expose HTTP endpoints

**Endpoints**:
```
POST /documents/upload     - Upload and process documents
GET  /documents           - List processed documents
POST /questions/ask       - Ask questions about documents
GET  /health             - Health check
GET  /docs               - API documentation
```

## Data Models

### Document Chunk
```python
{
    "id": "uuid",
    "document_id": "uuid", 
    "content": "text content",
    "embedding": [float],
    "metadata": {
        "source": "filename",
        "page": int,
        "chunk_index": int,
        "created_at": "timestamp"
    }
}
```

### Question Response
```python
{
    "question": "user question",
    "answer": "generated answer",
    "sources": [
        {
            "document": "filename",
            "page": int,
            "content": "relevant chunk",
            "similarity": float
        }
    ],
    "confidence": float,
    "processing_time": float
}
```

## Technology Integration

### Endee Vector Database
- **Connection**: HTTP client to Endee API
- **Index Strategy**: Single index for all document embeddings
- **Search Method**: Cosine similarity
- **Metadata Storage**: Document source, page numbers, timestamps

### Embedding Strategy
- **Model**: sentence-transformers/all-MiniLM-L6-v2 (default)
- **Dimension**: 384 (configurable)
- **Chunking**: 512 tokens with 50 token overlap
- **Normalization**: L2 normalization for cosine similarity

### LLM Integration
- **Primary**: OpenAI GPT-3.5-turbo
- **Fallback**: Local Ollama model
- **Prompt Template**: System + context + question format
- **Response Parsing**: Extract answer and confidence

## Deployment Architecture

### Docker Composition
```yaml
services:
  endee:
    image: endee/endee:latest
    ports: ["8080:8080"]
    
  rag-api:
    build: .
    ports: ["8000:8000"]
    depends_on: [endee]
    environment:
      - ENDEE_URL=http://endee:8080
      - OPENAI_API_KEY=${OPENAI_API_KEY}
```

### Configuration Management
- Environment variables for API keys
- Config files for model parameters
- Docker secrets for sensitive data
- Health checks for all services

## Scalability Considerations

### Horizontal Scaling
- Stateless API design
- Load balancer for multiple API instances
- Shared Endee database across instances

### Performance Optimization
- Async processing for document ingestion
- Caching for frequently asked questions
- Batch embedding generation
- Connection pooling for Endee

### Monitoring
- API response times
- Vector search latency
- Document processing metrics
- Error rates and logging

## Security Design

### Input Validation
- File type and size limits
- Content sanitization
- Rate limiting per IP
- Request timeout handling

### Data Protection
- API key encryption
- Secure file storage
- Access logging
- Input/output sanitization

## Error Handling Strategy

### Graceful Degradation
- Fallback to cached responses
- Alternative embedding models
- Retry mechanisms with backoff
- Clear error messages to users

### Logging and Monitoring
- Structured logging (JSON format)
- Error tracking and alerting
- Performance metrics collection
- Debug mode for development