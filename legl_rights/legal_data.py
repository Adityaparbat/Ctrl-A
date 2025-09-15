digital_rights_data = {
    "rights": {
        "digital_accessibility": {
            "description": ("Right to equal access to digital information, products, and services "
                            "for disabled persons, including assistive technologies."),
            "applicable_laws": [
                "RPWD Act Section 34 (India)",
                "Americans with Disabilities Act (ADA) Title III (USA)",
                "Web Accessibility Directive (EU)",
                "UN Convention on the Rights of Persons with Disabilities (UN CRPD) Article 9"
            ],
            "applicable_regions": ["India", "USA", "EU", "Global"],
            "enforcement_authority": {
                "India": "Department of Empowerment of Persons with Disabilities",
                "USA": "U.S. Department of Justice, Civil Rights Division",
                "EU": "European Commission, Directorate-General for Digital Single Market"
            },
            "how_to_file_complaint": {
                "India": "National Portal for Persons With Disabilities complaint system",
                "USA": "File complaint via ADA.gov Civil Rights Complaint portal",
                "EU": "Contact local Equality Bodies or European Commission"
            },
            "contact_info": {
                "India": "https://disabilityaffairs.gov.in",
                "USA": "https://www.ada.gov",
                "EU": "https://ec.europa.eu/digital-single-market/en/web-accessibility"
            },
            "resources": [
                "WCAG 2.1 accessibility guidelines",
                "Screen reader compatibility requirements",
                "Captioning policies for audio/video content"
            ]
        },
        "data_privacy": {
            "description": ("Right to control personal data collected by online services, "
                            "including transparency, consent, and deletion rights."),
            "applicable_laws": [
                "Data Protection Act 2018 (India - pending enforcement)",
                "General Data Protection Regulation (GDPR - EU)",
                "California Consumer Privacy Act (CCPA - USA)"
            ],
            "applicable_regions": ["India", "EU", "USA"],
            "enforcement_authority": {
                "India": "Ministry of Electronics and Information Technology (MeitY)",
                "EU": "European Data Protection Board",
                "USA": "California Attorney General's Office"
            },
            "how_to_file_complaint": {
                "India": "MeitY complaint portal or helpline",
                "EU": "National Data Protection Authorities",
                "USA": "File complaint with California AG or FTC"
            },
            "contact_info": {
                "India": "https://meity.gov.in",
                "EU": "https://edpb.europa.eu",
                "USA": "https://oag.ca.gov/privacy"
            },
            "resources": [
                "User consent management tools",
                "Right to access and portability of data",
                "Data breach notification requirements"
            ]
        },
        "digital_inclusion": {
            "description": ("Right to affordable internet access, devices, and digital literacy programs "
                            "to reduce the digital divide."),
            "applicable_laws": [
                "National Digital Inclusion Policy (India - Draft)",
                "United Nations Sustainable Development Goals (SDG 9 - Industry, Innovation, and Infrastructure)",
                "FCC Lifeline Program (USA)"
            ],
            "applicable_regions": ["India", "USA", "Global"],
            "enforcement_authority": {
                "India": "Telecom Regulatory Authority of India (TRAI)",
                "USA": "Federal Communications Commission (FCC)",
                "Global": "International Telecommunication Union (ITU)"
            },
            "how_to_file_complaint": {
                "India": "TRAI customer grievance system",
                "USA": "FCC consumer complaint center",
                "Global": "ITU complaint channels"
            },
            "contact_info": {
                "India": "https://trai.gov.in",
                "USA": "https://consumercomplaints.fcc.gov",
                "Global": "https://www.itu.int/en/ITU-D/Commission/Pages/human-right.aspx"
            },
            "resources": [
                "Subsidized internet schemes",
                "Digital literacy workshops",
                "Assistive devices distribution"
            ]
        },
        "net_neutrality": {
            "description": ("Right to nondiscriminatory internet access where ISPs treat all data equally, "
                            "without throttling or blocking."),
            "applicable_laws": [
                "Net Neutrality Rules by TRAI (India)",
                "FCC Open Internet Order (2015 - USA, currently challenged)",
                "European Union Open Internet Regulation"
            ],
            "applicable_regions": ["India", "USA", "EU"],
            "enforcement_authority": {
                "India": "TRAI",
                "USA": "Federal Communications Commission (FCC)",
                "EU": "Body of European Regulators for Electronic Communications (BEREC)"
            },
            "how_to_file_complaint": {
                "India": "TRAI consumer complaint portal",
                "USA": "FCC complaint portal",
                "EU": "Report to national telecommunication regulators"
            },
            "contact_info": {
                "India": "https://trai.gov.in",
                "USA": "https://www.fcc.gov/complaints",
                "EU": "https://berec.europa.eu"
            },
            "resources": [
                "Open internet principles",
                "ISP transparency requirements",
                "Policies on paid prioritization"
            ]
        },
        "online_safety_and_cyberbullying": {
            "description": ("Right to protection from online harassment, cyberbullying, and abuse, "
                            "with accessible reporting and redressal mechanisms."),
            "applicable_laws": [
                "Information Technology Act 2000 (India) Section 66A & 66E (amended)",
                "Cyberbullying laws in various states (USA)",
                "EU Directive on combating abuse online"
            ],
            "applicable_regions": ["India", "USA", "EU"],
            "enforcement_authority": {
                "India": "Ministry of Home Affairs, Cyber Crime Cells",
                "USA": "Local and Federal law enforcement",
                "EU": "European Cybercrime Centre (EC3)"
            },
            "how_to_file_complaint": {
                "India": "National Cyber Crime Reporting Portal",
                "USA": "Report to FBI Internet Crime Complaint Center (IC3)",
                "EU": "Contact EC3 or local police"
            },
            "contact_info": {
                "India": "https://cybercrime.gov.in",
                "USA": "https://www.ic3.gov",
                "EU": "https://ec.europa.eu/home-affairs/what-we-do/policies/european-cybercrime-centre-ec3_en"
            },
            "resources": [
                "Safe internet usage guidelines",
                "Reporting cyberbullying",
                "Support groups and counseling"
            ]
        },
        # Add additional digital rights as needed
    }
}
def clean_text_for_cypher(text):
    return text.replace("'", "\\'").replace('"', '\\"')

