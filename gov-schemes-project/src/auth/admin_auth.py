"""
Admin authentication and authorization system.
"""

import hashlib
import secrets
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path

from src.models.admin_models import AdminUser, AdminRole, AdminLoginRequest, AdminRegisterRequest
from src.utils.config import get_settings


class AdminAuthManager:
    """Manages admin authentication and authorization."""
    
    def __init__(self):
        self.settings = get_settings()
        self.admin_db_path = Path("data/admin_users.json")
        self.admin_db_path.parent.mkdir(exist_ok=True)
        self._load_admin_db()
    
    def _load_admin_db(self):
        """Load admin database from file."""
        if self.admin_db_path.exists():
            try:
                with open(self.admin_db_path, 'r', encoding='utf-8') as f:
                    self.admin_db = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.admin_db = {"users": {}, "sessions": {}}
        else:
            self.admin_db = {"users": {}, "sessions": {}}
            self._save_admin_db()
    
    def _save_admin_db(self):
        """Save admin database to file."""
        with open(self.admin_db_path, 'w', encoding='utf-8') as f:
            json.dump(self.admin_db, f, indent=2, default=str)
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt."""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        try:
            salt, password_hash = hashed.split(':')
            return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
        except ValueError:
            return False
    
    def _generate_token(self) -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(32)
    
    def register_admin(self, request: AdminRegisterRequest) -> Dict[str, Any]:
        """Register a new admin user."""
        # Validate passwords match
        if request.password != request.confirm_password:
            return {"success": False, "message": "Passwords do not match"}
        
        # Check if username already exists
        if request.username in self.admin_db["users"]:
            return {"success": False, "message": "Username already exists"}
        
        # Check if email already exists
        for user_data in self.admin_db["users"].values():
            if user_data.get("email") == request.email:
                return {"success": False, "message": "Email already registered"}
        
        # Create admin user
        admin_id = secrets.token_urlsafe(16)
        admin_user = AdminUser(
            id=admin_id,
            username=request.username,
            email=request.email,
            role=request.role,
            is_active=True,
            created_at=datetime.now()
        )
        
        # Store user data
        self.admin_db["users"][request.username] = {
            "id": admin_user.id,
            "username": admin_user.username,
            "email": admin_user.email,
            "role": admin_user.role.value,
            "is_active": admin_user.is_active,
            "created_at": admin_user.created_at.isoformat(),
            "password_hash": self._hash_password(request.password)
        }
        
        self._save_admin_db()
        
        return {
            "success": True,
            "message": "Admin registered successfully",
            "admin": admin_user.dict()
        }
    
    def login_admin(self, request: AdminLoginRequest) -> Dict[str, Any]:
        """Login admin user."""
        # Check if user exists
        if request.username not in self.admin_db["users"]:
            return {"success": False, "message": "Invalid username or password"}
        
        user_data = self.admin_db["users"][request.username]
        
        # Check if user is active
        if not user_data.get("is_active", True):
            return {"success": False, "message": "Account is deactivated"}
        
        # Verify password
        if not self._verify_password(request.password, user_data["password_hash"]):
            return {"success": False, "message": "Invalid username or password"}
        
        # Generate token
        token = self._generate_token()
        expires_at = datetime.now() + timedelta(hours=1)
        
        # Store session
        self.admin_db["sessions"][token] = {
            "username": request.username,
            "expires_at": expires_at.isoformat()
        }
        
        # Update last login
        user_data["last_login"] = datetime.now().isoformat()
        
        self._save_admin_db()
        
        # Create admin user object
        admin_user = AdminUser(
            id=user_data["id"],
            username=user_data["username"],
            email=user_data["email"],
            role=AdminRole(user_data["role"]),
            is_active=user_data["is_active"],
            created_at=datetime.fromisoformat(user_data["created_at"]),
            last_login=datetime.fromisoformat(user_data["last_login"]) if user_data.get("last_login") else None
        )
        
        return {
            "success": True,
            "message": "Login successful",
            "access_token": token,
            "admin": admin_user.dict()
        }
    
    def verify_token(self, token: str) -> Optional[AdminUser]:
        """Verify admin token and return admin user."""
        if token not in self.admin_db["sessions"]:
            return None
        
        session = self.admin_db["sessions"][token]
        expires_at = datetime.fromisoformat(session["expires_at"])
        
        # Check if token is expired
        if datetime.now() > expires_at:
            del self.admin_db["sessions"][token]
            self._save_admin_db()
            return None
        
        # Get user data
        username = session["username"]
        if username not in self.admin_db["users"]:
            return None
        
        user_data = self.admin_db["users"][username]
        
        # Check if user is still active
        if not user_data.get("is_active", True):
            return None
        
        return AdminUser(
            id=user_data["id"],
            username=user_data["username"],
            email=user_data["email"],
            role=AdminRole(user_data["role"]),
            is_active=user_data["is_active"],
            created_at=datetime.fromisoformat(user_data["created_at"]),
            last_login=datetime.fromisoformat(user_data["last_login"]) if user_data.get("last_login") else None
        )
    
    def logout_admin(self, token: str) -> bool:
        """Logout admin user."""
        if token in self.admin_db["sessions"]:
            del self.admin_db["sessions"][token]
            self._save_admin_db()
            return True
        return False
    
    def get_all_admins(self) -> list:
        """Get all admin users."""
        admins = []
        for user_data in self.admin_db["users"].values():
            admin = AdminUser(
                id=user_data["id"],
                username=user_data["username"],
                email=user_data["email"],
                role=AdminRole(user_data["role"]),
                is_active=user_data["is_active"],
                created_at=datetime.fromisoformat(user_data["created_at"]),
                last_login=datetime.fromisoformat(user_data["last_login"]) if user_data.get("last_login") else None
            )
            admins.append(admin.dict())
        return admins


# Global instance
admin_auth = AdminAuthManager()
