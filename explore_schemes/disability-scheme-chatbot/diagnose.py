"""
Diagnostic Script for GraphRAG Chatbot
This script checks the database state and helps identify issues.
"""

from neo4j import GraphDatabase
from embeddings import encode_text
import logging
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Neo4j connection configuration (update with your settings)
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Kashish@2510"  # Update with your Neo4j password
NEO4J_DATABASE = "neo4j"

def check_database():
    """Check database state and diagnose issues."""
    print("=" * 60)
    print("GraphRAG Chatbot Diagnostic Tool")
    print("=" * 60)
    
    try:
        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )
        print(f"[OK] Connected to Neo4j at {NEO4J_URI}")
        
        with driver.session(database=NEO4J_DATABASE) as session:
            # 1. Check if Scheme nodes exist
            print("\n1. Checking Scheme nodes...")
            result = session.run("MATCH (s:Scheme) RETURN count(s) AS count")
            count_record = result.single()
            scheme_count = count_record['count'] if count_record else 0
            
            if scheme_count == 0:
                print(f"  [ERROR] No Scheme nodes found in database!")
                print(f"     Solution: Run 'python data_ingestion.py' to load data")
                return False
            else:
                print(f"  [OK] Found {scheme_count} Scheme nodes")
            
            # 2. Check if schemes have embeddings
            print("\n2. Checking embeddings on Scheme nodes...")
            result = session.run("""
                MATCH (s:Scheme)
                WHERE s.embedding IS NOT NULL
                RETURN count(s) AS count
            """)
            count_record = result.single()
            embedding_count = count_record['count'] if count_record else 0
            
            if embedding_count == 0:
                print(f"  [ERROR] No schemes have embeddings!")
                print(f"     Solution: Re-run 'python data_ingestion.py' to generate embeddings")
                return False
            else:
                print(f"  [OK] Found {embedding_count} schemes with embeddings")
            
            # 3. Check vector indexes
            print("\n3. Checking vector indexes...")
            try:
                result = session.run("SHOW INDEXES")
                indexes = []
                for record in result:
                    index_name = record.get('name', '')
                    index_type = record.get('type', '')
                    if 'vector' in index_type.lower() or 'embedding' in index_name.lower():
                        indexes.append({
                            'name': index_name,
                            'type': index_type,
                            'state': record.get('state', 'UNKNOWN')
                        })
                
                if not indexes:
                    print(f"  [WARNING] No vector indexes found!")
                    print(f"     Solution: Run 'neo4j_schema.cypher' in Neo4j Browser to create indexes")
                    print(f"     Note: Vector indexes require Neo4j 5.x+")
                else:
                    print(f"  [OK] Found {len(indexes)} vector index(es):")
                    for idx in indexes:
                        print(f"     - {idx['name']} ({idx['type']}, state: {idx['state']})")
                        
                        # Check if the index exists for Scheme nodes
                        if 'scheme' in idx['name'].lower():
                            # Try to query the index
                            try:
                                test_embedding = encode_text("test query")
                                test_result = session.run("""
                                    CALL db.index.vector.queryNodes($index_name, 1, $embedding)
                                    YIELD node, score
                                    RETURN count(node) AS count
                                """, index_name=idx['name'], embedding=test_embedding)
                                test_record = test_result.single()
                                if test_record:
                                    print(f"       [OK] Index is queryable")
                                else:
                                    print(f"       [ERROR] Index exists but query failed")
                            except Exception as e:
                                print(f"       [ERROR] Index query failed: {str(e)[:100]}")
            except Exception as e:
                print(f"  [ERROR] checking indexes: {e}")
                print(f"     Note: Vector indexes require Neo4j 5.x+")
            
            # 4. Check relationships
            print("\n4. Checking relationships...")
            result = session.run("""
                MATCH (s:Scheme)-[r]->(n)
                RETURN type(r) AS rel_type, count(r) AS count
                ORDER BY count DESC
            """)
            relationships = []
            for record in result:
                relationships.append({
                    'type': record['rel_type'],
                    'count': record['count']
                })
            
            if not relationships:
                print(f"  [WARNING] No relationships found!")
                print(f"     Solution: Check if data_ingestion.py created relationships correctly")
            else:
                print(f"  [OK] Found {sum(r['count'] for r in relationships)} relationships:")
                for rel in relationships[:5]:  # Show top 5
                    print(f"     - {rel['type']}: {rel['count']} relationships")
            
            # 5. Test vector search
            print("\n5. Testing vector search...")
            test_query = "What schemes are available for persons with disabilities?"
            test_embedding = encode_text(test_query)
            
            try:
                result = session.run("""
                    CALL db.index.vector.queryNodes(
                        'scheme_embedding_index',
                        5,
                        $embedding
                    )
                    YIELD node, score
                    RETURN node.name AS name, score
                    ORDER BY score DESC
                """, embedding=test_embedding)
                
                results = []
                for record in result:
                    results.append({
                        'name': record['name'],
                        'score': float(record['score'])
                    })
                
                if not results:
                    print(f"  [WARNING] Vector search returned no results")
                    print(f"     This might be normal if similarity threshold is too high")
                    print(f"     Try lowering SIMILARITY_THRESHOLD in graphrag.py")
                else:
                    print(f"  [OK] Vector search found {len(results)} results:")
                    for res in results[:3]:
                        print(f"     - {res['name']} (similarity: {res['score']:.3f})")
            except Exception as e:
                error_msg = str(e)
                if 'does not exist' in error_msg.lower():
                    print(f"  [ERROR] Vector index 'scheme_embedding_index' does not exist!")
                    print(f"     Solution: Run 'neo4j_schema.cypher' to create the index")
                elif 'vector' in error_msg.lower():
                    print(f"  [ERROR] Vector search failed: {error_msg[:100]}")
                    print(f"     Note: Vector indexes require Neo4j 5.x+")
                else:
                    print(f"  [ERROR] Vector search failed: {error_msg[:100]}")
            
            # 6. Sample scheme data
            print("\n6. Sample scheme data...")
            result = session.run("""
                MATCH (s:Scheme)
                RETURN s.name AS name, 
                       CASE WHEN s.embedding IS NOT NULL THEN 'Yes' ELSE 'No' END AS has_embedding
                LIMIT 3
            """)
            
            schemes = []
            for record in result:
                schemes.append({
                    'name': record['name'],
                    'has_embedding': record['has_embedding']
                })
            
            if schemes:
                print(f"  [OK] Sample schemes:")
                for scheme in schemes:
                    print(f"     - {scheme['name']} (embedding: {scheme['has_embedding']})")
            else:
                print(f"  [ERROR] No schemes found!")
        
        driver.close()
        print("\n" + "=" * 60)
        print("Diagnostic complete!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Failed to connect to Neo4j")
        print(f"   Error: {str(e)}")
        print(f"\n   Solutions:")
        print(f"   1. Ensure Neo4j is running: 'neo4j status'")
        print(f"   2. Check NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD in this script")
        print(f"   3. Verify Neo4j connection in Neo4j Browser")
        return False

if __name__ == "__main__":
    check_database()
