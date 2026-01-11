"""
Data Ingestion Script for GraphRAG Chatbot
This script:
1. Loads government scheme data
2. Generates embeddings for all nodes
3. Creates nodes in Neo4j with embeddings
4. Creates relationships between nodes

Run this script after setting up Neo4j and creating the schema.
"""

from neo4j import GraphDatabase
from embeddings import encode_text
import json
import os
import uuid
from datetime import datetime
import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Neo4j connection configuration
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Kashish@2510"  # Update with your Neo4j password
NEO4J_DATABASE = "neo4j"

# Initialize Neo4j driver
driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)


def generate_embedding_text(node_data: Dict[str, Any]) -> str:
    """
    Generate text for embedding from node data.
    Combines relevant fields into a single text string.
    
    Args:
        node_data: Dictionary with node properties
    
    Returns:
        Combined text string for embedding
    """
    parts = []
    
    # Add name
    if 'name' in node_data:
        parts.append(node_data['name'])
    
    # Add description
    if 'description_text' in node_data:
        parts.append(node_data['description_text'])
    
    # Add additional context
    if 'amount' in node_data:
        parts.append(f"amount: {node_data['amount']}")
    
    if 'age_min' in node_data or 'age_max' in node_data:
        age_parts = []
        if 'age_min' in node_data:
            age_parts.append(f"minimum age {node_data['age_min']}")
        if 'age_max' in node_data:
            age_parts.append(f"maximum age {node_data['age_max']}")
        if age_parts:
            parts.append(" ".join(age_parts))
    
    if 'income_max' in node_data:
        parts.append(f"maximum income {node_data['income_max']}")
    
    if 'disability_percent_min' in node_data:
        parts.append(f"disability percentage {node_data['disability_percent_min']}")
    
    return " ".join(parts)


def create_scheme_node(session, scheme_data: Dict[str, Any]) -> str:
    """
    Create a Scheme node with embedding.
    
    Args:
        session: Neo4j session
        scheme_data: Dictionary with scheme properties
    
    Returns:
        Scheme ID
    """
    # Generate embedding text
    embedding_text = generate_embedding_text(scheme_data)
    
    # Encode to embedding
    embedding = encode_text(embedding_text)
    
    # Generate ID if not present
    scheme_id = scheme_data.get('id', f"scheme_{uuid.uuid4().hex[:8]}")
    
    # Create node
    session.run("""
        CREATE (s:Scheme {
            id: $id,
            name: $name,
            description_text: $description_text,
            source: $source,
            last_updated: $last_updated,
            application_deadline: $application_deadline,
            deadline: $deadline,
            closing_date: $closing_date,
            embedding: $embedding
        })
    """,
        id=scheme_id,
        name=scheme_data['name'],
        description_text=scheme_data.get('description_text', ''),
        source=scheme_data.get('source', ''),
        last_updated=scheme_data.get('last_updated', datetime.now().isoformat()),
        application_deadline=scheme_data.get('application_deadline'),
        deadline=scheme_data.get('deadline'),
        closing_date=scheme_data.get('closing_date'),
        embedding=embedding
    )
    
    logger.info(f"Created Scheme node: {scheme_data['name']} (ID: {scheme_id})")
    return scheme_id


def create_disability_type_node(session, disability_data: Dict[str, Any]) -> str:
    """Create a DisabilityType node with embedding."""
    embedding_text = generate_embedding_text(disability_data)
    embedding = encode_text(embedding_text)
    
    disability_id = disability_data.get('id', f"disability_{uuid.uuid4().hex[:8]}")
    
    session.run("""
        CREATE (d:DisabilityType {
            id: $id,
            name: $name,
            description_text: $description_text,
            source: $source,
            last_updated: $last_updated,
            embedding: $embedding
        })
    """,
        id=disability_id,
        name=disability_data['name'],
        description_text=disability_data.get('description_text', ''),
        source=disability_data.get('source', ''),
        last_updated=disability_data.get('last_updated', datetime.now().isoformat()),
        embedding=embedding
    )
    
    logger.info(f"Created DisabilityType node: {disability_data['name']} (ID: {disability_id})")
    return disability_id


