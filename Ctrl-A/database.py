import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
import os

class DatabaseManager:
    def __init__(self, db_path="ctrl_a_users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                phone TEXT NOT NULL,
                disability_type TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Password reset tokens table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_used BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def verify_password(self, password, stored_hash):
        """Verify password against stored hash"""
        try:
            salt, password_hash = stored_hash.split(':')
            return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
        except:
            return False
    
    def create_user(self, email, phone, disability_type, password):
        """Create a new user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (email, phone, disability_type, password_hash)
                VALUES (?, ?, ?, ?)
            ''', (email, phone, disability_type, password_hash))
            
            user_id = cursor.lastrowid
            conn.commit()
            return {"success": True, "user_id": user_id}
        except sqlite3.IntegrityError:
            return {"success": False, "error": "Email already exists"}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
    
    def authenticate_user(self, email, password):
        """Authenticate user login"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, email, phone, disability_type, password_hash, is_active
                FROM users WHERE email = ?
            ''', (email,))
            
            user = cursor.fetchone()
            if not user:
                return {"success": False, "error": "User not found"}
            
            user_id, email, phone, disability_type, password_hash, is_active = user
            
            if not is_active:
                return {"success": False, "error": "Account is deactivated"}
            
            if not self.verify_password(password, password_hash):
                return {"success": False, "error": "Invalid password"}
            
            # Update last login
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user_id,))
            
            conn.commit()
            return {
                "success": True, 
                "user": {
                    "id": user_id,
                    "email": email,
                    "phone": phone,
                    "disability_type": disability_type
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
    
    def create_session(self, user_id):
        """Create a new session for user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Deactivate old sessions
            cursor.execute('''
                UPDATE sessions SET is_active = 0 WHERE user_id = ?
            ''', (user_id,))
            
            # Create new session
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(days=7)  # 7 days session
            
            cursor.execute('''
                INSERT INTO sessions (user_id, session_token, expires_at)
                VALUES (?, ?, ?)
            ''', (user_id, session_token, expires_at))
            
            conn.commit()
            return {"success": True, "session_token": session_token}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
    
    def validate_session(self, session_token):
        """Validate session token and return user info"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT s.user_id, s.expires_at, u.email, u.phone, u.disability_type
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = ? AND s.is_active = 1 AND s.expires_at > CURRENT_TIMESTAMP
            ''', (session_token,))
            
            session = cursor.fetchone()
            if not session:
                return {"success": False, "error": "Invalid or expired session"}
            
            user_id, expires_at, email, phone, disability_type = session
            return {
                "success": True,
                "user": {
                    "id": user_id,
                    "email": email,
                    "phone": phone,
                    "disability_type": disability_type
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
    
    def logout_user(self, session_token):
        """Logout user by deactivating session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE sessions SET is_active = 0 WHERE session_token = ?
            ''', (session_token,))
            conn.commit()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
    
    def create_password_reset_token(self, email):
        """Create password reset token"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get user
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            if not user:
                return {"success": False, "error": "User not found"}
            
            user_id = user[0]
            
            # Deactivate old tokens
            cursor.execute('''
                UPDATE password_reset_tokens SET is_used = 1 WHERE user_id = ?
            ''', (user_id,))
            
            # Create new token
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=1)  # 1 hour expiry
            
            cursor.execute('''
                INSERT INTO password_reset_tokens (user_id, token, expires_at)
                VALUES (?, ?, ?)
            ''', (user_id, token, expires_at))
            
            conn.commit()
            return {"success": True, "token": token}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
    
    def reset_password(self, token, new_password):
        """Reset password using token"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Validate token
            cursor.execute('''
                SELECT user_id FROM password_reset_tokens 
                WHERE token = ? AND is_used = 0 AND expires_at > CURRENT_TIMESTAMP
            ''', (token,))
            
            token_data = cursor.fetchone()
            if not token_data:
                return {"success": False, "error": "Invalid or expired token"}
            
            user_id = token_data[0]
            
            # Update password
            password_hash = self.hash_password(new_password)
            cursor.execute('''
                UPDATE users SET password_hash = ? WHERE id = ?
            ''', (password_hash, user_id))
            
            # Mark token as used
            cursor.execute('''
                UPDATE password_reset_tokens SET is_used = 1 WHERE token = ?
            ''', (token,))
            
            conn.commit()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

# Initialize database
db = DatabaseManager()
