"""
Pydantic models for the disability schemes system.

This module defines all the data models used for API requests and responses,
ensuring proper validation and documentation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class DisabilityType(str, Enum):
    """Enumeration of supported disability types."""
    VISUAL_IMPAIRMENT = "visual_impairment"
    HEARING_IMPAIRMENT = "hearing_impairment"
    MOBILITY_IMPAIRMENT = "mobility_impairment"
    INTELLECTUAL_DISABILITY = "intellectual_disability"
    AUTISM = "autism"
    CEREBRAL_PALSY = "cerebral_palsy"
    MULTIPLE_DISABILITIES = "multiple_disabilities"
    OTHER = "other"


class SupportType(str, Enum):
    """Enumeration of support types."""
    FINANCIAL = "financial"
    EDUCATIONAL = "educational"
    MEDICAL = "medical"
    EMPLOYMENT = "employment"
    ASSISTIVE_DEVICES = "assistive_devices"
    TRANSPORTATION = "transportation"
    HOUSING = "housing"
    OTHER = "other"


class SchemeBase(BaseModel):
    """Base model for scheme data."""
    name: str = Field(..., min_length=1, max_length=500, description="Name of the scheme")
    description: str = Field(..., min_length=10, max_length=2000, description="Detailed description of the scheme")
    state: str = Field(..., min_length=1, max_length=100, description="State where the scheme is available")
    disability_type: DisabilityType = Field(..., description="Type of disability the scheme supports")
    support_type: SupportType = Field(..., description="Type of support provided")
    apply_link: str = Field(..., min_length=1, max_length=500, description="Link to apply for the scheme")
    eligibility: Optional[str] = Field(None, max_length=1000, description="Eligibility criteria")
    benefits: Optional[str] = Field(None, max_length=1000, description="Benefits provided")
    contact_info: Optional[str] = Field(None, max_length=500, description="Contact information")
    validity_period: Optional[str] = Field(None, max_length=200, description="Validity period of the scheme")
    
    @validator('apply_link')
    def validate_apply_link(cls, v):
        """Validate that apply_link is a proper URL."""
        if not v.startswith(('http://', 'https://', 'www.')):
            raise ValueError('Apply link must be a valid URL')
        return v


class SchemeCreate(SchemeBase):
    """Model for creating a new scheme."""
    pass


class SchemeUpdate(BaseModel):
    """Model for updating an existing scheme."""
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    state: Optional[str] = Field(None, min_length=1, max_length=100)
    disability_type: Optional[DisabilityType] = None
    support_type: Optional[SupportType] = None
    apply_link: Optional[str] = Field(None, min_length=1, max_length=500)
    eligibility: Optional[str] = Field(None, max_length=1000)
    benefits: Optional[str] = Field(None, max_length=1000)
    contact_info: Optional[str] = Field(None, max_length=500)
    validity_period: Optional[str] = Field(None, max_length=200)


class SchemeResponse(SchemeBase):
    """Model for scheme response data."""
    id: str = Field(..., description="Unique identifier for the scheme")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    
    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    """Model for search requests."""
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    top_k: int = Field(5, ge=1, le=50, description="Number of results to return")
    state: Optional[str] = Field(None, max_length=100, description="Filter by state")
    disability_type: Optional[DisabilityType] = Field(None, description="Filter by disability type")
    support_type: Optional[SupportType] = Field(None, description="Filter by support type")
    min_score: Optional[float] = Field(0.0, ge=0.0, le=1.0, description="Minimum similarity score")
    
    @validator('query')
    def validate_query(cls, v):
        """Validate and clean the search query."""
        return v.strip()


class SearchResponse(BaseModel):
    """Model for search response."""
    query: str = Field(..., description="The search query")
    results: List[Dict[str, Any]] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results found")
    search_time_ms: float = Field(..., description="Search time in milliseconds")
    filters_applied: Dict[str, Any] = Field(..., description="Filters that were applied")


class SchemeSearchResult(BaseModel):
    """Model for individual search result."""
    name_and_desc: str = Field(..., description="Combined name and description")
    state: str = Field(..., description="State")
    disability_type: str = Field(..., description="Disability type")
    support_type: str = Field(..., description="Support type")
    apply_link: str = Field(..., description="Application link")
    similarity_score: Optional[float] = Field(None, description="Similarity score")
    eligibility: Optional[str] = Field(None, description="Eligibility criteria")
    benefits: Optional[str] = Field(None, description="Benefits")


class HealthCheckResponse(BaseModel):
    """Model for health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    database_status: str = Field(..., description="Database connection status")
    total_schemes: int = Field(..., description="Total number of schemes in database")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")


class ErrorResponse(BaseModel):
    """Model for error responses."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    error_code: Optional[str] = Field(None, description="Error code")


class BulkUploadResponse(BaseModel):
    """Model for bulk upload response."""
    total_processed: int = Field(..., description="Total number of schemes processed")
    successful: int = Field(..., description="Number of successfully added schemes")
    failed: int = Field(..., description="Number of failed schemes")
    errors: List[str] = Field(..., description="List of error messages")


class StatsResponse(BaseModel):
    """Model for statistics response."""
    total_schemes: int = Field(..., description="Total number of schemes")
    schemes_by_state: Dict[str, int] = Field(..., description="Number of schemes per state")
    schemes_by_disability_type: Dict[str, int] = Field(..., description="Number of schemes per disability type")
    schemes_by_support_type: Dict[str, int] = Field(..., description="Number of schemes per support type")
    last_updated: str = Field(..., description="Last update timestamp")
