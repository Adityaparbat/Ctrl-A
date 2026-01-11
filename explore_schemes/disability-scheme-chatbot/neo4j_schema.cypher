/*
Neo4j Schema and Constraints for GraphRAG Chatbot
Government Schemes for Persons with Disabilities (Divyangjan) in India

This schema defines:
- Node types with properties including embeddings
- Relationships between nodes
- Vector index for semantic similarity search
- Constraints for data integrity
*/

// ============================================
// CREATE CONSTRAINTS (Run first to ensure data integrity)
// ============================================

// Unique constraints on IDs
CREATE CONSTRAINT scheme_id IF NOT EXISTS FOR (s:Scheme) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT disability_type_id IF NOT EXISTS FOR (d:DisabilityType) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT benefit_id IF NOT EXISTS FOR (b:Benefit) REQUIRE b.id IS UNIQUE;
CREATE CONSTRAINT eligibility_id IF NOT EXISTS FOR (e:Eligibility) REQUIRE e.id IS UNIQUE;
CREATE CONSTRAINT document_id IF NOT EXISTS FOR (doc:Document) REQUIRE doc.id IS UNIQUE;
CREATE CONSTRAINT application_process_id IF NOT EXISTS FOR (ap:ApplicationProcess) REQUIRE ap.id IS UNIQUE;
CREATE CONSTRAINT government_body_id IF NOT EXISTS FOR (gb:GovernmentBody) REQUIRE gb.id IS UNIQUE;
CREATE CONSTRAINT portal_id IF NOT EXISTS FOR (p:Portal) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT helpline_id IF NOT EXISTS FOR (h:Helpline) REQUIRE h.id IS UNIQUE;

// ============================================
// CREATE VECTOR INDEX FOR SEMANTIC SIMILARITY SEARCH
// ============================================

// Vector index for Scheme nodes (embedding dimension: 384 for all-MiniLM-L6-v2)
CREATE VECTOR INDEX scheme_embedding_index IF NOT EXISTS
FOR (s:Scheme)
ON s.embedding
OPTIONS {
    indexConfig: {
        `vector.dimensions`: 384,
        `vector.similarity_function`: 'cosine'
    }
};

// Vector index for DisabilityType nodes
CREATE VECTOR INDEX disability_type_embedding_index IF NOT EXISTS
FOR (d:DisabilityType)
ON d.embedding
OPTIONS {
    indexConfig: {
        `vector.dimensions`: 384,
        `vector.similarity_function`: 'cosine'
    }
};

// Vector index for Benefit nodes
CREATE VECTOR INDEX benefit_embedding_index IF NOT EXISTS
FOR (b:Benefit)
ON b.embedding
OPTIONS {
    indexConfig: {
        `vector.dimensions`: 384,
        `vector.similarity_function`: 'cosine'
    }
};

// Vector index for Eligibility nodes
CREATE VECTOR INDEX eligibility_embedding_index IF NOT EXISTS
FOR (e:Eligibility)
ON e.embedding
OPTIONS {
    indexConfig: {
        `vector.dimensions`: 384,
        `vector.similarity_function`: 'cosine'
    }
};

// ============================================
// CREATE INDEXES FOR TEXT SEARCH (Optional, for keyword fallback)
// ============================================

CREATE INDEX scheme_name_index IF NOT EXISTS FOR (s:Scheme) ON (s.name);
CREATE INDEX scheme_description_index IF NOT EXISTS FOR (s:Scheme) ON (s.description_text);

// ============================================
// SCHEMA DOCUMENTATION
// ============================================

