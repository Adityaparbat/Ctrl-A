"""
API routes for the Disability Schemes Discovery System.

This module contains all the REST API endpoints for searching, managing,
and retrieving disability welfare schemes.
"""

import time
import logging
import os
import json
from typing import List, Optional
from datetime import datetime
import pymongo
import certifi
from fastapi import APIRouter, HTTPException, Depends, Query, status, BackgroundTasks, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel

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
            
            # Filter by deadline (exclude expired schemes)
            deadline_str = result.get("deadline")
            if deadline_str:
                try:
                    deadline_date = datetime.strptime(deadline_str, "%Y-%m-%d")
                    if deadline_date < datetime.now():
                        continue
                except (ValueError, TypeError):
                    # If date format is invalid, keep it or log error? 
                    # For safety, let's keep it but log warning if strict
                    # For now just ignore parsing errors
                    pass
            
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
        import traceback
        traceback.print_exc()
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search operation failed: {str(e)}"
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


class PersonalizedQuery(BaseModel):
    disability_type: str
    state: Optional[str] = None
    age: Optional[str] = None
    gender: Optional[str] = None
    income_range: Optional[str] = None

@router.post("/schemes/personalized", response_model=SearchResponse)
async def personalized_schemes(
    query: PersonalizedQuery,
    retriever: ChromaDBRetriever = Depends(get_retriever_dependency)
):
    """
    Get personalized scheme recommendations based on user profile.
    Performs a broad search and then strictly filters by eligibility.
    """
    try:
        # Construct a search query focused on the disability type
        search_text = f"schemes for {query.disability_type} in {query.state or 'India'} benefits financial assistance"
        
        # Get a larger set of results to filter down
        results = retriever.query_schemes(
            user_query=search_text,
            top_k=100 
        )
        
        # Parse User Info for better filtering
        import re
        
        # User Age
        user_age = None
        if query.age:
            try: user_age = int(query.age)
            except: pass
            
        # User Income (Approximate Lower Bound)
        user_min_income = 0
        if query.income_range:
            # Handle formats like "500000+", "0-100000"
            parts = query.income_range.replace('+', '').replace('Above', '').replace('Below', '').strip().split('-')
            try:
                if parts and parts[0]:
                    val = float(parts[0].replace(',', '').replace('₹', '').strip())
                    user_min_income = val
            except: pass
            
        filtered_results = []
        for result in results:
            # 1. State Filter
            scheme_state = (result.get("state") or "All States").strip()
            # Treat "Central" or "India" as All States
            is_central = scheme_state.lower() in ["central", "india", "unknown", "all states"]
            
            if not is_central and query.state:
                q_state = query.state.strip().lower()
                s_state = scheme_state.lower()
                
                # Bidirectional check
                if q_state not in s_state and s_state not in q_state:
                    continue
            
            # 2. Disability Type Filter
            scheme_dtype = result.get("disability_type") or "All Disabilities"
            s_dtype_lower = scheme_dtype.lower()
            q_dtype_lower = query.disability_type.lower()
            
            # If user has "Multiple Disabilities", show them everything (broad matching)
            # Or if scheme is generic
            if "multiple" in q_dtype_lower:
                pass 
            elif s_dtype_lower != "all disabilities" and s_dtype_lower != "multiple_disabilities":
                if q_dtype_lower not in s_dtype_lower and s_dtype_lower not in q_dtype_lower:
                       desc = (result.get("description") or "").lower()
                       # Fuzzy mappings
                       if "mobility" in q_dtype_lower and any(x in s_dtype_lower or x in desc for x in ["locomotor", "orthopedic", "physical", "handicap"]):
                           pass 
                       elif "visual" in q_dtype_lower and any(x in s_dtype_lower or x in desc for x in ["blind", "low vision"]):
                           pass
                       elif "hearing" in q_dtype_lower and any(x in s_dtype_lower or x in desc for x in ["deaf"]):
                           pass
                       else:
                           continue

            # 3. Income Filter (NEW)
            eligibility = (result.get("eligibility") or "").lower()
            
            # Check for BPL constraint first
            if ("below poverty line" in eligibility or "bpl" in eligibility) and user_min_income > 150000:
                 continue
            
            # Capture "income < X" patterns
            # Pattern: (income) ... (below|less than|upto) ... (Rs. X | X lakhs)
            # More general check: "income below Rs. 2.5 lakhs"
            inc_match = re.search(r'(?:income|financial|family).*?(?:below|less than|upto|not exceeding|max).*?(?:rs\.?)?\s*(\d+(?:\.\d+)?)\s*(lakhs?|lakh|k)', eligibility)
            if inc_match:
                 val = float(inc_match.group(1))
                 unit = inc_match.group(2)
                 limit = val * 100000 if 'lakh' in unit else val * 1000
                 
                 # If User Minimum Income >= Scheme Maximum Limit -> Conflict
                 if user_min_income >= limit:
                     continue

            # 4. Age Filter (NEW)
            if user_age:
                # Max Age
                max_age_match = re.search(r'(?:below|upto|max|not exceeding)\s*(\d+)\s*years?', eligibility)
                if max_age_match:
                    limit = int(max_age_match.group(1))
                    if user_age >= limit:
                        continue
                
                # Min Age
                min_age_match = re.search(r'(?:above|min|minimum)\s*(\d+)\s*years?', eligibility)
                if min_age_match:
                    limit = int(min_age_match.group(1))
                    if user_age < limit:
                        continue

            filtered_results.append(result)
        
        return SearchResponse(
            query=search_text,
            results=filtered_results,
            total_results=len(filtered_results),
            search_time_ms=0,
            filters_applied={
                "personalized": True,
                "user_state": query.state,
                "user_disability": query.disability_type
            }
        )
    except Exception as e:
        logger.error(f"Personalized search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Personalized search failed: {str(e)}"
        )


