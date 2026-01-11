# Government Schemes Chatbot for Persons with Disabilities (Divyangjan) - GraphRAG Architecture

A production-ready, domain-restricted GraphRAG chatbot for government schemes and services for persons with disabilities in India. This chatbot uses **Graph + Vector Retrieval Augmented Generation** architecture with Neo4j as the knowledge graph database and semantic embeddings for intelligent retrieval.

## 🎯 Core Features

- **GraphRAG Architecture**: Combines graph structure with vector similarity search for accurate, explainable responses
- **Strict Domain Restriction**: Answers ONLY questions related to government disability schemes
- **Semantic Understanding**: Uses sentence embeddings (not keyword matching) for intent understanding
- **Vector Similarity Search**: Neo4j vector indexes for efficient semantic search
- **No Hallucination**: LLM used ONLY for response formatting, NOT as a knowledge source
- **Accessibility-Friendly**: Simple, clear language with structured output

## 📋 Requirements

### Software Dependencies
- Python 3.8+
- Neo4j 5.x (with vector index support)
- FastAPI for backend API
- SentenceTransformers for embeddings

### Python Packages
Install dependencies:
```bash
pip install -r requirements.txt
```

## 🏗️ Architecture

### GraphRAG Flow (MANDATORY)

```
User Query
    ↓
Semantic Embedding (SentenceTransformers)
    ↓
Domain Similarity Check (threshold-based)
    ↓
Neo4j Vector Similarity Search
    ↓
Subgraph Extraction
    ↓
Context Assembly (ONLY from graph)
    ↓
LLM Response Generation (formatting only)
```

### Neo4j Schema

**Node Types:**
- `Scheme` - Government schemes
- `DisabilityType` - Types of disabilities
- `Benefit` - Benefits provided
- `Eligibility` - Eligibility criteria
- `Document` - Required documents
- `ApplicationProcess` - Application processes
- `GovernmentBody` - Implementing bodies
- `Portal` - Online portals
- `Helpline` - Helpline numbers

**Relationships:**
- `(Scheme)-[:FOR_DISABILITY]->(DisabilityType)`
- `(Scheme)-[:HAS_BENEFIT]->(Benefit)`
- `(Scheme)-[:HAS_ELIGIBILITY]->(Eligibility)`
- `(Scheme)-[:REQUIRES_DOCUMENT]->(Document)`
- `(Scheme)-[:APPLY_VIA]->(Portal)`
- `(Scheme)-[:APPLY_THROUGH]->(ApplicationProcess)`
- `(Scheme)-[:IMPLEMENTED_BY]->(GovernmentBody)`
- `(Scheme)-[:HAS_HELPLINE]->(Helpline)`

**Vector Indexes:**
- Vector index on `Scheme.embedding` (384 dimensions, cosine similarity)
- Vector index on `DisabilityType.embedding`
- Vector index on `Benefit.embedding`
- Vector index on `Eligibility.embedding`
- Vector index on `ApplicationProcess.embedding`

## 🚀 Setup Instructions

### 1. Neo4j Setup

1. Install Neo4j Desktop or Neo4j Community Edition (5.x+)
2. Start Neo4j server
3. Note your Neo4j URI, username, and password

### 2. Configure Connection

Update Neo4j connection settings in:
- `graphrag.py`: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- `data_ingestion.py`: Same settings

Default settings:
```python
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "your_password"
```

### 3. Create Schema

Run the Neo4j schema file to create constraints and vector indexes:

```bash
# In Neo4j Browser or Cypher Shell
cypher-shell < neo4j_schema.cypher
```

Or manually copy-paste the contents of `neo4j_schema.cypher` into Neo4j Browser.

### 4. Ingest Sample Data

Load sample government scheme data with embeddings:

```bash
python data_ingestion.py
```

This script:
- Generates embeddings for all nodes
- Creates nodes in Neo4j with embeddings
- Creates relationships between nodes

### 5. Start Backend API

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: `http://127.0.0.1:8000`

### 6. Test the API

Health check:
```bash
curl http://127.0.0.1:8000/health
```

