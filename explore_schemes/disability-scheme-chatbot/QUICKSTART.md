# Quick Start Guide

Get the GraphRAG chatbot running in 5 minutes!

## Prerequisites

- Python 3.8+
- Neo4j 5.x (Community Edition or Desktop)
- Internet connection (for downloading embeddings model)

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI and Uvicorn
- Neo4j driver
- SentenceTransformers (for embeddings)
- Other required packages

## Step 2: Start Neo4j

1. **If using Neo4j Desktop:**
   - Open Neo4j Desktop
   - Start your database instance
   - Note the connection URI (usually `neo4j://localhost:7687`)

2. **If using Neo4j Community Edition:**
   ```bash
   # Start Neo4j service
   neo4j start
   ```

3. **Verify Neo4j is running:**
   - Open Neo4j Browser: `http://localhost:7474`
   - Login with your credentials (default: `neo4j` / `neo4j`)

## Step 3: Configure Connection

Update Neo4j connection settings in `graphrag.py` and `data_ingestion.py`:

```python
NEO4J_URI = "neo4j://127.0.0.1:7687"  # Your Neo4j URI
NEO4J_USER = "neo4j"                   # Your username
NEO4J_PASSWORD = "your_password"       # Your password
```

## Step 4: Create Schema

**Option A: Using Neo4j Browser**
1. Open Neo4j Browser: `http://localhost:7474`
2. Copy contents of `neo4j_schema.cypher`
3. Paste and execute in Browser

**Option B: Using Cypher Shell**
```bash
cypher-shell -u neo4j -p your_password < neo4j_schema.cypher
```

This creates:
- Constraints on node IDs
- Vector indexes for semantic search
- Text indexes for fallback search

## Step 5: Ingest Sample Data

```bash
python data_ingestion.py
```

This will:
- Generate embeddings for all nodes (first run downloads model ~80MB)
- Create nodes in Neo4j with embeddings
- Create relationships between nodes

**Expected output:**
```
INFO:__main__:Starting data ingestion...
INFO:__main__:Created DisabilityType node: Visual Impairment (ID: disability_visual)
INFO:__main__:Created Scheme node: Indira Gandhi National Disability Pension Scheme (ID: scheme_igndps)
...
INFO:__main__:Data ingestion completed successfully!
```

**Verify data:**
In Neo4j Browser, run:
```cypher
MATCH (s:Scheme) RETURN s.name LIMIT 5
```

## Step 6: Start API Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Step 7: Test the API

### Health Check
```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "neo4j_connection": "connected",
  "vector_indexes": "configured"
}
```

### Test Chat Endpoint

**Domain-related query (should work):**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What schemes are available for persons with disabilities?"}'
```

**Out-of-domain query (should be rejected):**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the weather today?"}'
```

**Expected response for out-of-domain:**
```json
{
  "answer": "I can help only with government schemes and services for persons with disabilities. Please ask a related question."
}
```

## Step 8: Open Frontend (Optional)

Open `chatbot.html` in your web browser and test the chatbot interface.

Or update the API URL in `chatbot.html` if your server is running on a different port.

## Troubleshooting

### Issue: Neo4j Connection Failed

**Solution:**
- Verify Neo4j is running: `neo4j status`
- Check URI, username, password in `graphrag.py`
- Ensure Neo4j is accessible at the specified URI

### Issue: Vector Index Not Found

**Error:** `Index 'scheme_embedding_index' does not exist`

**Solution:**
- Ensure Neo4j version is 5.x+ (vector indexes require Neo4j 5.x)
- Run `neo4j_schema.cypher` to create indexes
- Check index creation: `SHOW INDEXES` in Neo4j Browser

### Issue: Embedding Model Download Fails

**Error:** `ConnectionError: Failed to download model`

**Solution:**
- Check internet connection
- Model `all-MiniLM-L6-v2` (~80MB) needs to be downloaded once
- Model is cached for future use

### Issue: No Results from Vector Search

**Solution:**
- Verify data is ingested: `MATCH (s:Scheme) RETURN count(s)`
- Check embeddings exist: `MATCH (s:Scheme) WHERE s.embedding IS NOT NULL RETURN count(s)`
- Lower similarity threshold in `graphrag.py` if needed

### Issue: Import Errors

**Error:** `ModuleNotFoundError: No module named 'sentence_transformers'`

**Solution:**
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install sentence-transformers torch fastapi uvicorn neo4j pydantic
```

## Next Steps

1. **Add More Schemes:** Update `sample_data.json` and re-run `data_ingestion.py`
2. **Customize Domain Guardrail:** Adjust threshold in `domain_guardrail.py`
3. **Fine-tune Vector Search:** Modify `VECTOR_SEARCH_TOP_K` and `SIMILARITY_THRESHOLD` in `graphrag.py`
4. **Deploy to Production:** Follow deployment guidelines in `README.md`

## Verification Checklist

- [ ] Neo4j is running and accessible
- [ ] Schema is created (constraints and indexes)
- [ ] Sample data is ingested
- [ ] API server is running
- [ ] Health check returns "healthy"
- [ ] Domain-related queries work
- [ ] Out-of-domain queries are rejected with exact message

## Support

For issues or questions:
1. Check `README.md` for detailed documentation
2. Review error messages in logs
3. Verify Neo4j version compatibility (5.x+)
4. Check vector index syntax for your Neo4j version

---

**Happy Chatbot Building! 🚀**
