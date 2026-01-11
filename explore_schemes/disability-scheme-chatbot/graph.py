"""
Graph RAG Module - Neo4j Database Queries
This module handles all Cypher queries to retrieve scheme information
from the Neo4j graph database using Graph RAG architecture.

Node Types: Scheme, Disability, Benefit, Eligibility, Document, Department
Relationships: FOR, PROVIDES, REQUIRES, ELIGIBLE_IF
"""

from neo4j import GraphDatabase
import os

# Neo4j connection configuration (stable on Windows)
# Use the same URI as shown in Neo4j Desktop for your local instance
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
NEO4J_USER = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "Kashish@2510")

# Initialize Neo4j driver
driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)


def get_all_schemes():
    """
    Retrieve all government schemes with basic information.
    Returns: List of dictionaries with scheme name and state.
    """
    with driver.session(database="neo4j") as session:
        result = session.run("""
            MATCH (s:Scheme)
            RETURN s.name AS name, s.state AS state
            ORDER BY s.name
        """)
        return [record.data() for record in result]


def search_schemes_by_keyword(keyword: str):
    """
    Search schemes by keyword (name, state, or description).
    Uses case-insensitive matching.
    """
    keyword_lower = keyword.lower()
    with driver.session(database="neo4j") as session:
        result = session.run("""
            MATCH (s:Scheme)
            WHERE toLower(s.name) CONTAINS $keyword 
               OR toLower(s.state) CONTAINS $keyword
               OR toLower(s.description) CONTAINS $keyword
            RETURN DISTINCT s.name AS name, s.state AS state, s.description AS description
            ORDER BY s.name
            LIMIT 10
        """, keyword=keyword_lower)
        return [record.data() for record in result]


def get_scheme_details(scheme_name: str):
    """
    Get complete details of a specific scheme including:
    - Scheme information
    - Associated disabilities (FOR relationship)
    - Benefits provided (PROVIDES relationship)
    - Eligibility criteria (ELIGIBLE_IF relationship)
    - Required documents (REQUIRES relationship)
    - Department information
    """
    with driver.session(database="neo4j") as session:
        # Get scheme basic info
        scheme_result = session.run("""
            MATCH (s:Scheme)
            WHERE toLower(s.name) CONTAINS $scheme_name
            RETURN s.name AS name, s.state AS state, s.description AS description
            LIMIT 1
        """, scheme_name=scheme_name.lower())
        
        scheme_data = scheme_result.single()
        if not scheme_data:
            return None
        
        scheme_info = dict(scheme_data)
        
        # Get disabilities (FOR relationship)
        disabilities_result = session.run("""
            MATCH (s:Scheme)-[:FOR]->(d:Disability)
            WHERE toLower(s.name) CONTAINS $scheme_name
            RETURN d.name AS name, d.type AS type
        """, scheme_name=scheme_name.lower())
        scheme_info['disabilities'] = [dict(record) for record in disabilities_result]
        
        # Get benefits (PROVIDES relationship)
        benefits_result = session.run("""
            MATCH (s:Scheme)-[:PROVIDES]->(b:Benefit)
            WHERE toLower(s.name) CONTAINS $scheme_name
            RETURN b.name AS name, b.amount AS amount, b.description AS description
        """, scheme_name=scheme_name.lower())
        scheme_info['benefits'] = [dict(record) for record in benefits_result]
        
        # Get eligibility criteria (ELIGIBLE_IF relationship)
        eligibility_result = session.run("""
            MATCH (s:Scheme)-[:ELIGIBLE_IF]->(e:Eligibility)
            WHERE toLower(s.name) CONTAINS $scheme_name
            RETURN e.criteria AS criteria, e.age_min AS age_min, e.age_max AS age_max, 
                   e.income_max AS income_max, e.disability_percent AS disability_percent
        """, scheme_name=scheme_name.lower())
        scheme_info['eligibility'] = [dict(record) for record in eligibility_result]
        
        # Get required documents (REQUIRES relationship)
        documents_result = session.run("""
            MATCH (s:Scheme)-[:REQUIRES]->(doc:Document)
            WHERE toLower(s.name) CONTAINS $scheme_name
            RETURN doc.name AS name, doc.type AS type, doc.description AS description
        """, scheme_name=scheme_name.lower())
        scheme_info['documents'] = [dict(record) for record in documents_result]
        
        # Get department information
        department_result = session.run("""
            MATCH (s:Scheme)-[:ADMINISTERED_BY]->(dept:Department)
            WHERE toLower(s.name) CONTAINS $scheme_name
            RETURN dept.name AS name, dept.contact AS contact
        """, scheme_name=scheme_name.lower())
        dept_data = department_result.single()
        scheme_info['department'] = dict(dept_data) if dept_data else None
        
        return scheme_info