Chat endpoint:
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What schemes are available for persons with disabilities?"}'
```

## 📁 Project Structure

```
disability-scheme-chatbot/
├── main.py                 # FastAPI backend with GraphRAG flow
├── graphrag.py            # GraphRAG retrieval pipeline (vector search + subgraph)
├── embeddings.py          # Semantic embedding functions
├── domain_guardrail.py    # Strict domain restriction logic
├── rag.py                 # Response generation (formatting only)
├── graph.py               # Legacy graph queries (backup)
├── validator.py           # Legacy validator (backup)
├── data_ingestion.py      # Data ingestion script with embeddings
├── neo4j_schema.cypher    # Neo4j schema, constraints, and vector indexes
├── sample_data.json       # Sample government scheme data
├── requirements.txt       # Python dependencies
├── chatbot.html           # Frontend HTML interface
└── README.md              # This file
```

## 🔒 Domain Restriction

The chatbot has **strict domain guardrails**:

### Allowed Questions:
- Government schemes for persons with disabilities
- Welfare services, certificates, pensions
- Scholarships, assistive devices
- Employment & skill schemes
- Portals and helplines

### Out-of-Domain Questions:
Any question NOT related to disability schemes receives the EXACT response:
```
"I can help only with government schemes and services for persons with disabilities. Please ask a related question."
```

**No exceptions. No hallucination. No extra explanation.**

### Domain Validation:
- Uses semantic similarity (embedding-based) comparison
- Threshold: 0.45 cosine similarity
- Reference embedding: Domain-specific text about disability schemes

## 🧠 Semantic Understanding

The chatbot uses **sentence embeddings** (not keyword matching) for intent understanding:

**Example Mappings:**
- `"money help for disabled students"` → disability scholarship schemes
- `"wheelchair from government"` → ADIP scheme
- `"disability id card"` → UDID certificate
- `"monthly support for blind people"` → disability pension

## 📊 Vector Similarity Search

**How it works:**
1. User query is encoded into a 384-dimensional embedding vector
2. Query embedding is compared with scheme embeddings using cosine similarity
3. Top-K most similar schemes are retrieved (default: 10, threshold: 0.5)
4. Subgraph is extracted for relevant schemes
5. Context is assembled from graph relationships

**Embedding Model:**
- Model: `all-MiniLM-L6-v2` (SentenceTransformers)
- Dimensions: 384
- Similarity Function: Cosine similarity

## 🎨 Response Generation

**Response Rules:**
- Simple, clear language
- Structured output (bullet points / steps)
- Answer ONLY from Neo4j graph context
- If information is missing: `"This information is not available in the official scheme data."`

**LLM Usage:**
- LLM is used **ONLY** for response formatting
- **NOT** used as a knowledge source
- **NO** hallucination - all information comes from graph

## 🧪 Testing

### Test Domain Guardrail

```bash
# Should be accepted (domain-related)
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is disability pension?"}'

# Should be rejected (out-of-domain)
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the weather today?"}'
```

### Test Semantic Understanding

```bash
# These should map to the same intent (semantic similarity)
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "money help for disabled students"}'

curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "scholarship schemes for persons with disabilities"}'
```

### Test Vector Search

```bash
# Should retrieve relevant schemes based on semantic similarity
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "wheelchair from government"}'
```

## 🔧 Configuration

### Vector Search Parameters

In `graphrag.py`:
```python
VECTOR_SEARCH_TOP_K = 10      # Number of top similar nodes
SIMILARITY_THRESHOLD = 0.5    # Minimum similarity score
```

### Domain Guardrail Threshold

In `domain_guardrail.py`:
```python
DOMAIN_SIMILARITY_THRESHOLD = 0.45  # Domain similarity threshold
```

### Embedding Model

In `embeddings.py`:
```python
MODEL_NAME = "all-MiniLM-L6-v2"  # SentenceTransformer model
EMBEDDING_DIM = 384               # Embedding dimensions
```

## 🐛 Troubleshooting

### Neo4j Connection Issues
- Ensure Neo4j is running: `neo4j status`
- Check URI, username, password in `graphrag.py`
- Verify database name: `NEO4J_DATABASE = "neo4j"`

### Vector Index Not Found
- Ensure Neo4j version 5.x+ (vector index support)
- Run `neo4j_schema.cypher` to create indexes
- Check index creation: `SHOW INDEXES` in Neo4j Browser

### Embedding Model Download
- First run will download `all-MiniLM-L6-v2` model (~80MB)
- Requires internet connection
- Model is cached for future use

### No Results from Vector Search
- Check if data is ingested: `MATCH (s:Scheme) RETURN count(s)`
- Verify embeddings exist: `MATCH (s:Scheme) WHERE s.embedding IS NOT NULL RETURN count(s)`
- Lower similarity threshold if needed

## 📝 Adding New Schemes

To add new government schemes:

1. **Update `sample_data.json`**:
   - Add scheme details
   - Add related nodes (disabilities, benefits, eligibility, documents, etc.)
   - Define relationships

2. **Re-run data ingestion**:
   ```bash
   python data_ingestion.py
   ```

3. **Verify in Neo4j**:
   ```cypher
   MATCH (s:Scheme {name: "Your Scheme Name"}) RETURN s
   ```

## 🚧 Production Deployment

### Security Considerations
- Update CORS settings in `main.py` (specify exact origins)
- Secure Neo4j credentials (use environment variables)
- Use HTTPS for API endpoints
- Rate limiting recommended

### Performance Optimization
- Use Neo4j clustering for high availability
- Cache embeddings for frequently accessed nodes
- Monitor vector index performance
- Adjust `VECTOR_SEARCH_TOP_K` based on response time

### Monitoring
- Log all queries for audit
- Monitor domain guardrail rejections
- Track vector search performance metrics
- Monitor Neo4j query execution time

## 📚 References

- [Neo4j Vector Index Documentation](https://neo4j.com/docs/cypher-manual/current/indexes-for-vector-search/)
- [SentenceTransformers Documentation](https://www.sbert.net/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Government Disability Schemes Portal](https://disabilityaffairs.gov.in)

## 📄 License

This project is provided as-is for educational and research purposes.

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Domain restriction is maintained
- No hallucination in responses
- All information comes from Neo4j graph
- Semantic understanding is used (not keyword matching)

---

**Built with ❤️ for accessibility and social good.**
