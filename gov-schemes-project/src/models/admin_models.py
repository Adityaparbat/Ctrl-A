"""
Admin models for authentication and scheme management.
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum


class AdminRole(str, Enum):
    """Admin roles."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"


class AdminUser(BaseModel):
    """Admin user model."""
    id: str
    username: str
    email: EmailStr
    role: AdminRole
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None


class AdminLoginRequest(BaseModel):
    """Admin login request."""
    username: str
    password: str


class AdminRegisterRequest(BaseModel):
    """Admin registration request."""
    username: str
    email: EmailStr
    password: str
    confirm_password: str
    role: AdminRole = AdminRole.ADMIN


class AdminLoginResponse(BaseModel):
    """Admin login response."""
    access_token: str
    token_type: str = "bearer"
    admin: AdminUser
    expires_in: int = 3600  # 1 hour


class AdminAuthResponse(BaseModel):
    """Admin authentication response."""
    success: bool
    message: str
    admin: Optional[AdminUser] = None


class SchemeCreateRequest(BaseModel):
    """Request to create a new scheme."""
    name: str
    description: str
    state: str
    disability_type: str
    support_type: str
    apply_link: str
    eligibility: Optional[str] = None
    benefits: Optional[str] = None
    contact_info: Optional[str] = None
    validity_period: Optional[str] = None


class SchemeUpdateRequest(BaseModel):
    """Request to update an existing scheme."""
    name: Optional[str] = None
    description: Optional[str] = None
    state: Optional[str] = None
    disability_type: Optional[str] = None
    support_type: Optional[str] = None
    apply_link: Optional[str] = None
    eligibility: Optional[str] = None
    benefits: Optional[str] = None
    contact_info: Optional[str] = None
    validity_period: Optional[str] = None


class SchemeDeleteRequest(BaseModel):
    """Request to delete a scheme."""
    scheme_id: str


class AdminSchemeResponse(BaseModel):
    """Response for scheme operations."""
    success: bool
    message: str
    scheme_id: Optional[str] = None
    scheme: Optional[dict] = None


class AdminListResponse(BaseModel):
    """Response for listing schemes."""
    schemes: List[dict]
    total: int
    page: int = 1
    per_page: int = 20