def get_schemes_by_disability(disability_name: str):
    """
    Find all schemes available for a specific disability type.
    Uses FOR relationship to connect schemes to disabilities.
    """
    with driver.session(database="neo4j") as session:
        result = session.run("""
            MATCH (s:Scheme)-[:FOR]->(d:Disability)
            WHERE toLower(d.name) CONTAINS $disability_name
               OR toLower(d.type) CONTAINS $disability_name
            RETURN DISTINCT s.name AS scheme_name, s.state AS state, 
                   d.name AS disability_name, d.type AS disability_type
            ORDER BY s.name
        """, disability_name=disability_name.lower())
        return [record.data() for record in result]


def get_schemes_by_benefit(benefit_keyword: str):
    """
    Find schemes that provide specific benefits.
    Uses PROVIDES relationship.
    """
    with driver.session(database="neo4j") as session:
        result = session.run("""
            MATCH (s:Scheme)-[:PROVIDES]->(b:Benefit)
            WHERE toLower(b.name) CONTAINS $benefit_keyword
               OR toLower(b.description) CONTAINS $benefit_keyword
            RETURN DISTINCT s.name AS scheme_name, s.state AS state,
                   b.name AS benefit_name, b.amount AS amount
            ORDER BY s.name
        """, benefit_keyword=benefit_keyword.lower())
        return [record.data() for record in result]


def get_eligibility_info(scheme_name: str):
    """
    Get detailed eligibility criteria for a scheme.
    Returns age limits, income limits, disability percentage requirements.
    """
    with driver.session(database="neo4j") as session:
        result = session.run("""
            MATCH (s:Scheme)-[:ELIGIBLE_IF]->(e:Eligibility)
            WHERE toLower(s.name) CONTAINS $scheme_name
            RETURN e.criteria AS criteria, e.age_min AS age_min, e.age_max AS age_max,
                   e.income_max AS income_max, e.disability_percent AS disability_percent
        """, scheme_name=scheme_name.lower())
        return [record.data() for record in result]


def get_required_documents(scheme_name: str):
    """
    Get list of documents required for a scheme application.
    Uses REQUIRES relationship.
    """
    with driver.session(database="neo4j") as session:
        result = session.run("""
            MATCH (s:Scheme)-[:REQUIRES]->(doc:Document)
            WHERE toLower(s.name) CONTAINS $scheme_name
            RETURN doc.name AS name, doc.type AS type, doc.description AS description
            ORDER BY doc.name
        """, scheme_name=scheme_name.lower())
        return [record.data() for record in result]


def get_common_required_documents():
    """
    Get a distinct list of documents that are commonly required
    across disability-related government schemes.
    This is used when the user asks general questions like
    \"What documents are required for disability schemes?\"
    without naming a specific scheme.
    """
    with driver.session(database="neo4j") as session:
        result = session.run(
            """
            MATCH (s:Scheme)-[:REQUIRES]->(doc:Document)
            RETURN DISTINCT doc.name AS name, doc.type AS type, doc.description AS description
            ORDER BY doc.name
            """
        )
        return [record.data() for record in result]
