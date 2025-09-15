"""
Main FastAPI application for the Disability Schemes Discovery System.

This application provides a REST API for searching and managing disability welfare schemes
using vector similarity search with ChromaDB.
"""

import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from src.api.routes import router
from src.rag.chroma_config import get_chroma_config
from src.rag.vector_store import get_vector_store
from src.models.scheme_models import HealthCheckResponse, ErrorResponse
from src.utils.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global variables for tracking
start_time = time.time()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Disability Schemes Discovery System...")
    try:
        # Initialize ChromaDB
        config = get_chroma_config()
        info = config.get_collection_info()
        logger.info(f"ChromaDB initialized: {info}")

        # Auto-populate from JSON if empty
        total = info.get("total_schemes", 0) if isinstance(info, dict) else 0
        if total == 0:
            logger.info("Vector DB empty. Populating from data/disability_schemes.json ...")
            store = get_vector_store()
            inserted = store.populate_vector_db(clear_existing=True)
            logger.info(f"Inserted {inserted} schemes into vector DB")
    except Exception as e:
        logger.error(f"Failed to initialize ChromaDB: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Disability Schemes Discovery System...")


# Create FastAPI application
app = FastAPI(
    title="Disability Schemes Discovery System",
    description="A comprehensive API for discovering disability welfare schemes using AI-powered search",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

# Serve UI from static directory at root
app.mount("/", StaticFiles(directory="static", html=True), name="static")


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    try:
        config = get_chroma_config()
        db_info = config.get_collection_info()
        
        uptime = time.time() - start_time
        
        return HealthCheckResponse(
            status="healthy",
            version="1.0.0",
            database_status="connected" if "error" not in db_info else "disconnected",
            total_schemes=db_info.get("total_schemes", 0),
            uptime_seconds=uptime
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler."""
    return ErrorResponse(
        error="Not Found",
        detail="The requested resource was not found",
        error_code="404"
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler."""
    logger.error(f"Internal server error: {exc}")
    return ErrorResponse(
        error="Internal Server Error",
        detail="An unexpected error occurred",
        error_code="500"
    )


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