def create_benefit_node(session, benefit_data: Dict[str, Any]) -> str:
    """Create a Benefit node with embedding."""
    embedding_text = generate_embedding_text(benefit_data)
    embedding = encode_text(embedding_text)
    
    benefit_id = benefit_data.get('id', f"benefit_{uuid.uuid4().hex[:8]}")
    
    session.run("""
        CREATE (b:Benefit {
            id: $id,
            name: $name,
            description_text: $description_text,
            amount: $amount,
            source: $source,
            last_updated: $last_updated,
            embedding: $embedding
        })
    """,
        id=benefit_id,
        name=benefit_data['name'],
        description_text=benefit_data.get('description_text', ''),
        amount=benefit_data.get('amount', ''),
        source=benefit_data.get('source', ''),
        last_updated=benefit_data.get('last_updated', datetime.now().isoformat()),
        embedding=embedding
    )
    
    logger.info(f"Created Benefit node: {benefit_data['name']} (ID: {benefit_id})")
    return benefit_id


def create_eligibility_node(session, eligibility_data: Dict[str, Any]) -> str:
    """Create an Eligibility node with embedding."""
    embedding_text = generate_embedding_text(eligibility_data)
    embedding = encode_text(embedding_text)
    
    eligibility_id = eligibility_data.get('id', f"eligibility_{uuid.uuid4().hex[:8]}")
    
    session.run("""
        CREATE (e:Eligibility {
            id: $id,
            name: $name,
            description_text: $description_text,
            age_min: $age_min,
            age_max: $age_max,
            income_max: $income_max,
            disability_percent_min: $disability_percent_min,
            source: $source,
            last_updated: $last_updated,
            embedding: $embedding
        })
    """,
        id=eligibility_id,
        name=eligibility_data.get('name', ''),
        description_text=eligibility_data.get('description_text', ''),
        age_min=eligibility_data.get('age_min'),
        age_max=eligibility_data.get('age_max'),
        income_max=eligibility_data.get('income_max'),
        disability_percent_min=eligibility_data.get('disability_percent_min'),
        source=eligibility_data.get('source', ''),
        last_updated=eligibility_data.get('last_updated', datetime.now().isoformat()),
        embedding=embedding
    )
    
    logger.info(f"Created Eligibility node: {eligibility_data.get('name', eligibility_id)} (ID: {eligibility_id})")
    return eligibility_id


def create_document_node(session, document_data: Dict[str, Any]) -> str:
    """Create a Document node."""
    document_id = document_data.get('id', f"document_{uuid.uuid4().hex[:8]}")
    
    session.run("""
        CREATE (doc:Document {
            id: $id,
            name: $name,
            description_text: $description_text,
            document_type: $document_type,
            source: $source,
            last_updated: $last_updated
        })
    """,
        id=document_id,
        name=document_data['name'],
        description_text=document_data.get('description_text', ''),
        document_type=document_data.get('document_type', ''),
        source=document_data.get('source', ''),
        last_updated=document_data.get('last_updated', datetime.now().isoformat())
    )
    
    logger.info(f"Created Document node: {document_data['name']} (ID: {document_id})")
    return document_id


def create_application_process_node(session, process_data: Dict[str, Any]) -> str:
    """Create an ApplicationProcess node with embedding."""
    embedding_text = generate_embedding_text(process_data)
    embedding = encode_text(embedding_text)
    
    process_id = process_data.get('id', f"process_{uuid.uuid4().hex[:8]}")
    
    session.run("""
        CREATE (ap:ApplicationProcess {
            id: $id,
            name: $name,
            description_text: $description_text,
            steps: $steps,
            source: $source,
            last_updated: $last_updated,
            embedding: $embedding
        })
    """,
        id=process_id,
        name=process_data['name'],
        description_text=process_data.get('description_text', ''),
        steps=process_data.get('steps', []),
        source=process_data.get('source', ''),
        last_updated=process_data.get('last_updated', datetime.now().isoformat()),
        embedding=embedding
    )
    
    logger.info(f"Created ApplicationProcess node: {process_data['name']} (ID: {process_id})")
    return process_id


