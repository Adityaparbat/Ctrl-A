# Architecture Documentation

## Overview

This GraphRAG chatbot implements a strict domain-restricted system for government schemes for persons with disabilities in India. The architecture follows a **Graph + Vector Retrieval Augmented Generation** pattern with semantic embeddings.

## Architecture Components

### 1. **Embeddings Module** (`embeddings.py`)
- **Purpose**: Semantic embedding generation using SentenceTransformers
- **Model**: `all-MiniLM-L6-v2` (384 dimensions)
- **Functions**:
  - `encode_text()`: Encode text(s) into embedding vectors
  - `compute_cosine_similarity()`: Calculate cosine similarity between vectors
  - `batch_encode_texts()`: Batch encoding for efficiency

### 2. **Domain Guardrail** (`domain_guardrail.py`)
- **Purpose**: Strict domain restriction using semantic similarity
- **Method**: Embedding-based similarity comparison
- **Threshold**: 0.45 cosine similarity
- **Rejection Message**: Exact, unchangeable message for out-of-domain queries
- **Functions**:
  - `is_domain_related()`: Check if query is domain-related
  - `get_rejection_message()`: Return exact rejection message

### 3. **GraphRAG Pipeline** (`graphrag.py`)
- **Purpose**: Main GraphRAG retrieval pipeline
- **Flow**:
  1. Query embedding
  2. Domain similarity check
  3. Vector similarity search in Neo4j
  4. Subgraph extraction
  5. Context assembly
- **Functions**:
  - `vector_search_schemes()`: Vector similarity search on Scheme nodes
  - `extract_subgraph()`: Extract related nodes for schemes
  - `semantic_intent_understanding()`: Understand query intent semantically
  - `retrieve_context()`: Main retrieval function implementing GraphRAG flow

### 4. **Response Generation** (`rag.py`)
- **Purpose**: Format graph data into natural language answers
- **Rules**:
  - Simple, clear language
  - Structured output (bullet points/steps)
  - Answer ONLY from graph context
  - No hallucination
- **Functions**:
  - `generate_answer()`: Main response generation function
  - `format_scheme_list()`: Format list of schemes
  - `format_scheme_details()`: Format detailed scheme information
  - `format_eligibility_info()`: Format eligibility criteria
  - `format_documents_info()`: Format required documents
  - `format_application_process()`: Format application process

### 5. **API Backend** (`main.py`)
- **Framework**: FastAPI
- **Endpoints**:
  - `POST /chat`: Main chat endpoint (GraphRAG flow)
  - `GET /`: Health check
  - `GET /health`: Detailed health check
- **Process Flow**:
  1. Domain guardrail check
  2. GraphRAG retrieval
  3. Response generation
  4. Return formatted answer

### 6. **Data Ingestion** (`data_ingestion.py`)
- **Purpose**: Load government scheme data with embeddings into Neo4j
- **Process**:
  1. Load data from JSON
  2. Generate embeddings for all nodes
  3. Create nodes in Neo4j with embeddings
  4. Create relationships between nodes
- **Functions**:
  - Node creation functions for each node type
  - `generate_embedding_text()`: Create text for embedding generation
  - `ingest_data()`: Main ingestion function

### 7. **Neo4j Schema** (`neo4j_schema.cypher`)
- **Node Types**: Scheme, DisabilityType, Benefit, Eligibility, Document, ApplicationProcess, GovernmentBody, Portal, Helpline
- **Relationships**: FOR_DISABILITY, HAS_BENEFIT, HAS_ELIGIBILITY, REQUIRES_DOCUMENT, APPLY_VIA, APPLY_THROUGH, IMPLEMENTED_BY, HAS_HELPLINE
- **Constraints**: Unique constraints on node IDs
- **Vector Indexes**: Vector indexes on Scheme, DisabilityType, Benefit, Eligibility, ApplicationProcess nodes (384 dimensions, cosine similarity)

## Data Flow

### Query Processing Flow

```
User Query
    ↓
[Domain Guardrail]
    ├─> Semantic Embedding
    ├─> Compare with Domain Embedding
    └─> Similarity >= 0.45? ──Yes──> Continue
                            └─No──> Return Rejection Message
    ↓
[Intent Understanding]
    ├─> Encode Query
    ├─> Compare with Intent Patterns
    └─> Classify Intent (scheme_list, benefit, eligibility, etc.)
    ↓
[Vector Similarity Search]
    ├─> Encode Query → Embedding Vector (384D)
    ├─> Query Neo4j Vector Index
    ├─> Retrieve Top-K Similar Schemes
    └─> Filter by Similarity Threshold (>= 0.5)
    ↓
[Subgraph Extraction]
    ├─> Extract Scheme IDs
    ├─> Query Related Nodes (Disabilities, Benefits, Eligibility, etc.)
    └─> Assemble Subgraph Context
    ↓
[Context Assembly]
    ├─> Combine Scheme Information
    ├─> Include Related Nodes
    └─> Structure Context Dictionary
    ↓
[Response Generation]
    ├─> Format Based on Intent
    ├─> Use ONLY Graph Context (No Hallucination)
    └─> Return Structured Answer
```

