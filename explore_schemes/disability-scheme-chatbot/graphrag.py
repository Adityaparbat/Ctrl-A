"""
GraphRAG Module - Graph + Vector Retrieval Augmented Generation
This module implements the GraphRAG retrieval pipeline:
1. Query embedding
2. Vector similarity search in Neo4j
3. Subgraph extraction
4. Context assembly from graph
5. LLM response generation (delegated to rag.py)

MANDATORY FLOW:
User Query → Semantic embedding → Domain similarity check → Neo4j vector similarity search 
→ Subgraph extraction → Context assembly → LLM generates final answer
"""

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from typing import List, Dict, Any, Optional
import logging
from embeddings import encode_text, compute_cosine_similarity
from domain_guardrail import is_domain_related, get_rejection_message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Neo4j connection configuration
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Kashish@2510"  # Update with your Neo4j password
NEO4J_DATABASE = "neo4j"

# Vector similarity search parameters
VECTOR_SEARCH_TOP_K = 10  # Number of top similar nodes to retrieve
SIMILARITY_THRESHOLD = 0.35  # Minimum similarity score threshold (lowered from 0.4 for better recall)

# Initialize Neo4j driver
try:
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD)
    )
    logger.info("Neo4j driver initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Neo4j driver: {e}")
    driver = None


def get_driver():
    """Get the Neo4j driver instance."""
    if driver is None:
        raise ConnectionError("Neo4j driver not initialized. Please check connection settings.")
    return driver


def vector_search_schemes(query_embedding: List[float], top_k: int = VECTOR_SEARCH_TOP_K) -> List[Dict[str, Any]]:
    """
    Perform vector similarity search on Scheme nodes.
    
    Uses Neo4j vector index for efficient similarity search.
    Falls back to text-based search if vector index is not available.
    
    Args:
        query_embedding: Query embedding vector (384 dimensions)
        top_k: Number of top similar schemes to return
    
    Returns:
        List of scheme dictionaries with similarity scores
    """
    try:
        with get_driver().session(database=NEO4J_DATABASE) as session:
            # First, try vector similarity search
            try:
                result = session.run("""
                    CALL db.index.vector.queryNodes(
                        'scheme_embedding_index',
                        $top_k,
                        $query_embedding
                    )
                    YIELD node, score
                    WHERE score >= $threshold
                    RETURN node.id AS id, node.name AS name, 
                           node.description_text AS description_text,
                           node.source AS source, node.last_updated AS last_updated,
                           node.application_deadline AS application_deadline,
                           node.deadline AS deadline,
                           node.closing_date AS closing_date,
                           score AS similarity_score
                    ORDER BY score DESC
                """, 
                query_embedding=query_embedding,
                top_k=top_k,
                threshold=SIMILARITY_THRESHOLD)
                
                schemes = []
                for record in result:
                    schemes.append({
                        'id': record['id'],
                        'name': record['name'],
                        'description_text': record.get('description_text', ''),
                        'source': record.get('source', ''),
                        'last_updated': record.get('last_updated', ''),
                        'application_deadline': record.get('application_deadline'),
                        'deadline': record.get('deadline'),
                        'closing_date': record.get('closing_date'),
                        'similarity_score': float(record['similarity_score'])
                    })
                
                if schemes:
                    logger.info(f"Vector search found {len(schemes)} schemes")
                    return schemes
                else:
                    logger.warning("Vector search returned no results, trying lower threshold...")
                    # Try with lower threshold
                    result = session.run("""
                        CALL db.index.vector.queryNodes(
                            'scheme_embedding_index',
                            $top_k,
                            $query_embedding
                        )
                        YIELD node, score
                        WHERE score >= 0.3
                        RETURN node.id AS id, node.name AS name, 
                               node.description_text AS description_text,
                               node.source AS source, node.last_updated AS last_updated,
                               node.application_deadline AS application_deadline,
                               node.deadline AS deadline,
                               node.closing_date AS closing_date,
                               score AS similarity_score
                        ORDER BY score DESC
                        LIMIT 5
                    """, 
                    query_embedding=query_embedding,
                    top_k=top_k)
                    
                    schemes = []
                    for record in result:
                        schemes.append({
                            'id': record['id'],
                            'name': record['name'],
                            'description_text': record.get('description_text', ''),
                            'source': record.get('source', ''),
                            'last_updated': record.get('last_updated', ''),
                            'similarity_score': float(record['similarity_score'])
                        })
                    
                    if schemes:
                        logger.info(f"Vector search with lower threshold found {len(schemes)} schemes")
                        return schemes
                    
            except Exception as vector_error:
                logger.warning(f"Vector index search failed: {vector_error}, falling back to text search")
            
            # Fallback: Check if any schemes exist without embeddings
            check_result = session.run("""
                MATCH (s:Scheme)
                WHERE s.embedding IS NOT NULL
                RETURN count(s) AS count
            """)
            
            count_record = check_result.single()
            if count_record and count_record['count'] > 0:
                logger.warning(f"Found {count_record['count']} schemes with embeddings but vector search failed")
            else:
                logger.warning("No schemes with embeddings found, falling back to text-based search")
            
            # Fallback to text-based search: get all schemes (including deadline fields)
            result = session.run("""
                MATCH (s:Scheme)
                RETURN s.id AS id, s.name AS name, 
                       s.description_text AS description_text,
                       s.source AS source, s.last_updated AS last_updated,
                       s.application_deadline AS application_deadline,
                       s.deadline AS deadline,
                       s.closing_date AS closing_date
                ORDER BY s.name
                LIMIT 10
            """)
            
            schemes = []
            for record in result:
                    schemes.append({
                        'id': record['id'],
                        'name': record['name'],
                        'description_text': record.get('description_text', ''),
                        'source': record.get('source', ''),
                        'last_updated': record.get('last_updated', ''),
                        'application_deadline': record.get('application_deadline'),
                        'deadline': record.get('deadline'),
                        'closing_date': record.get('closing_date'),
                        'similarity_score': 0.5  # Default score for text-based results
                    })
            
            if schemes:
                logger.info(f"Fallback text search found {len(schemes)} schemes")
                return schemes
            else:
                logger.error("No schemes found in database at all!")
                return []
                
    except Exception as e:
        logger.error(f"Error in vector_search_schemes: {e}", exc_info=True)
        return []