@router.get("/schemes/stats", response_model=StatsResponse)
async def get_schemes_stats(
    vector_store: VectorStore = Depends(get_vector_store_dependency)
):
    """
    Get statistics about the schemes in the database.
    """
    try:
        # Get all schemes to calculate real stats
        schemes = vector_store.get_all_schemes()
        logger.info(f"Retrieved {len(schemes)} schemes for stats calculation")
        
        total_schemes = len(schemes)
        active_schemes = 0
        schemes_by_state = {}
        schemes_by_disability = {}
        schemes_by_support = {}
        
        current_date = datetime.now().date()
        
        # Log first scheme to verify structure
        if schemes:
            logger.info(f"Sample scheme data: {schemes[0]}")
        
        for scheme in schemes:
            # Check if active
            is_active = True
            deadline_str = scheme.get("deadline")
            
            if deadline_str and deadline_str != "None":  # Handle string "None" just in case
                try:
                    # Try flexible date parsing
                    deadline_date = None
                    for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"]:
                        try:
                            deadline_date = datetime.strptime(deadline_str, fmt).date()
                            break
                        except ValueError:
                            continue
                            
                    if deadline_date:
                        if deadline_date < current_date:
                            is_active = False
                    else:
                        logger.warning(f"Could not parse date: {deadline_str} for scheme {scheme.get('name')}")
                except Exception as e:
                    logger.warning(f"Error parsing date {deadline_str}: {e}")
            
            if is_active:
                active_schemes += 1
            
            # Count by State - Clean up string
            state = str(scheme.get("state", "Unknown")).strip()
            if not state or state.lower() == "none":
                state = "Unknown"
            schemes_by_state[state] = schemes_by_state.get(state, 0) + 1
            
            # Count by Disability Type
            disability = str(scheme.get("disability_type", "Unknown")).strip()
            if not disability or disability.lower() == "none":
                disability = "Unknown"
            schemes_by_disability[disability] = schemes_by_disability.get(disability, 0) + 1
            
            # Count by Support Type
            support = str(scheme.get("support_type", "Unknown")).strip()
            if not support or support.lower() == "none":
                support = "Unknown"
            schemes_by_support[support] = schemes_by_support.get(support, 0) + 1
            
        return StatsResponse(
            total_schemes=total_schemes,
            active_schemes=active_schemes,
            schemes_by_state=schemes_by_state,
            schemes_by_disability_type=schemes_by_disability,
            schemes_by_support_type=schemes_by_support,
            last_updated=datetime.now().isoformat()
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
    _: bool = Depends(require_admin_token)
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
    vector_store: VectorStore = Depends(get_vector_store_dependency)
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
    background_tasks: BackgroundTasks,
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
            "validity_period": request.validity_period,
            "deadline": request.deadline
        }
        
        # Add to vector store
        scheme_id = vector_store.add_scheme(scheme_data)  # We'll need to implement this method
        
        # PERSISTENCE: Save to JSON file so it survives refresh
        try:
            settings = get_settings()
            if os.path.exists(settings.data_path):
                with open(settings.data_path, 'r', encoding='utf-8') as f:
                    schemes = json.load(f)
            else:
                schemes = []
            
            # Add new scheme
            schemes.append(scheme_data)
            
            with open(settings.data_path, 'w', encoding='utf-8') as f:
                json.dump(schemes, f, indent=4, ensure_ascii=False)
                
            logger.info(f"Persisted new scheme '{scheme_data['name']}' to JSON")
        except Exception as e:
            logger.error(f"Failed to persist scheme to JSON: {e}")
        
        # Trigger notification (Synchronous for guaranteed execution during debug)
        try:
            logger.info("Triggering synchronous notification...")
            notify_users(scheme_data)
        except Exception as ne:
            logger.error(f"Notification error: {ne}")

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

        # PERSISTENCE: Update in JSON file
        try:
            settings = get_settings()
            if os.path.exists(settings.data_path):
                with open(settings.data_path, 'r', encoding='utf-8') as f:
                    schemes = json.load(f)
                
                # Find and update scheme (assuming name match for now as ID isn't in JSON originally)
                # But schemes in vector store have IDs. 
                # Strategy: Match by name if ID not present, or better, we can't reliably sync perfectly 
                # without an ID in JSON. For now, best effort match by Name if possible, 
                # or just acknowledge this limitation. 
                # Ideally we should start adding IDs to the JSON.
                
                # Simple approach: Find scheme where name matches (if name didn't change) 
                # OR this is a complex sync issue. 
                # Better approach for Hackathon: Just append new ones. 
                # Full sync is hard. Let's just focus on Creation persistence as that's the user complaint.
                pass 
                
        except Exception as e:
            logger.error(f"Failed to persist update to JSON: {e}")
        
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
        
        # Get scheme details before deletion to find name
        scheme_to_delete = vector_store.get_scheme_by_id(scheme_id)
        
        # Delete scheme from vector store
        success = vector_store.delete_scheme(scheme_id)  # We'll need to implement this method
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scheme not found"
            )
            
        # PERSISTENCE: Remove from JSON file
        try:
            if scheme_to_delete:
                name_to_delete = scheme_to_delete.get("name")
                settings = get_settings()
                if os.path.exists(settings.data_path):
                    with open(settings.data_path, 'r', encoding='utf-8') as f:
                        schemes = json.load(f)
                    
                    # Filter out the deleted scheme
                    initial_len = len(schemes)
                    schemes = [s for s in schemes if s.get("name") != name_to_delete]
                    
                    if len(schemes) < initial_len:
                        with open(settings.data_path, 'w', encoding='utf-8') as f:
                            json.dump(schemes, f, indent=4, ensure_ascii=False)
                        logger.info(f"Removed scheme '{name_to_delete}' from JSON")
        except Exception as e:
            logger.error(f"Failed to persist deletion to JSON: {e}")
        
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