cypher_queries = []

# Create nodes & relationships
for right_name, right_info in digital_rights_data["rights"].items():
    right_desc = clean_text_for_cypher(right_info.get("description", ""))
    # Right node
    cypher_queries.append(f"MERGE (r:Right {{name: '{right_name}'}}) SET r.description='{right_desc}';")
    
    # Applicable Laws nodes and relationships
    for law in right_info.get("applicable_laws", []):
        law_clean = clean_text_for_cypher(law)
        cypher_queries.append(f"MERGE (l:Law {{name: '{law_clean}'}});")
        cypher_queries.append(f"MATCH (r:Right {{name: '{right_name}'}}), (l:Law {{name: '{law_clean}'}}) MERGE (r)-[:APPLIES_UNDER]->(l);")
    
    # Regions nodes and relationships
    for region in right_info.get("applicable_regions", []):
        cypher_queries.append(f"MERGE (rg:Region {{name: '{region}'}});")
        cypher_queries.append(f"MATCH (r:Right {{name: '{right_name}'}}), (rg:Region {{name: '{region}'}}) MERGE (r)-[:APPLIES_TO]->(rg);")
        
        # Enforcement Authority nodes and relationships
        auth = right_info.get("enforcement_authority", {}).get(region)
        if auth:
            auth_clean = clean_text_for_cypher(auth)
            cypher_queries.append(f"MERGE (a:Authority {{name: '{auth_clean}', region: '{region}'}});")
            cypher_queries.append(f"MATCH (r:Right {{name: '{right_name}'}}), (a:Authority {{name: '{auth_clean}'}}) MERGE (r)-[:ENFORCED_BY]->(a);")
        
        # Complaint process and contact info as properties on relationships or nodes
        complaint = right_info.get("how_to_file_complaint", {}).get(region)
        contact = right_info.get("contact_info", {}).get(region)
        if complaint or contact:
            # Create a Process node for complaint process
            proc_name = f"ComplaintProcess_{right_name}_{region}"
            complaint_clean = clean_text_for_cypher(complaint or "")
            contact_clean = clean_text_for_cypher(contact or "")
            cypher_queries.append(f"MERGE (p:Process {{name: '{proc_name}'}}) SET p.complaint='{complaint_clean}', p.contact='{contact_clean}';")
            # Link Right -> Process
            cypher_queries.append(f"MATCH (r:Right {{name: '{right_name}'}}), (p:Process {{name: '{proc_name}'}}) MERGE (r)-[:HAS_COMPLAINT_PROCESS]->(p);")
            # Link Process -> Region
            cypher_queries.append(f"MATCH (p:Process {{name: '{proc_name}'}}), (rg:Region {{name: '{region}'}}) MERGE (p)-[:CONCERNS]->(rg);")