def create_government_body_node(session, body_data: Dict[str, Any]) -> str:
    """Create a GovernmentBody node."""
    body_id = body_data.get('id', f"gov_body_{uuid.uuid4().hex[:8]}")
    
    session.run("""
        CREATE (gb:GovernmentBody {
            id: $id,
            name: $name,
            description_text: $description_text,
            contact: $contact,
            source: $source,
            last_updated: $last_updated
        })
    """,
        id=body_id,
        name=body_data['name'],
        description_text=body_data.get('description_text', ''),
        contact=body_data.get('contact', ''),
        source=body_data.get('source', ''),
        last_updated=body_data.get('last_updated', datetime.now().isoformat())
    )
    
    logger.info(f"Created GovernmentBody node: {body_data['name']} (ID: {body_id})")
    return body_id


def create_portal_node(session, portal_data: Dict[str, Any]) -> str:
    """Create a Portal node."""
    portal_id = portal_data.get('id', f"portal_{uuid.uuid4().hex[:8]}")
    
    session.run("""
        CREATE (p:Portal {
            id: $id,
            name: $name,
            url: $url,
            description_text: $description_text,
            source: $source,
            last_updated: $last_updated
        })
    """,
        id=portal_id,
        name=portal_data['name'],
        url=portal_data.get('url', ''),
        description_text=portal_data.get('description_text', ''),
        source=portal_data.get('source', ''),
        last_updated=portal_data.get('last_updated', datetime.now().isoformat())
    )
    
    logger.info(f"Created Portal node: {portal_data['name']} (ID: {portal_id})")
    return portal_id


def create_helpline_node(session, helpline_data: Dict[str, Any]) -> str:
    """Create a Helpline node."""
    helpline_id = helpline_data.get('id', f"helpline_{uuid.uuid4().hex[:8]}")
    
    session.run("""
        CREATE (h:Helpline {
            id: $id,
            name: $name,
            number: $number,
            description_text: $description_text,
            source: $source,
            last_updated: $last_updated
        })
    """,
        id=helpline_id,
        name=helpline_data['name'],
        number=helpline_data.get('number', ''),
        description_text=helpline_data.get('description_text', ''),
        source=helpline_data.get('source', ''),
        last_updated=helpline_data.get('last_updated', datetime.now().isoformat())
    )
    
    logger.info(f"Created Helpline node: {helpline_data['name']} (ID: {helpline_id})")
    return helpline_id


def create_relationship(session, from_node_type: str, from_node_id: str, 
                       rel_type: str, to_node_type: str, to_node_id: str):
    """Create a relationship between two nodes."""
    session.run(f"""
        MATCH (a:{from_node_type} {{id: $from_id}})
        MATCH (b:{to_node_type} {{id: $to_id}})
        CREATE (a)-[:{rel_type}]->(b)
    """,
        from_id=from_node_id,
        to_id=to_node_id
    )
    
    logger.info(f"Created relationship: {from_node_type}({from_node_id}) -[:{rel_type}]-> {to_node_type}({to_node_id})")