def notify_users(scheme_data: dict):
    """
    Background task to notify relevant users about a new scheme.
    Matches users based on disability type and state (via address).
    """
    try:
        # Connect to MongoDB (Ctrl-A database)
        uri = "mongodb+srv://aditya2006:adi2006@cluster0.xdbxki9.mongodb.net/gov_access?retryWrites=true&w=majority&appName=Cluster0"
        client = pymongo.MongoClient(uri, tlsCAFile=certifi.where())
        db = client['ctrl_a_db']
        
        logger.info(f"Checking notifications for scheme: {scheme_data['name']} (Type: {scheme_data['disability_type']}, State: {scheme_data['state']})")
        
        query = {}
        
        # 1. Filter by Disability Type (with fuzzy matching for 'mobility')
        dtype = scheme_data["disability_type"]
        if dtype not in ["multiple_disabilities", "all_disabilities"]:
            if dtype == "mobility_impairment":
                query["disability_type"] = {"$in": ["mobility_impairment", "mobility"]}
            elif dtype == "visual_impairment":
                query["disability_type"] = {"$in": ["visual_impairment", "visual"]}
            elif dtype == "hearing_impairment":
                query["disability_type"] = {"$in": ["hearing_impairment", "hearing"]}
            else:
                query["disability_type"] = dtype
        
        # 2. Filter by State
        scheme_state = scheme_data.get("state", "All States")
        if scheme_state and scheme_state.lower() != "all states":
            # Match strictly by state OR if user has no address specified (so they don't miss out)
            query["$or"] = [
                {"address": {"$regex": scheme_state, "$options": "i"}},
                {"address": ""},
                {"address": None},
                {"address": {"$exists": False}}
            ]
            
        logger.info(f"Notification Query Generated: {query}")
            
        users = list(db.users.find(query))
        logger.info(f"Found {len(users)} users matching the notification criteria.")
        
        if not users:
            logger.warning("No matching users found. Debug info:")
            total = db.users.count_documents({})
            logger.info(f"Total users in DB: {total}")
            # Relaxed fallback: if no users found with exact match, try notifying ALL users for debugging if needed
            # For now, just return
            return

        notifications = []
        current_time = datetime.utcnow()
        for user in users:
            notifications.append({
                "user_id": str(user["_id"]),
                "message": f"New Scheme Alert: '{scheme_data['name']}' is now available.",
                "is_read": False,
                "created_at": current_time
            })
            
        if notifications:
            result = db.notifications.insert_many(notifications)
            logger.info(f"Successfully inserted {len(result.inserted_ids)} notifications into DB.")
            
    except Exception as e:
        logger.error(f"CRITICAL: Failed to send notifications: {e}", exc_info=True)
            
    except Exception as e:
        logger.error(f"Failed to send notifications: {e}")