## Graph Structure

### Node Relationships

```
Scheme
  ├─> FOR_DISABILITY ──> DisabilityType
  ├─> HAS_BENEFIT ──> Benefit
  ├─> HAS_ELIGIBILITY ──> Eligibility
  ├─> REQUIRES_DOCUMENT ──> Document
  ├─> APPLY_VIA ──> Portal
  ├─> APPLY_THROUGH ──> ApplicationProcess
  ├─> IMPLEMENTED_BY ──> GovernmentBody
  └─> HAS_HELPLINE ──> Helpline
```

## Vector Search Details

### Embedding Generation
- **Model**: `all-MiniLM-L6-v2` (SentenceTransformers)
- **Dimensions**: 384
- **Similarity Function**: Cosine Similarity
- **Text for Embedding**: Combines node name, description, and relevant attributes

### Vector Index Configuration
- **Index Type**: Vector Index (Neo4j 5.x+)
- **Dimensions**: 384
- **Similarity Function**: Cosine
- **Indexed Nodes**: Scheme, DisabilityType, Benefit, Eligibility, ApplicationProcess

### Vector Search Query
```cypher
CALL db.index.vector.queryNodes(
    'scheme_embedding_index',
    10,  // top_k
    $queryEmbedding  // 384-dimensional vector
)
YIELD node, score
WHERE score >= 0.5  // threshold
RETURN node, score
ORDER BY score DESC
```

## Domain Restriction Mechanism

### Semantic Domain Validation

1. **Domain Reference Embedding**: Pre-computed embedding for disability schemes domain
2. **Query Embedding**: Real-time embedding of user query
3. **Similarity Comparison**: Cosine similarity between query and domain embeddings
4. **Threshold Check**: Similarity >= 0.45 → Allow, else → Reject

### Allowed Domains
- Government schemes for persons with disabilities
- Welfare services, certificates, pensions
- Scholarships, assistive devices
- Employment & skill schemes
- Portals and helplines

### Rejection Message
**Exact message** (never modified):
```
"I can help only with government schemes and services for persons with disabilities. Please ask a related question."
```

## Semantic Understanding

### Intent Classification

The system uses semantic similarity to understand query intent without keyword matching:

**Example Mappings:**
- `"money help for disabled students"` → benefit intent → scholarship schemes
- `"wheelchair from government"` → benefit intent → ADIP scheme
- `"disability id card"` → document intent → UDID certificate
- `"monthly support for blind people"` → benefit intent → pension schemes

**Intent Patterns:**
- `scheme_list`: What schemes are available?
- `scheme_details`: Tell me about a specific scheme
- `benefit`: What benefits are available?
- `eligibility`: Who is eligible?
- `documents`: What documents are required?
- `application_process`: How to apply?
- `portal`: Where to apply online?
- `helpline`: Contact information

## Performance Considerations

### Embedding Caching
- Model is loaded once and reused (singleton pattern)
- Domain embedding is pre-computed at module load
- Intent patterns are encoded once and reused

### Neo4j Optimization
- Vector indexes for fast similarity search
- Text indexes for fallback keyword search
- Constraints for data integrity
- Efficient subgraph extraction queries

### Scalability
- Batch embedding generation for data ingestion
- Top-K retrieval limits result set size
- Similarity threshold filters low-relevance results

## Security Considerations

### Input Validation
- Domain guardrail prevents out-of-domain queries
- No SQL/cypher injection (parameterized queries)
- Input sanitization through Pydantic models

### Data Integrity
- Unique constraints on node IDs
- Relationship validation
- Source attribution for all data

## Monitoring and Logging

### Logging Levels
- **INFO**: Normal operations (queries, responses)
- **ERROR**: Errors (connection failures, query errors)
- **WARNING**: Warnings (missing data, low similarity scores)

### Metrics to Monitor
- Domain guardrail rejection rate
- Vector search performance (query time, result count)
- Similarity score distribution
- API response times
- Neo4j query execution time

## Future Enhancements

### Potential Improvements
1. **Multi-language Support**: Extend embeddings to Hindi and other Indian languages
2. **Conversation Context**: Maintain conversation history for follow-up questions
3. **Feedback Loop**: Collect user feedback to improve domain guardrail
4. **Advanced Intent Classification**: Fine-tune embeddings for better intent understanding
5. **Real-time Updates**: Webhook-based scheme data updates
6. **Analytics Dashboard**: Track popular queries and schemes

### Scalability Options
1. **Neo4j Clustering**: High availability and load distribution
2. **Embedding Service**: Separate embedding service for better resource management
3. **Caching Layer**: Redis cache for frequently accessed queries
4. **CDN**: Frontend asset delivery

---

**Architecture Version**: 1.0.0  
**Last Updated**: 2024-01-01