def load_real_data_from_json():
    """
    Load real scheme data from the gov-schemes-project and transform it into graph structure.
    """
    # Path to the shared data file
    data_path = "C:/Users/Aditya/Documents/buildthon/buildthon/gov-schemes-project/data/disability_schemes.json"
    
    if not os.path.exists(data_path):
        logger.warning(f"Real data file not found at {data_path}. Falling back to sample_data.json.")
        return load_sample_data()
        
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            
        logger.info(f"Loaded {len(raw_data.get('schemes', []))} schemes from source JSON.")
        
        # Initialize graph structure
        graph_data = {
            "schemes": [],
            "disability_types": [],
            "benefits": [],
            "eligibility": [],
            "documents": [],
            "application_processes": [],
            "government_bodies": [],
            "portals": [],
            "helplines": [],
            "relationships": []
        }
        
        # Helper to deduplicate nodes
        # Map: "NodeName" -> NodeID
        seen_nodes = {
            "disability": {},
            "benefit": {},
            "eligibility": {},
            "document": {}
        }
        
        for item in raw_data.get("schemes", []):
            # 1. Create Scheme Node
            scheme_id = f"scheme_{uuid.uuid4().hex[:8]}"
            scheme_node = {
                "id": scheme_id,
                "name": item.get("name"),
                "description_text": item.get("description"),
                "source": item.get("apply_link", ""),
                "deadline": item.get("deadline"),
                "closing_date": item.get("deadline"), # Map deadline to closing_date as well
                "last_updated": item.get("validity_period", datetime.now().isoformat())
            }
            graph_data["schemes"].append(scheme_node)
            
            # 2. Extract Disability Type
            dtype = item.get("disability_type", "General")
            if dtype not in seen_nodes["disability"]:
                d_id = f"disability_{uuid.uuid4().hex[:8]}"
                d_node = {
                    "id": d_id,
                    "name": dtype.replace("_", " ").title(),
                    "description_text": f"Schemes for {dtype.replace('_', ' ')}"
                }
                graph_data["disability_types"].append(d_node)
                seen_nodes["disability"][dtype] = d_id
            
            # Link Scheme -> Disability
            graph_data["relationships"].append({
                "from": scheme_id,
                "to": seen_nodes["disability"][dtype],
                "type": "FOR_DISABILITY"
            })
            
            # 3. Extract Benefit (from text)
            benefit_text = item.get("benefits", "Financial Assistance")
            # Simple deduping by full text might be too strict, but okay for now
            if benefit_text not in seen_nodes["benefit"]:
                b_id = f"benefit_{uuid.uuid4().hex[:8]}"
                b_node = {
                    "id": b_id,
                    "name": "Benefit Details", # Generic name
                    "description_text": benefit_text,
                    "amount": "" # Parsing amount is complex, leaving blank
                }
                graph_data["benefits"].append(b_node)
                seen_nodes["benefit"][benefit_text] = b_id
                
            # Link Scheme -> Benefit
            graph_data["relationships"].append({
                "from": scheme_id,
                "to": seen_nodes["benefit"][benefit_text],
                "type": "HAS_BENEFIT"
            })
            
            # 4. Extract Eligibility (from text)
            elig_text = item.get("eligibility", "General Eligibility")
            if elig_text not in seen_nodes["eligibility"]:
                e_id = f"eligibility_{uuid.uuid4().hex[:8]}"
                e_node = {
                    "id": e_id,
                    "name": "Eligibility Criteria",
                    "description_text": elig_text
                }
                graph_data["eligibility"].append(e_node)
                seen_nodes["eligibility"][elig_text] = e_id
            
            # Link Scheme -> Eligibility
            graph_data["relationships"].append({
                "from": scheme_id,
                "to": seen_nodes["eligibility"][elig_text],
                "type": "HAS_ELIGIBILITY"
            })
            
            # 5. Extract Documents (basic string match)
            # Not present in simple JSON, skipping or inferring?
            # Let's skip extracting specific documents to avoid noise for now.
            
        return graph_data
        
    except Exception as e:
        logger.error(f"Failed to load real data: {e}")
        return load_sample_data()

def load_sample_data():
    """
    Load sample government scheme data.
    Reserved as fallback.
    """
    try:
        with open('sample_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "schemes": [], "disability_types": [], "benefits": [], 
            "eligibility": [], "documents": [], "application_processes": [], 
            "government_bodies": [], "portals": [], "helplines": [], "relationships": []
        }
        