print("\n".join(cypher_queries))

# Neo4j and query processing imports
from neo4j import GraphDatabase
import re
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from urllib.parse import urlparse

# Initialize FastAPI app
app = FastAPI()

class QueryRequest(BaseModel):
    question: str

class Neo4jConnection:
    def __init__(self, uri: str, username: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
    
    def close(self):
        self.driver.close()
    
    def execute_query(self, query: str, parameters: Dict = None):
        with self.driver.session() as session:
            try:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
            except Exception as e:
                print(f"Error executing query: {e}")
                return []

# Initialize Neo4j connection
def get_neo4j_connection():
    # Try to get credentials from environment variables
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    username = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    
    try:
        return Neo4jConnection(uri, username, password)
    except Exception as e:
        print(f"Failed to connect to Neo4j: {e}")
        return None

def setup_database():
    """Initialize the database with the legal rights data"""
    conn = get_neo4j_connection()
    if not conn:
        print("Cannot connect to Neo4j. Please ensure Neo4j is running and credentials are correct.")
        return False
    
    try:
        # Clear existing data
        conn.execute_query("MATCH (n) DETACH DELETE n")
        
        # Execute all the cypher queries to populate the database
        for query in cypher_queries:
            conn.execute_query(query)
        
        print("Database initialized successfully!")
        return True
    except Exception as e:
        print(f"Error setting up database: {e}")
        return False
    finally:
        conn.close()

def parse_user_query(question: str) -> List[str]:
    """Convert natural language question to Cypher queries"""
    question_lower = question.lower()
    
    # Define query patterns
    queries = []
    
    # Pattern 1: "What are my digital rights?"
    if any(phrase in question_lower for phrase in ["digital rights", "my rights", "what rights"]):
        queries.append("MATCH (r:Right) RETURN r.name as right_name, r.description as description")
    
    # Pattern 2: "What laws apply to [right_name]?"
    elif "laws" in question_lower or "legal" in question_lower:
        right_match = re.search(r'(?:rights?|to)\s+([a-zA-Z_]+)', question_lower)
        if right_match:
            right_name = right_match.group(1)
            queries.append(f"MATCH (r:Right {{name: '{right_name}'}})-[:APPLIES_UNDER]->(l:Law) RETURN l.name as law_name")
        else:
            queries.append("MATCH (r:Right)-[:APPLIES_UNDER]->(l:Law) RETURN r.name as right_name, l.name as law_name")
    
    # Pattern 3: "How do I file a complaint for [right_name]?"
    elif "complaint" in question_lower or "file" in question_lower:
        right_match = re.search(r'(?:for|about)\s+([a-zA-Z_]+)', question_lower)
        if right_match:
            right_name = right_match.group(1)
            queries.append(f"MATCH (r:Right {{name: '{right_name}'}})-[:HAS_COMPLAINT_PROCESS]->(p:Process) RETURN p.complaint as complaint_process, p.contact as contact_info")
        else:
            queries.append("MATCH (r:Right)-[:HAS_COMPLAINT_PROCESS]->(p:Process) RETURN r.name as right_name, p.complaint as complaint_process, p.contact as contact_info")
    
    # Pattern 4: "Who enforces [right_name]?"
    elif "enforce" in question_lower or "authority" in question_lower:
        right_match = re.search(r'(?:for|about)\s+([a-zA-Z_]+)', question_lower)
        if right_match:
            right_name = right_match.group(1)
            queries.append(f"MATCH (r:Right {{name: '{right_name}'}})-[:ENFORCED_BY]->(a:Authority) RETURN a.name as authority_name, a.region as region")
        else:
            queries.append("MATCH (r:Right)-[:ENFORCED_BY]->(a:Authority) RETURN r.name as right_name, a.name as authority_name, a.region as region")
    
    # Pattern 5: "What regions does [right_name] apply to?"
    elif "region" in question_lower or "country" in question_lower or "where" in question_lower:
        right_match = re.search(r'(?:does|for)\s+([a-zA-Z_]+)', question_lower)
        if right_match:
            right_name = right_match.group(1)
            queries.append(f"MATCH (r:Right {{name: '{right_name}'}})-[:APPLIES_TO]->(rg:Region) RETURN rg.name as region_name")
        else:
            queries.append("MATCH (r:Right)-[:APPLIES_TO]->(rg:Region) RETURN r.name as right_name, rg.name as region_name")
    
    # Default: Return all rights
    if not queries:
        queries.append("MATCH (r:Right) RETURN r.name as right_name, r.description as description")
    
    return queries

def format_query_results(results: List[Dict[str, Any]]) -> str:
    """Format query results into a readable response"""
    if not results:
        return "I couldn't find any relevant information for your query. Please try rephrasing your question."
    
    response_parts = []
    
    for result in results:
        if 'right_name' in result and 'description' in result:
            response_parts.append(f"**{result['right_name'].replace('_', ' ').title()}**: {result['description']}")
        
        elif 'law_name' in result:
            response_parts.append(f"• {result['law_name']}")
        
        elif 'complaint_process' in result:
            if result['complaint_process']:
                response_parts.append(f"**Complaint Process**: {result['complaint_process']}")
            if result.get('contact_info'):
                response_parts.append(f"**Contact**: {result['contact_info']}")
        
        elif 'authority_name' in result:
            response_parts.append(f"• {result['authority_name']} ({result.get('region', 'Unknown region')})")
        
        elif 'region_name' in result:
            response_parts.append(f"• {result['region_name']}")
    
    return "\n\n".join(response_parts) if response_parts else "No specific information found."

def answer_user_query(question: str) -> str:
    """Main function to answer user queries about digital rights"""
    try:
        # Parse the user query to generate Cypher queries
        cypher_queries = parse_user_query(question)
        
        # Execute queries and collect results
        all_results = []
        conn = get_neo4j_connection()
        
        if not conn:
            return "I'm unable to connect to the legal database. Please ensure the database is running."
        
        try:
            for query in cypher_queries:
                results = conn.execute_query(query)
                all_results.extend(results)
            
            # Format and return the response
            return format_query_results(all_results)
        
        finally:
            conn.close()
    
    except Exception as e:
        return f"I encountered an error while processing your question: {str(e)}"

@app.post("/ask")
def ask_rights(query: QueryRequest):
    """FastAPI endpoint to answer questions about digital rights"""
    try:
        answer = answer_user_query(query.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Digital Rights Legal Database API",
        "endpoints": {
            "/ask": "POST - Ask questions about digital rights",
            "/setup": "GET - Initialize the database",
            "/health": "GET - Check API health"
        }
    }

@app.get("/setup")
def setup_endpoint():
    """Endpoint to initialize the database"""
    success = setup_database()
    return {"status": "success" if success else "failed", "message": "Database setup completed" if success else "Database setup failed"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    conn = get_neo4j_connection()
    if conn:
        conn.close()
        return {"status": "healthy", "database": "connected"}
    else:
        return {"status": "unhealthy", "database": "disconnected"}

if __name__ == "__main__":
    import uvicorn
    print("Starting Digital Rights Legal Database API...")
    print("Available endpoints:")
    print("- POST /ask - Ask questions about digital rights")
    print("- GET /setup - Initialize the database")
    print("- GET /health - Check API health")
    uvicorn.run(app, port=8000)