def extract_subgraph(scheme_ids: List[str]) -> Dict[str, Any]:
    """
    Extract subgraph for given scheme IDs.
    Retrieves all related nodes (disabilities, benefits, eligibility, documents, etc.)
    
    Args:
        scheme_ids: List of scheme IDs to extract subgraphs for
    
    Returns:
        Dictionary containing schemes and their related nodes
    """
    try:
        with get_driver().session(database=NEO4J_DATABASE) as session:
            result = session.run("""
                MATCH (s:Scheme)
                WHERE s.id IN $scheme_ids
                OPTIONAL MATCH (s)-[:FOR_DISABILITY]->(d:DisabilityType)
                OPTIONAL MATCH (s)-[:HAS_BENEFIT]->(b:Benefit)
                OPTIONAL MATCH (s)-[:HAS_ELIGIBILITY]->(e:Eligibility)
                OPTIONAL MATCH (s)-[:REQUIRES_DOCUMENT]->(doc:Document)
                OPTIONAL MATCH (s)-[:APPLY_VIA]->(p:Portal)
                OPTIONAL MATCH (s)-[:APPLY_THROUGH]->(ap:ApplicationProcess)
                OPTIONAL MATCH (s)-[:IMPLEMENTED_BY]->(gb:GovernmentBody)
                OPTIONAL MATCH (s)-[:HAS_HELPLINE]->(h:Helpline)
                RETURN s.id AS scheme_id,
                       s.name AS scheme_name,
                       s.description_text AS scheme_description,
                       s.source AS scheme_source,
                       s.last_updated AS scheme_last_updated,
                       COALESCE(s.application_deadline, null) AS scheme_deadline,
                       COALESCE(s.deadline, null) AS scheme_deadline_alt,
                       COALESCE(s.closing_date, null) AS scheme_closing_date,
                       collect(DISTINCT {
                           id: d.id,
                           name: d.name,
                           description: d.description_text
                       }) AS disabilities,
                       collect(DISTINCT {
                           id: b.id,
                           name: b.name,
                           description: b.description_text,
                           amount: b.amount
                       }) AS benefits,
                       collect(DISTINCT {
                           id: e.id,
                           name: e.name,
                           description: e.description_text,
                           age_min: e.age_min,
                           age_max: e.age_max,
                           income_max: e.income_max,
                           disability_percent_min: e.disability_percent_min
                       }) AS eligibility,
                       collect(DISTINCT {
                           id: doc.id,
                           name: doc.name,
                           description: doc.description_text,
                           document_type: doc.document_type
                       }) AS documents,
                       collect(DISTINCT {
                           id: p.id,
                           name: p.name,
                           url: p.url,
                           description: p.description_text
                       }) AS portals,
                       collect(DISTINCT {
                           id: ap.id,
                           name: ap.name,
                           description: ap.description_text,
                           steps: ap.steps
                       }) AS application_processes,
                       collect(DISTINCT {
                           id: gb.id,
                           name: gb.name,
                           description: gb.description_text,
                           contact: gb.contact
                       }) AS government_bodies,
                       collect(DISTINCT {
                           id: h.id,
                           name: h.name,
                           number: h.number,
                           description: h.description_text
                       }) AS helplines
            """, scheme_ids=scheme_ids)
            
            schemes_data = []
            for record in result:
                scheme_data = {
                    'scheme': {
                        'id': record['scheme_id'],
                        'name': record['scheme_name'],
                        'description': record.get('scheme_description', ''),
                        'source': record.get('scheme_source', ''),
                        'last_updated': record.get('scheme_last_updated', ''),
                        'application_deadline': record.get('scheme_deadline'),
                        'deadline': record.get('scheme_deadline_alt'),
                        'closing_date': record.get('scheme_closing_date')
                    },
                    'disabilities': [d for d in record['disabilities'] if d.get('id')],
                    'benefits': [b for b in record['benefits'] if b.get('id')],
                    'eligibility': [e for e in record['eligibility'] if e.get('id')],
                    'documents': [doc for doc in record['documents'] if doc.get('id')],
                    'portals': [p for p in record['portals'] if p.get('id')],
                    'application_processes': [ap for ap in record['application_processes'] if ap.get('id')],
                    'government_bodies': [gb for gb in record['government_bodies'] if gb.get('id')],
                    'helplines': [h for h in record['helplines'] if h.get('id')]
                }
                schemes_data.append(scheme_data)
            
            return {'schemes': schemes_data}
    except Exception as e:
        logger.error(f"Error in extract_subgraph: {e}")
        return {'schemes': []}