def create_vector_index(session):
    """Create vector index for Scheme nodes."""
    try:
        # Check if index exists
        result = session.run("SHOW INDEXES")
        indexes = [record["name"] for record in result]
        
        if "scheme_embedding_index" not in indexes:
            logger.info("Creating vector index 'scheme_embedding_index'...")
            session.run("""
                CREATE VECTOR INDEX scheme_embedding_index IF NOT EXISTS
                FOR (s:Scheme) ON (s.embedding)
                OPTIONS {indexConfig: {
                    `vector.dimensions`: 384,
                    `vector.similarity_function`: 'cosine'
                }}
            """)
            logger.info("Vector index created successfully")
        else:
            logger.info("Vector index 'scheme_embedding_index' already exists")
    except Exception as e:
        logger.error(f"Error creating vector index: {e}")

def ingest_data():
    """Main function to ingest data into Neo4j."""
    logger.info("Starting data ingestion...")
    
    # Load data
    driver.verify_connectivity()
    
    # Load data (Real data from gov-schemes-project)
    data = load_real_data_from_json()
    
    with driver.session(database=NEO4J_DATABASE) as session:
        # Clear existing data
        logger.warning("Clearing existing data...")
        session.run("MATCH (n) DETACH DELETE n")
        
        # Create Vector Index
        create_vector_index(session)
        
        # Create nodes
        node_id_map = {}
        
        # Create DisabilityType nodes
        for disability in data.get('disability_types', []):
            disability_id = create_disability_type_node(session, disability)
            node_id_map[disability.get('id', disability['name'])] = ('DisabilityType', disability_id)
        
        # Create Benefit nodes
        for benefit in data.get('benefits', []):
            benefit_id = create_benefit_node(session, benefit)
            node_id_map[benefit.get('id', benefit['name'])] = ('Benefit', benefit_id)
        
        # Create Eligibility nodes
        for eligibility in data.get('eligibility', []):
            eligibility_id = create_eligibility_node(session, eligibility)
            node_id_map[eligibility.get('id', eligibility.get('name', 'eligibility'))] = ('Eligibility', eligibility_id)
        
        # Create Document nodes
        for document in data.get('documents', []):
            document_id = create_document_node(session, document)
            node_id_map[document.get('id', document['name'])] = ('Document', document_id)
        
        # Create ApplicationProcess nodes
        for process in data.get('application_processes', []):
            process_id = create_application_process_node(session, process)
            node_id_map[process.get('id', process['name'])] = ('ApplicationProcess', process_id)
        
        # Create GovernmentBody nodes
        for body in data.get('government_bodies', []):
            body_id = create_government_body_node(session, body)
            node_id_map[body.get('id', body['name'])] = ('GovernmentBody', body_id)
        
        # Create Portal nodes
        for portal in data.get('portals', []):
            portal_id = create_portal_node(session, portal)
            node_id_map[portal.get('id', portal['name'])] = ('Portal', portal_id)
        
        # Create Helpline nodes
        for helpline in data.get('helplines', []):
            helpline_id = create_helpline_node(session, helpline)
            node_id_map[helpline.get('id', helpline['name'])] = ('Helpline', helpline_id)
        
        # Create Scheme nodes (after related nodes are created)
        for scheme in data.get('schemes', []):
            scheme_id = create_scheme_node(session, scheme)
            node_id_map[scheme.get('id', scheme['name'])] = ('Scheme', scheme_id)
        
        # Create relationships
        for rel in data.get('relationships', []):
            from_key = rel['from']
            to_key = rel['to']
            rel_type = rel['type']
            
            if from_key in node_id_map and to_key in node_id_map:
                from_node_type, from_node_id = node_id_map[from_key]
                to_node_type, to_node_id = node_id_map[to_key]
                
                create_relationship(session, from_node_type, from_node_id, 
                                 rel_type, to_node_type, to_node_id)
        
        logger.info("Data ingestion completed successfully!")
    
    driver.close()


if __name__ == "__main__":
    try:
        ingest_data()
    except Exception as e:
        logger.error(f"Error during data ingestion: {e}", exc_info=True)
        raise
