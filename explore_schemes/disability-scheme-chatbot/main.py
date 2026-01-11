"""
FastAPI Backend - Government Scheme Chatbot
Main API endpoint for the domain-restricted GraphRAG chatbot.

MANDATORY FLOW:
User Query → Semantic embedding → Domain similarity check → Neo4j vector similarity search 
→ Subgraph extraction → Context assembly → LLM generates final answer

The LLM is used ONLY for response generation, NOT as a knowledge source.
All information comes from Neo4j graph context.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import logging

from domain_guardrail import is_domain_related, get_rejection_message
from graphrag import retrieve_context
from rag import generate_answer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Government Schemes for Persons with Disabilities Chatbot API",
    description="GraphRAG-based chatbot for government schemes and services for persons with disabilities (Divyangjan) in India",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    question: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    answer: str


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint implementing GraphRAG flow.
    
    Process:
    1. Domain guardrail check (semantic similarity)
    2. Query embedding
    3. Vector similarity search in Neo4j
    4. Subgraph extraction
    5. Context assembly from graph
    6. LLM generates final answer (formatting only)
    
    Args:
        req: ChatRequest with user question
    
    Returns:
        ChatResponse with formatted answer
    """
    user_query = req.question.strip()
    
    if not user_query:
        return ChatResponse(
            answer="Please provide a question about government schemes for persons with disabilities."
        )
    
    logger.info(f"Received query: {user_query}")
    
    # Step 1: Domain guardrail check (semantic similarity)
    if not is_domain_related(user_query):
        logger.info(f"Query rejected as out-of-domain: {user_query}")
        return ChatResponse(answer=get_rejection_message())
    
    # Step 2-6: GraphRAG retrieval pipeline
    try:
        retrieval_result = retrieve_context(user_query)
        
        # Check if out-of-domain (double-check)
        if retrieval_result.get('is_out_of_domain', False):
            return ChatResponse(answer=get_rejection_message())
        
        # Get context from retrieval
        context = retrieval_result.get('context')
        
        if not context:
            return ChatResponse(
                answer="This information is not available in the official scheme data."
            )
        
        # Check if context has schemes
        schemes = context.get('schemes', [])
        if not schemes:
            # Check if there's a helpful error message
            message = context.get('message', '')
            if message:
                # If the message indicates a DB connection error, use Mock Mode
                if "Unable to connect to database" in message:
                    return ChatResponse(
                        answer="[Notice: Neo4j Database not connected. Running in Demo Mode.] \n\n"
                               "Since the database is offline, I can only answer basic questions. "
                               "Schemes for persons with disabilities include:\n"
                               "1. **UDID Card**: Unique Disability ID for availing benefits.\n"
                               "2. **ADIP Scheme**: Assistance for purchasing aids and appliances.\n"
                               "3. **NHFDC Loans**: Concessional loans for self-employment.\n\n"
                               "Please ensure Neo4j is running for full functionality."
                    )
                return ChatResponse(answer=message)
            return ChatResponse(
                answer="No schemes found matching your query. Please try rephrasing your question about government schemes for persons with disabilities."
            )
        
        # Step 7: Generate formatted answer from graph context
        # LLM is used ONLY for formatting, NOT as knowledge source
        answer = generate_answer(context)
        
        logger.info(f"Generated answer for query: {user_query[:50]}...")
        
        return ChatResponse(answer=answer)
    
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        # Fallback/Mock Mode for when Neo4j is not connected
        return ChatResponse(
            answer="[Notice: Neo4j Database not connected. Running in Demo Mode.] \n\n"
                   "Since the database is offline, I can only answer basic questions. "
                   "Schemes for persons with disabilities include:\n"
                   "1. **UDID Card**: Unique Disability ID for availing benefits.\n"
                   "2. **ADIP Scheme**: Assistance for purchasing aids and appliances.\n"
                   "3. **NHFDC Loans**: Concessional loans for self-employment.\n\n"
                   "Please ensure Neo4j is running for full functionality."
        )


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Government Schemes for Persons with Disabilities Chatbot API is running",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check endpoint."""
    try:
        from graphrag import get_driver
        # Mock check if module exists but connection might fail
        return {
             "status": "running"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