def semantic_intent_understanding(query: str) -> Dict[str, Any]:
    """
    Understand user query intent using semantic embeddings.
    Maps natural language to structured intent without keyword matching.
    
    Example mappings:
    - "money help for disabled students" → intent: benefit, subtype: scholarship
    - "wheelchair from government" → intent: benefit, subtype: assistive_device
    - "disability id card" → intent: document, subtype: certificate
    - "monthly support for blind people" → intent: benefit, subtype: pension
    
    Args:
        query: User's natural language query
    
    Returns:
        Dictionary with intent classification
    """
    query_lower = query.lower()
    
    # Encode query for semantic comparison
    query_embedding = encode_text(query)
    
    # Semantic intent patterns (represented as embeddings)
    # Enhanced to handle "retirement" as pension and "deadline" queries
    intent_patterns = {
        'scheme_list': encode_text("what schemes are available for persons with disabilities"),
        'scheme_details': encode_text("tell me about a specific government scheme"),
        'benefit': encode_text("what benefits money pension retirement scheme scholarship allowance"),
        'eligibility': encode_text("who is eligible for disability schemes"),
        'documents': encode_text("what documents are required for application"),
        'application_process': encode_text("how to apply for disability schemes"),
        'deadline': encode_text("deadline last date application deadline closing date when to apply"),
        'disability_specific': encode_text("schemes for specific disability type"),
        'portal': encode_text("where to apply online portal website"),
        'helpline': encode_text("contact help support helpline number")
    }
    
    # Compute similarities with intent patterns
    similarities = {}
    for intent, pattern_embedding in intent_patterns.items():
        similarities[intent] = compute_cosine_similarity(query_embedding, pattern_embedding)
    
    # --- KEYWORD BOOSTING ---
    # Boost scores based on explicit keys to improve accuracy over pure vectors
    
    if 'deadline' in query_lower or 'last date' in query_lower or 'closing date' in query_lower:
        similarities['deadline'] = max(similarities.get('deadline', 0), 0.75)
        
    if 'how to' in query_lower or 'process' in query_lower or 'procedure' in query_lower or 'steps' in query_lower:
        similarities['application_process'] = max(similarities.get('application_process', 0), 0.65)
        
    if 'document' in query_lower or 'paper' in query_lower or 'proof' in query_lower or 'certificate' in query_lower:
        similarities['documents'] = max(similarities.get('documents', 0), 0.65)
        
    if 'eligible' in query_lower or 'criteria' in query_lower or 'who can' in query_lower:
        similarities['eligibility'] = max(similarities.get('eligibility', 0), 0.65)
        
    if 'benefit' in query_lower or 'money' in query_lower or 'amount' in query_lower or 'rupees' in query_lower or 'financial' in query_lower:
        similarities['benefit'] = max(similarities.get('benefit', 0), 0.65)
        
    if 'contact' in query_lower or 'number' in query_lower or 'phone' in query_lower or 'email' in query_lower:
        similarities['helpline'] = max(similarities.get('helpline', 0), 0.7)
        
    # Check for disability specific keywords
    disability_keywords = ['hearing', 'visual', 'blind', 'locomotor', 'orthopedic', 'mental', 'autism', 'cerebral', 'speech', 'deaf', 'handicap']
    if any(k in query_lower for k in disability_keywords):
        similarities['disability_specific'] = max(similarities.get('disability_specific', 0), 0.65)
        # Also boost scheme list but slightly less
        similarities['scheme_list'] = max(similarities.get('scheme_list', 0), 0.55)

    # Special handling for "retirement" queries - map to pension/benefit
    if 'retirement' in query_lower or 'retire' in query_lower:
        # Force benefit intent for retirement queries
        similarities['benefit'] = max(similarities.get('benefit', 0), 0.65)
        logger.info("Detected retirement query, mapping to pension/benefit schemes")
    
    # Find intent with highest similarity
    best_intent = max(similarities, key=similarities.get)
    best_score = similarities[best_intent]
    
    return {
        'intent': best_intent if best_score > 0.35 else 'general',
        'confidence': best_score,
        'all_similarities': similarities
    }