/*
NODE TYPES:

1. Scheme
   Properties:
   - id (String, Unique)
   - name (String)
   - description_text (String) - Full text description
   - source (String) - Official government source URL
   - last_updated (String, Date)
   - application_deadline (String, optional) - Application deadline/last date
   - deadline (String, optional) - Alternative deadline field
   - closing_date (String, optional) - Closing date for applications
   - embedding (List[Float], 384 dimensions) - Semantic embedding vector

2. DisabilityType
   Properties:
   - id (String, Unique)
   - name (String)
   - description_text (String)
   - source (String)
   - last_updated (String)
   - embedding (List[Float], 384 dimensions)

3. Benefit
   Properties:
   - id (String, Unique)
   - name (String)
   - description_text (String)
   - amount (String, optional) - e.g., "₹3000 per month"
   - source (String)
   - last_updated (String)
   - embedding (List[Float], 384 dimensions)

4. Eligibility
   Properties:
   - id (String, Unique)
   - name (String) - e.g., "Age 18+ with 40% disability"
   - description_text (String) - Full eligibility criteria
   - age_min (Integer, optional)
   - age_max (Integer, optional)
   - income_max (Integer, optional)
   - disability_percent_min (Integer, optional)
   - source (String)
   - last_updated (String)
   - embedding (List[Float], 384 dimensions)

5. Document
   Properties:
   - id (String, Unique)
   - name (String)
   - description_text (String)
   - document_type (String) - e.g., "Certificate", "Identity", "Medical"
   - source (String)
   - last_updated (String)

6. ApplicationProcess
   Properties:
   - id (String, Unique)
   - name (String) - e.g., "Online Application Process"
   - description_text (String) - Step-by-step process
   - steps (List[String], optional) - Array of steps
   - source (String)
   - last_updated (String)
   - embedding (List[Float], 384 dimensions)

7. GovernmentBody
   Properties:
   - id (String, Unique)
   - name (String) - e.g., "Department of Empowerment of Persons with Disabilities"
   - description_text (String)
   - contact (String, optional)
   - source (String)
   - last_updated (String)

8. Portal
   Properties:
   - id (String, Unique)
   - name (String) - e.g., "UDID Portal"
   - url (String) - Portal URL
   - description_text (String)
   - source (String)
   - last_updated (String)

9. Helpline
   Properties:
   - id (String, Unique)
   - name (String) - e.g., "Disability Helpline"
   - number (String) - Phone number
   - description_text (String)
   - source (String)
   - last_updated (String)


RELATIONSHIPS:

- (Scheme)-[:FOR_DISABILITY]->(DisabilityType)
  - Meaning: Scheme is available for this disability type

- (Scheme)-[:HAS_BENEFIT]->(Benefit)
  - Meaning: Scheme provides this benefit

- (Scheme)-[:HAS_ELIGIBILITY]->(Eligibility)
  - Meaning: Scheme has this eligibility criterion

- (Scheme)-[:REQUIRES_DOCUMENT]->(Document)
  - Meaning: Scheme requires this document for application

- (Scheme)-[:APPLY_VIA]->(Portal)
  - Meaning: Scheme can be applied through this portal

- (Scheme)-[:APPLY_THROUGH]->(ApplicationProcess)
  - Meaning: Scheme uses this application process

- (Scheme)-[:IMPLEMENTED_BY]->(GovernmentBody)
  - Meaning: Scheme is implemented/administered by this government body

- (Scheme)-[:HAS_HELPLINE]->(Helpline)
  - Meaning: Scheme has this helpline for support


USAGE:

1. Vector Similarity Search:
   CALL db.index.vector.queryNodes('scheme_embedding_index', 10, $queryEmbedding)
   YIELD node, score
   RETURN node, score
   ORDER BY score DESC

2. Subgraph Extraction:
   MATCH (s:Scheme {id: $schemeId})
   OPTIONAL MATCH (s)-[:FOR_DISABILITY]->(d:DisabilityType)
   OPTIONAL MATCH (s)-[:HAS_BENEFIT]->(b:Benefit)
   OPTIONAL MATCH (s)-[:HAS_ELIGIBILITY]->(e:Eligibility)
   OPTIONAL MATCH (s)-[:REQUIRES_DOCUMENT]->(doc:Document)
   OPTIONAL MATCH (s)-[:APPLY_VIA]->(p:Portal)
   OPTIONAL MATCH (s)-[:APPLY_THROUGH]->(ap:ApplicationProcess)
   OPTIONAL MATCH (s)-[:IMPLEMENTED_BY]->(gb:GovernmentBody)
   OPTIONAL MATCH (s)-[:HAS_HELPLINE]->(h:Helpline)
   RETURN s, collect(DISTINCT d) as disabilities, collect(DISTINCT b) as benefits,
          collect(DISTINCT e) as eligibility, collect(DISTINCT doc) as documents,
          collect(DISTINCT p) as portals, collect(DISTINCT ap) as processes,
          collect(DISTINCT gb) as government_bodies, collect(DISTINCT h) as helplines
*/
