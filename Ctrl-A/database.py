import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import hashlib
import secrets
from datetime import datetime, timedelta
import os
import certifi

class DatabaseManager:
    def __init__(self):
        # Connection string
        self.uri = "mongodb+srv://aditya2006:adi2006@cluster0.xdbxki9.mongodb.net/gov_access?retryWrites=true&w=majority&appName=Cluster0"
        try:
            # Fix for SSL: TLSV1_ALERT_INTERNAL_ERROR
            self.client = MongoClient(self.uri, tlsCAFile=certifi.where())
            # Send a ping to confirm a successful connection
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(f"MongoDB Connection Error: {e}")

        self.db = self.client['ctrl_a_db']
        
        # Collections
        self.users = self.db['users']
        self.sessions = self.db['sessions']
        self.password_reset_tokens = self.db['password_reset_tokens']
        self.applications = self.db['applications']
        self.notifications = self.db['notifications']
        
        # Create indexes (idempotent)
        try:
            self.users.create_index("email", unique=True)
            self.sessions.create_index("session_token", unique=True)
            self.password_reset_tokens.create_index("token", unique=True)
        except Exception as e:
            print(f"Index creation warning: {e}")
    
    def hash_password(self, password):
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def verify_password(self, password, stored_hash):
        """Verify password against stored hash"""
        try:
            if not stored_hash: return False
            salt, password_hash = stored_hash.split(':')
            return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
        except:
            return False
    
    def create_user(self, email, phone, disability_type, password, state="", age="", income_range=""):
        """Create a new user"""
        try:
            # Check if email exists
            if self.users.find_one({"email": email}):
                return {"success": False, "error": "Email already exists"}
            
            password_hash = self.hash_password(password)
            
            user_doc = {
                "email": email,
                "phone": phone,
                "disability_type": disability_type,
                "state": state,
                "age": age,
                "income_range": income_range,
                "password_hash": password_hash,
                "created_at": datetime.utcnow(),
                "last_login": None,
                "is_active": True,
                # New fields for profile
                "full_name": email.split('@')[0], # Default name from email
                "address": "",
                "profile_image_url": ""
            }
            
            result = self.users.insert_one(user_doc)
            return {"success": True, "user_id": str(result.inserted_id)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def authenticate_user(self, email, password):
        """Authenticate user login"""
        try:
            user = self.users.find_one({"email": email})
            if not user:
                return {"success": False, "error": "User not found"}
            
            if not user.get("is_active", True):
                return {"success": False, "error": "Account is deactivated"}
            
            if not self.verify_password(password, user.get("password_hash")):
                return {"success": False, "error": "Invalid password"}
            
            # Update last login
            self.users.update_one(
                {"_id": user["_id"]},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            
            return {
                "success": True, 
                "user": {
                    "id": str(user["_id"]),
                    "email": user["email"],
                    "phone": user.get("phone", ""),
                    "disability_type": user.get("disability_type", ""),
                    "state": user.get("state", ""),
                    "age": user.get("age", ""),
                    "income_range": user.get("income_range", "")
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_session(self, user_id):
        """Create a new session for user"""
        try:
            # Check if user exists first
            user = self.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                 return {"success": False, "error": "User does not exist"}

            # Deactivate old sessions
            self.sessions.update_many(
                {"user_id": str(user_id)},
                {"$set": {"is_active": False}}
            )
            
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(days=7)
            
            session_doc = {
                "user_id": str(user_id),
                "session_token": session_token,
                "created_at": datetime.utcnow(),
                "expires_at": expires_at,
                "is_active": True
            }
            
            self.sessions.insert_one(session_doc)
            return {"success": True, "session_token": session_token}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def validate_session(self, session_token):
        """Validate session token and return user info"""
        try:
            session = self.sessions.find_one({
                "session_token": session_token,
                "is_active": True,
                "expires_at": {"$gt": datetime.utcnow()}
            })
            
            if not session:
                return {"success": False, "error": "Invalid or expired session"}
            
            user = self.users.find_one({"_id": ObjectId(session["user_id"])})
            if not user:
                return {"success": False, "error": "User not found"}
            
            return {
                "success": True,
                "user": {
                    "id": str(user["_id"]),
                    "email": user["email"],
                    "phone": user.get("phone", ""),
                    "disability_type": user.get("disability_type", ""),
                    "state": user.get("state", ""),
                    "age": user.get("age", ""),
                    "income_range": user.get("income_range", ""),
                    "full_name": user.get("full_name", user["email"].split('@')[0])
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def logout_user(self, session_token):
        """Logout user by deactivating session"""
        try:
            self.sessions.update_one(
                {"session_token": session_token},
                {"$set": {"is_active": False}}
            )
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_password_reset_token(self, email):
        """Create password reset token"""
        try:
            user = self.users.find_one({"email": email})
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Deactivate old tokens
            self.password_reset_tokens.update_many(
                {"user_id": str(user["_id"])},
                {"$set": {"is_used": True}}
            )
            
            token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(hours=1)
            
            token_doc = {
                "user_id": str(user["_id"]),
                "token": token,
                "created_at": datetime.utcnow(),
                "expires_at": expires_at,
                "is_used": False
            }
            
            self.password_reset_tokens.insert_one(token_doc)
            return {"success": True, "token": token}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def reset_password(self, token, new_password):
        """Reset password using token"""
        try:
            token_doc = self.password_reset_tokens.find_one({
                "token": token,
                "is_used": False,
                "expires_at": {"$gt": datetime.utcnow()}
            })
            
            if not token_doc:
                return {"success": False, "error": "Invalid or expired token"}
            
            password_hash = self.hash_password(new_password)
            user_id = token_doc["user_id"]
            
            self.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"password_hash": password_hash}}
            )
            
            # Mark token as used
            self.password_reset_tokens.update_one(
                {"_id": token_doc["_id"]},
                {"$set": {"is_used": True}}
            )
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # -------------------------------------------------------------
    # NEW METHODS FOR APPLICATIONS & NOTIFICATIONS
    # -------------------------------------------------------------

    def submit_application(self, user_id, scheme_id, scheme_title, documents):
        """
        Submit a new application for a scheme.
        documents should be a dict/list of file URLs or paths.
        """
        try:
            application_doc = {
                "user_id": str(user_id),
                "scheme_id": str(scheme_id),
                "scheme_title": scheme_title,
                "status": "pending",  # pending, verified, rejected
                "documents": documents, # e.g. {"aadhar": "url", ...}
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = self.applications.insert_one(application_doc)
            
            # Add a notification for the user
            self.create_notification(
                user_id, 
                f"Application submitted for '{scheme_title}'. Status: Pending approval."
            )
            
            return {"success": True, "application_id": str(result.inserted_id)}
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def get_user_applications(self, user_id):
        """Get all applications for a specific user"""
        try:
            cursor = self.applications.find({"user_id": str(user_id)}).sort("created_at", -1)
            apps = []
            for doc in cursor:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                apps.append(doc)
            return {"success": True, "applications": apps}
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def get_all_applications(self, status_filter=None):
        """Get all applications (for admin)"""
        try:
            query = {}
            if status_filter:
                query["status"] = status_filter
            else:
                 query["status"] = "pending" # Default to pending applications for admin dashboard usually
                
            # If no filter provided, or we strictly want all:
            if status_filter == "all":
                query = {}

            cursor = self.applications.find(query).sort("created_at", -1)
            apps = []
            for doc in cursor:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                # Fetch user email for context
                user = self.users.find_one({"_id": ObjectId(doc["user_id"])})
                doc["user_email"] = user["email"] if user else "Unknown User"
                apps.append(doc)
            return {"success": True, "applications": apps}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_application_status(self, application_id, new_status, admin_notes=""):
        """Update application status (verified/rejected)"""
        try:
            # Get current app to notify user
            app = self.applications.find_one({"_id": ObjectId(application_id)})
            if not app:
                return {"success": False, "error": "Application not found"}
            
            self.applications.update_one(
                {"_id": ObjectId(application_id)},
                {"$set": {
                    "status": new_status, 
                    "admin_notes": admin_notes,
                    "updated_at": datetime.utcnow()
                }}
            )
            
            # Notify user
            note_msg = f" Note: {admin_notes}" if admin_notes else ""
            self.create_notification(
                app["user_id"],
                f"Your application for '{app.get('scheme_title', 'Unknown Scheme')}' is now {new_status.upper()}.{note_msg}"
            )
            
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_notification(self, user_id, message):
        """Create a notification for a user"""
        try:
            notif = {
                "user_id": str(user_id),
                "message": message,
                "is_read": False,
                "created_at": datetime.utcnow()
            }
            self.notifications.insert_one(notif)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def get_user_notifications(self, user_id):
        """Get notifications for a user"""
        try:
            cursor = self.notifications.find({"user_id": str(user_id)}).sort("created_at", -1)
            notifs = []
            for doc in cursor:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                notifs.append(doc)
            return {"success": True, "notifications": notifs}
        except Exception as e:
             return {"success": False, "error": str(e)}

    def mark_notification_read(self, notification_id):
        try:
            self.notifications.update_one(
                {"_id": ObjectId(notification_id)},
                {"$set": {"is_read": True}}
            )
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Initialize database
db = DatabaseManager()