def retrieve_context(query: str) -> Dict[str, Any]:
    """
    Main GraphRAG retrieval function.
    Implements the mandatory flow:
    Query → Embedding → Vector Search → Subgraph Extraction → Context
    
    Args:
        query: User's natural language query
    
    Returns:
        Dictionary with retrieved context from graph
    """
    # Step 1: Domain guardrail check
    if not is_domain_related(query):
        return {
            'is_out_of_domain': True,
            'rejection_message': get_rejection_message(),
            'context': None
        }
    
    # Step 2: Semantic intent understanding
    intent_info = semantic_intent_understanding(query)
    logger.info(f"Query intent: {intent_info['intent']} (confidence: {intent_info['confidence']:.2f})")
    
    # Step 3: Encode query for vector search
    query_lower = query.lower()
    
    # Determine if this is a general query (should return all schemes)
    intent = intent_info.get('intent', 'general')
    is_general_query = (intent == 'scheme_list' or intent == 'general') and \
                       ('list' in query_lower or 'all' in query_lower or \
                        query_lower.strip() in ['schemes', 'government schemes', 'help']) 
    
    if len(query.split()) < 4 and 'scheme' in query_lower:
         pass
    
    query_embedding = encode_text(query)
    
    # Step 4: Vector similarity search on Scheme nodes
    # For retirement queries, also search by benefit/pension keywords
    if 'retirement' in query_lower or 'retire' in query_lower:
        logger.info("Retirement query detected, searching for pension schemes...")
        # Also try a modified query that includes pension
        query_embedding = encode_text(f"{query} pension scheme for disabled persons")
    
    similar_schemes = vector_search_schemes(query_embedding, top_k=VECTOR_SEARCH_TOP_K)
    
    # If no results and query contains "retirement" or "pension", try broader search
    if not similar_schemes and ('retirement' in query_lower or 'pension' in query_lower or 'retire' in query_lower):
        logger.info("No direct matches for retirement query, trying pension-specific search...")
        pension_query_embedding = encode_text("pension scheme for persons with disabilities monthly financial assistance")
        similar_schemes = vector_search_schemes(pension_query_embedding, top_k=VECTOR_SEARCH_TOP_K)
    
    # Only fall back to ALL schemes if we really found nothing matching AND it looks general
    if (not similar_schemes) and is_general_query:
        logger.info(f"General scheme list query detected (intent: {intent}), falling back to all schemes...")
        try:
            with get_driver().session(database=NEO4J_DATABASE) as session:
                # Get all schemes directly (fallback for general queries)
                all_schemes_result = session.run("""
                    MATCH (s:Scheme)
                    RETURN s.id AS id, s.name AS name, 
                           s.description_text AS description_text,
                           s.source AS source, s.last_updated AS last_updated,
                           COALESCE(s.application_deadline, null) AS application_deadline,
                           COALESCE(s.deadline, null) AS deadline,
                           COALESCE(s.closing_date, null) AS closing_date
                    ORDER BY s.name
                    LIMIT 10
                """)
                
                fallback_schemes = []
                for record in all_schemes_result:
                    fallback_schemes.append({
                        'id': record['id'],
                        'name': record['name'],
                        'description_text': record.get('description_text', ''),
                        'source': record.get('source', ''),
                        'last_updated': record.get('last_updated', ''),
                        'application_deadline': record.get('application_deadline'),
                        'deadline': record.get('deadline'),
                        'closing_date': record.get('closing_date'),
                        'similarity_score': 0.65  # Good score for general query fallback
                    })
                
                if fallback_schemes:
                    logger.info(f"Fallback retrieved {len(fallback_schemes)} schemes for general query")
                    similar_schemes = fallback_schemes
        except Exception as e:
            logger.error(f"Error in fallback scheme retrieval: {e}", exc_info=True)
    
    if not similar_schemes:
        logger.warning(f"No schemes found for query: {query}")
        # Check if database has any schemes at all
        try:
            with get_driver().session(database=NEO4J_DATABASE) as session:
                count_result = session.run("MATCH (s:Scheme) RETURN count(s) AS count")
                count_record = count_result.single()
                total_schemes = count_record['count'] if count_record else 0
                
                if total_schemes == 0:
                    logger.error("Database has no schemes! Please run data_ingestion.py first.")
                    return {
                        'is_out_of_domain': False,
                        'context': {
                            'schemes': [],
                            'intent': intent_info,
                            'message': 'No schemes found in database. Please ensure data has been ingested using data_ingestion.py'
                        }
                    }
                else:
                    # For retirement/pension queries, try to get pension schemes directly
                    if 'retirement' in query.lower() or 'pension' in query.lower() or 'retire' in query.lower():
                        logger.info("Trying to find pension schemes directly...")
                        pension_result = session.run("""
                            MATCH (s:Scheme)-[:HAS_BENEFIT]->(b:Benefit)
                            WHERE toLower(b.name) CONTAINS 'pension' OR toLower(s.name) CONTAINS 'pension'
                            RETURN DISTINCT s.id AS id, s.name AS name, 
                                   s.description_text AS description_text,
                                   s.source AS source, s.last_updated AS last_updated,
                                   s.application_deadline AS application_deadline,
                                   s.deadline AS deadline,
                                   s.closing_date AS closing_date
                            LIMIT 5
                        """)
                        
                        pension_schemes = []
                        for record in pension_result:
                            pension_schemes.append({
                                'id': record['id'],
                                'name': record['name'],
                                'description_text': record.get('description_text', ''),
                                'source': record.get('source', ''),
                                'last_updated': record.get('last_updated', ''),
                                'application_deadline': record.get('application_deadline'),
                                'deadline': record.get('deadline'),
                                'closing_date': record.get('closing_date'),
                                'similarity_score': 0.6  # Default score for direct match
                            })
                        
                        if pension_schemes:
                            logger.info(f"Found {len(pension_schemes)} pension schemes via direct search")
                            scheme_ids = [s['id'] for s in pension_schemes]
                            subgraph = extract_subgraph(scheme_ids)
                            context = {
                                'query': query,
                                'intent': intent_info,
                                'schemes': subgraph.get('schemes', []),
                                'similarity_scores': {s['id']: s['similarity_score'] for s in pension_schemes}
                            }
                            return {
                                'is_out_of_domain': False,
                                'context': context
                            }
                    
                    # For general queries, return all schemes as fallback
                    if is_general_query:
                        logger.info(f"General query detected, returning all {total_schemes} schemes as fallback")
                        try:
                            all_schemes_result = session.run("""
                                MATCH (s:Scheme)
                                RETURN s.id AS id, s.name AS name, 
                                       s.description_text AS description_text,
                                       s.source AS source, s.last_updated AS last_updated,
                                       s.application_deadline AS application_deadline,
                                       s.deadline AS deadline,
                                       s.closing_date AS closing_date
                                ORDER BY s.name
                                LIMIT 10
                            """)
                            
                            fallback_schemes = []
                            for record in all_schemes_result:
                                fallback_schemes.append({
                                    'id': record['id'],
                                    'name': record['name'],
                                    'description_text': record.get('description_text', ''),
                                    'source': record.get('source', ''),
                                    'last_updated': record.get('last_updated', ''),
                                    'application_deadline': record.get('application_deadline'),
                                    'deadline': record.get('deadline'),
                                    'closing_date': record.get('closing_date'),
                                    'similarity_score': 0.65
                                })
                            
                            if fallback_schemes:
                                scheme_ids = [s['id'] for s in fallback_schemes]
                                subgraph = extract_subgraph(scheme_ids)
                                context = {
                                    'query': query,
                                    'intent': intent_info,
                                    'schemes': subgraph.get('schemes', []),
                                    'similarity_scores': {s['id']: s['similarity_score'] for s in fallback_schemes}
                                }
                                return {
                                    'is_out_of_domain': False,
                                    'context': context
                                }
                        except Exception as fallback_error:
                            logger.error(f"Error in fallback: {fallback_error}", exc_info=True)
                    
                    logger.warning(f"Database has {total_schemes} schemes but vector search returned none. Check vector indexes and embeddings.")
                    return {
                        'is_out_of_domain': False,
                        'context': {
                            'schemes': [],
                            'intent': intent_info,
                            'message': f'Found {total_schemes} schemes in database but vector search failed. Try asking: "What schemes are available?" or "List all disability schemes".'
                        }
                    }
        except ServiceUnavailable as e:
            # Clean logging for connection failures (Mock Mode trigger)
            logger.warning(f"Neo4j Connection Failed: {e}")
            return {
                'is_out_of_domain': False,
                'context': {
                    'schemes': [],
                    'intent': intent_info,
                    'message': 'Unable to connect to database. Please ensure Neo4j is running.'
                }
            }
        except Exception as e:
            logger.error(f"Error checking database: {e}", exc_info=True)
            return {
                'is_out_of_domain': False,
                'context': {
                    'schemes': [],
                    'intent': intent_info,
                    'message': 'Unable to connect to database. Please ensure Neo4j is running.'
                }
            }
    
    # Step 5: Extract scheme IDs
    scheme_ids = [scheme['id'] for scheme in similar_schemes]
    
    # Step 6: Extract subgraph for relevant schemes
    subgraph = extract_subgraph(scheme_ids)
    
    # Step 7: Assemble context
    context = {
        'query': query,
        'intent': intent_info,
        'schemes': subgraph.get('schemes', []),
        'similarity_scores': {s['id']: s['similarity_score'] for s in similar_schemes}
    }
    
    return {
        'is_out_of_domain': False,
        'context': context
    }
