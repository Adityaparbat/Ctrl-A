#!/usr/bin/env python3
"""
Simple Legal Rights API - No database required for basic functionality
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
import re

# Initialize FastAPI app
app = FastAPI(title="Digital Rights Legal Database API", version="1.0.0")

class QueryRequest(BaseModel):
    question: str

# In-memory data structure for digital rights
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
        }
    }
}

def parse_user_query(question: str) -> Dict:
    """Parse user query and return relevant information"""
    question_lower = question.lower()
    
    # Pattern 1: "What are my digital rights?"
    if any(phrase in question_lower for phrase in ["digital rights", "my rights", "what rights", "all rights"]):
        return {"type": "all_rights", "data": digital_rights_data["rights"]}
    
    # Pattern 2: "What laws apply to [right_name]?"
    elif "laws" in question_lower or "legal" in question_lower:
        right_match = re.search(r'(?:rights?|to)\s+([a-zA-Z_]+)', question_lower)
        if right_match:
            right_name = right_match.group(1)
            # Try to find matching right
            for key, value in digital_rights_data["rights"].items():
                if right_name in key.lower():
                    return {"type": "laws", "data": value["applicable_laws"], "right_name": key}
        return {"type": "all_laws", "data": digital_rights_data["rights"]}
    
    # Pattern 3: "How do I file a complaint for [right_name]?"
    elif "complaint" in question_lower or "file" in question_lower:
        right_match = re.search(r'(?:for|about)\s+([a-zA-Z_]+)', question_lower)
        if right_match:
            right_name = right_match.group(1)
            for key, value in digital_rights_data["rights"].items():
                if right_name in key.lower():
                    return {"type": "complaint", "data": value, "right_name": key}
        return {"type": "all_complaints", "data": digital_rights_data["rights"]}
    
    # Pattern 4: "Who enforces [right_name]?"
    elif "enforce" in question_lower or "authority" in question_lower:
        right_match = re.search(r'(?:for|about)\s+([a-zA-Z_]+)', question_lower)
        if right_match:
            right_name = right_match.group(1)
            for key, value in digital_rights_data["rights"].items():
                if right_name in key.lower():
                    return {"type": "authority", "data": value["enforcement_authority"], "right_name": key}
        return {"type": "all_authorities", "data": digital_rights_data["rights"]}
    
    # Pattern 5: "What regions does [right_name] apply to?"
    elif "region" in question_lower or "country" in question_lower or "where" in question_lower:
        right_match = re.search(r'(?:does|for)\s+([a-zA-Z_]+)', question_lower)
        if right_match:
            right_name = right_match.group(1)
            for key, value in digital_rights_data["rights"].items():
                if right_name in key.lower():
                    return {"type": "regions", "data": value["applicable_regions"], "right_name": key}
        return {"type": "all_regions", "data": digital_rights_data["rights"]}
    
    # Default: Return all rights
    return {"type": "all_rights", "data": digital_rights_data["rights"]}

def format_response(query_result: Dict) -> str:
    """Format query result into a readable response"""
    query_type = query_result["type"]
    data = query_result["data"]
    
    response_parts = []
    
    if query_type == "all_rights":
        response_parts.append("## Digital Rights Available:")
        for right_name, right_info in data.items():
            formatted_name = right_name.replace('_', ' ').title()
            response_parts.append(f"\n**{formatted_name}**")
            response_parts.append(f"{right_info['description']}")
    
    elif query_type == "laws":
        response_parts.append(f"## Laws for {query_result.get('right_name', '').replace('_', ' ').title()}:")
        for law in data:
            response_parts.append(f"• {law}")
    
    elif query_type == "all_laws":
        response_parts.append("## All Applicable Laws:")
        for right_name, right_info in data.items():
            formatted_name = right_name.replace('_', ' ').title()
            response_parts.append(f"\n**{formatted_name}**:")
            for law in right_info["applicable_laws"]:
                response_parts.append(f"• {law}")
    
    elif query_type == "complaint":
        right_name = query_result.get('right_name', '').replace('_', ' ').title()
        response_parts.append(f"## How to File a Complaint for {right_name}:")
        for region, process in data["how_to_file_complaint"].items():
            response_parts.append(f"\n**{region}**: {process}")
            if region in data["contact_info"]:
                response_parts.append(f"Contact: {data['contact_info'][region]}")
    
    elif query_type == "all_complaints":
        response_parts.append("## Complaint Processes:")
        for right_name, right_info in data.items():
            formatted_name = right_name.replace('_', ' ').title()
            response_parts.append(f"\n**{formatted_name}**:")
            for region, process in right_info["how_to_file_complaint"].items():
                response_parts.append(f"• {region}: {process}")
    
    elif query_type == "authority":
        right_name = query_result.get('right_name', '').replace('_', ' ').title()
        response_parts.append(f"## Enforcement Authorities for {right_name}:")
        for region, authority in data.items():
            response_parts.append(f"• **{region}**: {authority}")
    
    elif query_type == "all_authorities":
        response_parts.append("## All Enforcement Authorities:")
        for right_name, right_info in data.items():
            formatted_name = right_name.replace('_', ' ').title()
            response_parts.append(f"\n**{formatted_name}**:")
            for region, authority in right_info["enforcement_authority"].items():
                response_parts.append(f"• {region}: {authority}")
    
    elif query_type == "regions":
        right_name = query_result.get('right_name', '').replace('_', ' ').title()
        response_parts.append(f"## Regions where {right_name} applies:")
        for region in data:
            response_parts.append(f"• {region}")
    
    elif query_type == "all_regions":
        response_parts.append("## All Regions:")
        for right_name, right_info in data.items():
            formatted_name = right_name.replace('_', ' ').title()
            response_parts.append(f"\n**{formatted_name}**:")
            for region in right_info["applicable_regions"]:
                response_parts.append(f"• {region}")
    
    return "\n".join(response_parts) if response_parts else "No information found for your query."

def answer_user_query(question: str) -> str:
    """Main function to answer user queries about digital rights"""
    try:
        query_result = parse_user_query(question)
        return format_response(query_result)
    except Exception as e:
        return f"I encountered an error while processing your question: {str(e)}"

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Digital Rights Legal Database API (Simple Version)",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "/ask": "POST - Ask questions about digital rights",
            "/rights": "GET - Get all available rights",
            "/health": "GET - Check API health",
            "/docs": "GET - Interactive API documentation"
        },
        "example_questions": [
            "What are my digital rights?",
            "What laws apply to data privacy?",
            "How do I file a complaint for online harassment?",
            "Who enforces net neutrality?",
            "What regions does digital accessibility apply to?"
        ]
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "message": "API is running without database dependency",
        "version": "1.0.0"
    }

@app.get("/rights")
def get_all_rights():
    """Get all available digital rights"""
    return {
        "rights": list(digital_rights_data["rights"].keys()),
        "total_count": len(digital_rights_data["rights"]),
        "rights_details": digital_rights_data["rights"]
    }

@app.post("/ask")
def ask_rights(query: QueryRequest):
    """FastAPI endpoint to answer questions about digital rights"""
    try:
        answer = answer_user_query(query.question)
        return {
            "question": query.question,
            "answer": answer,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Simple Digital Rights Legal Database API...")
    print("📋 Available endpoints:")
    print("   • GET  /        - API information")
    print("   • GET  /health  - Health check")
    print("   • GET  /rights  - Get all rights")
    print("   • POST /ask     - Ask questions")
    print("   • GET  /docs    - Interactive API documentation")
    print("\n🔗 API will be available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    print("\n⏹️  Press Ctrl+C to stop the server")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)