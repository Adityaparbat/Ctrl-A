"""
API routes for the Disability Schemes Discovery System.

This module contains all the REST API endpoints for searching, managing,
and retrieving disability welfare schemes.
"""

import time
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status, BackgroundTasks, Header
from fastapi.responses import JSONResponse

from src.models.scheme_models import (
    SearchRequest, SearchResponse, SchemeResponse, SchemeCreate, 
    SchemeUpdate, HealthCheckResponse, ErrorResponse, BulkUploadResponse,
    StatsResponse, SchemeSearchResult
)
from src.models.admin_models import (
    AdminLoginRequest, AdminRegisterRequest, AdminLoginResponse,
    AdminAuthResponse, SchemeCreateRequest, SchemeUpdateRequest,
    SchemeDeleteRequest, AdminSchemeResponse, AdminListResponse
)
from src.auth.admin_auth import admin_auth
from src.rag.retriever import get_retriever, ChromaDBRetriever
from src.rag.vector_store import get_vector_store, VectorStore
from src.utils.config import get_settings
from src.rag.chroma_config import get_chroma_config

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

def require_admin(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    settings = get_settings()
    if not settings.admin_api_key or x_api_key != settings.admin_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")
    return True

def require_admin_token(authorization: str | None = Header(default=None)):
    """Require admin token for authentication."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid authorization header")
    
    token = authorization.split(" ")[1]
    admin = admin_auth.verify_token(token)
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    
    return admin

# Dependency injection
def get_retriever_dependency() -> ChromaDBRetriever:
    """Get retriever instance."""
    return get_retriever()

def get_vector_store_dependency() -> VectorStore:
    """Get vector store instance."""
    return get_vector_store()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint for the API."""
    try:
        config = get_chroma_config()
        db_info = config.get_collection_info()
        
        return HealthCheckResponse(
            status="healthy",
            version="1.0.0",
            database_status="connected" if "error" not in db_info else "disconnected",
            total_schemes=db_info.get("total_schemes", 0),
            uptime_seconds=0.0  # This would be calculated in main.py
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )


@router.post("/schemes/search", response_model=SearchResponse)
async def search_schemes(
    search_request: SearchRequest,
    retriever: ChromaDBRetriever = Depends(get_retriever_dependency)
):
    """
    Search for disability schemes using natural language queries.
    
    This endpoint allows users to search for relevant disability welfare schemes
    using plain language queries. The search is powered by vector similarity
    and can be filtered by various criteria.
    """
    try:
        start_time = time.time()
        
        # Perform the search
        results = retriever.query_schemes(
            user_query=search_request.query,
            top_k=search_request.top_k
        )
        
        # Apply additional filters if specified
        filtered_results = []
        for result in results:
            # Filter by state
            if search_request.state and search_request.state.lower() not in result.get("state", "").lower():
                continue
            
            # Filter by disability type
            if search_request.disability_type and search_request.disability_type.value not in result.get("disability_type", "").lower():
                continue
            
            # Filter by support type
            if search_request.support_type and search_request.support_type.value not in result.get("support_type", "").lower():
                continue
            
            # Add similarity score if available
            if hasattr(result, 'similarity_score'):
                if search_request.min_score and result.similarity_score < search_request.min_score:
                    continue
                result["similarity_score"] = result.similarity_score
            
            filtered_results.append(result)
        
        search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return SearchResponse(
            query=search_request.query,
            results=filtered_results,
            total_results=len(filtered_results),
            search_time_ms=search_time,
            filters_applied={
                "state": search_request.state,
                "disability_type": search_request.disability_type,
                "support_type": search_request.support_type,
                "min_score": search_request.min_score
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search operation failed"
        )


@router.get("/schemes/search", response_model=SearchResponse)
async def search_schemes_get(
    query: str = Query(..., description="Search query"),
    top_k: int = Query(5, ge=1, le=50, description="Number of results to return"),
    state: Optional[str] = Query(None, description="Filter by state"),
    disability_type: Optional[str] = Query(None, description="Filter by disability type"),
    support_type: Optional[str] = Query(None, description="Filter by support type"),
    min_score: Optional[float] = Query(0.0, ge=0.0, le=1.0, description="Minimum similarity score"),
    retriever: ChromaDBRetriever = Depends(get_retriever_dependency)
):
    """
    Search for disability schemes using GET method (for simple queries).
    """
    search_request = SearchRequest(
        query=query,
        top_k=top_k,
        state=state,
        disability_type=disability_type,
        support_type=support_type,
        min_score=min_score
    )
    return await search_schemes(search_request, retriever)


@router.get("/schemes/stats", response_model=StatsResponse)
async def get_schemes_stats(
    vector_store: VectorStore = Depends(get_vector_store_dependency)
):
    """
    Get statistics about the schemes in the database.
    """
    try:
        # This would typically query the database for statistics
        # For now, we'll return basic info from ChromaDB
        config = get_chroma_config()
        info = config.get_collection_info()
        
        # In a real implementation, you'd query the database for detailed stats
        return StatsResponse(
            total_schemes=info.get("total_schemes", 0),
            schemes_by_state={"Unknown": info.get("total_schemes", 0)},
            schemes_by_disability_type={"Unknown": info.get("total_schemes", 0)},
            schemes_by_support_type={"Unknown": info.get("total_schemes", 0)},
            last_updated="2024-01-01T00:00:00Z"  # This would be dynamic
        )
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )


@router.post("/schemes/populate", response_model=BulkUploadResponse)
async def populate_database(
    background_tasks: BackgroundTasks,
    clear_existing: bool = Query(False, description="Clear existing data before populating"),
    vector_store: VectorStore = Depends(get_vector_store_dependency),
    _: bool = Depends(require_admin)
):
    """
    Populate the database with schemes from the JSON file.
    """
    try:
        # Run population in background
        background_tasks.add_task(
            vector_store.populate_vector_db,
            clear_existing=clear_existing
        )
        
        return BulkUploadResponse(
            total_processed=0,  # This would be updated by the background task
            successful=0,
            failed=0,
            errors=["Population started in background"]
        )
    except Exception as e:
        logger.error(f"Failed to start population: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start database population"
        )

@router.post("/schemes/replace", response_model=BulkUploadResponse)
async def replace_database(
    vector_store: VectorStore = Depends(get_vector_store_dependency),
    _: bool = Depends(require_admin)
):
    try:
        count = vector_store.populate_vector_db(clear_existing=True)
        return BulkUploadResponse(
            total_processed=count,
            successful=count,
            failed=0,
            errors=[]
        )
    except Exception as e:
        logger.error(f"Failed to replace database: {e}")
        raise HTTPException(status_code=500, detail="Failed to replace database")


@router.get("/schemes/suggestions")
async def get_search_suggestions(
    query: str = Query(..., min_length=1, description="Partial query for suggestions"),
    limit: int = Query(10, ge=1, le=50, description="Number of suggestions to return")
):
    """
    Get search suggestions based on partial query.
    """
    try:
        # This would typically query a suggestions index
        # For now, return some basic suggestions
        suggestions = [
            "education support for visually impaired",
            "financial aid for hearing impaired",
            "employment opportunities for mobility impaired",
            "assistive devices for autism",
            "medical support for cerebral palsy"
        ]
        
        # Filter suggestions based on query
        filtered_suggestions = [
            s for s in suggestions 
            if query.lower() in s.lower()
        ][:limit]
        
        return {"suggestions": filtered_suggestions}
        
    except Exception as e:
        logger.error(f"Failed to get suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve suggestions"
        )


@router.get("/schemes/states")
async def get_available_states():
    """
    Get list of all available states in the database.
    """
    try:
        # This would typically query the database
        # For now, return a sample list
        states = [
            "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
            "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
            "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
            "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
            "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
            "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi", "Puducherry"
        ]
        return {"states": states}
    except Exception as e:
        logger.error(f"Failed to get states: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve states"
        )


@router.get("/schemes/disability-types")
async def get_disability_types():
    """
    Get list of all supported disability types.
    """
    try:
        from src.models.scheme_models import DisabilityType
        return {
            "disability_types": [
                {"value": dt.value, "label": dt.value.replace("_", " ").title()}
                for dt in DisabilityType
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get disability types: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve disability types"
        )


@router.get("/schemes/support-types")
async def get_support_types():
    """
    Get list of all supported support types.
    """
    try:
        from src.models.scheme_models import SupportType
        return {
            "support_types": [
                {"value": st.value, "label": st.value.replace("_", " ").title()}
                for st in SupportType
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get support types: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve support types"
        )


# ==================== ADMIN ENDPOINTS ====================

@router.post("/admin/register", response_model=AdminAuthResponse)
async def register_admin(request: AdminRegisterRequest):
    """Register a new admin user."""
    try:
        result = admin_auth.register_admin(request)
        return AdminAuthResponse(**result)
    except Exception as e:
        logger.error(f"Admin registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/admin/login", response_model=AdminLoginResponse)
async def login_admin(request: AdminLoginRequest):
    """Login admin user."""
    try:
        result = admin_auth.login_admin(request)
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result["message"]
            )
        
        return AdminLoginResponse(
            access_token=result["access_token"],
            admin=result["admin"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/admin/logout")
async def logout_admin(authorization: str = Header(..., alias="Authorization")):
    """Logout admin user."""
    try:
        token = authorization.split(" ")[1]
        success = admin_auth.logout_admin(token)
        return {"success": success, "message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"Admin logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/admin/me")
async def get_current_admin(admin: dict = Depends(require_admin_token)):
    """Get current admin user info."""
    return {"admin": admin}


@router.get("/admin/schemes", response_model=AdminListResponse)
async def list_schemes_admin(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    admin: dict = Depends(require_admin_token)
):
    """List all schemes for admin management."""
    try:
        # Get all schemes from vector store
        vector_store = get_vector_store_dependency()
        
        # This is a simplified implementation - in production you'd want proper pagination
        # For now, we'll get all schemes and paginate in memory
        all_schemes = vector_store.get_all_schemes()  # We'll need to implement this method
        
        # Simple pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        schemes = all_schemes[start_idx:end_idx]
        
        return AdminListResponse(
            schemes=schemes,
            total=len(all_schemes),
            page=page,
            per_page=per_page
        )
    except Exception as e:
        logger.error(f"Failed to list schemes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve schemes"
        )


@router.post("/admin/schemes", response_model=AdminSchemeResponse)
async def create_scheme(
    request: SchemeCreateRequest,
    admin: dict = Depends(require_admin_token)
):
    """Create a new scheme."""
    try:
        vector_store = get_vector_store_dependency()
        
        # Create scheme data
        scheme_data = {
            "name": request.name,
            "description": request.description,
            "state": request.state,
            "disability_type": request.disability_type,
            "support_type": request.support_type,
            "apply_link": request.apply_link,
            "eligibility": request.eligibility,
            "benefits": request.benefits,
            "contact_info": request.contact_info,
            "validity_period": request.validity_period
        }
        
        # Add to vector store
        scheme_id = vector_store.add_scheme(scheme_data)  # We'll need to implement this method
        
        return AdminSchemeResponse(
            success=True,
            message="Scheme created successfully",
            scheme_id=scheme_id,
            scheme=scheme_data
        )
    except Exception as e:
        logger.error(f"Failed to create scheme: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create scheme"
        )


@router.put("/admin/schemes/{scheme_id}", response_model=AdminSchemeResponse)
async def update_scheme(
    scheme_id: str,
    request: SchemeUpdateRequest,
    admin: dict = Depends(require_admin_token)
):
    """Update an existing scheme."""
    try:
        vector_store = get_vector_store_dependency()
        
        # Update scheme in vector store
        success = vector_store.update_scheme(scheme_id, request.dict(exclude_unset=True))  # We'll need to implement this method
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scheme not found"
            )
        
        return AdminSchemeResponse(
            success=True,
            message="Scheme updated successfully",
            scheme_id=scheme_id
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update scheme: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update scheme"
        )


@router.delete("/admin/schemes/{scheme_id}", response_model=AdminSchemeResponse)
async def delete_scheme(
    scheme_id: str,
    admin: dict = Depends(require_admin_token)
):
    """Delete a scheme."""
    try:
        vector_store = get_vector_store_dependency()
        
        # Delete scheme from vector store
        success = vector_store.delete_scheme(scheme_id)  # We'll need to implement this method
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scheme not found"
            )
        
        return AdminSchemeResponse(
            success=True,
            message="Scheme deleted successfully",
            scheme_id=scheme_id
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete scheme: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete scheme"
        )
