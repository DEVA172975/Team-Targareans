from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import hashlib
import secrets

class UserRegistration(BaseModel):
    name: str
    mobile: str
    email: str
    address: str
    gst_number: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class User(BaseModel):
    id: Optional[int] = None
    name: str
    mobile: str
    email: str
    address: str
    gst_number: str
    is_verified: bool = False
    verification_token: Optional[str] = None
    created_at: datetime = datetime.now()

class UserAuth:
    def __init__(self):
        self.users_db = {}  # In-memory for demo
        self.sessions = {}
    
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        return hashlib.sha256(password.encode()).hexdigest() == hashed
    
    def generate_token(self) -> str:
        return secrets.token_urlsafe(32)
    
    def register_user(self, user_data: UserRegistration) -> dict:
        # Check duplicates
        for user in self.users_db.values():
            if user.email == user_data.email:
                return {"status": "error", "message": "Email already exists"}
            if user.mobile == user_data.mobile:
                return {"status": "error", "message": "Mobile number already exists"}
            if user.gst_number == user_data.gst_number:
                return {"status": "error", "message": "GST number already exists"}
        
        # Create user
        user_id = len(self.users_db) + 1
        verification_token = self.generate_token()
        
        user = User(
            id=user_id,
            name=user_data.name,
            mobile=user_data.mobile,
            email=user_data.email,
            address=user_data.address,
            gst_number=user_data.gst_number,
            verification_token=verification_token
        )
        
        self.users_db[user_id] = user
        
        return {
            "status": "success", 
            "message": "Registration successful. Please verify your email.",
            "verification_token": verification_token,
            "user_id": user_id
        }
    
    def verify_email(self, token: str) -> dict:
        for user in self.users_db.values():
            if user.verification_token == token:
                user.is_verified = True
                user.verification_token = None
                return {"status": "success", "message": "Email verified successfully"}
        return {"status": "error", "message": "Invalid verification token"}
    
    def login_user(self, login_data: UserLogin) -> dict:
        for user in self.users_db.values():
            if user.email == login_data.email:
                if not user.is_verified:
                    return {"status": "error", "message": "Please verify your email first"}
                
                # For demo, we'll skip password verification
                session_token = self.generate_token()
                self.sessions[session_token] = user.id
                
                return {
                    "status": "success",
                    "message": "Login successful",
                    "session_token": session_token,
                    "user": user
                }
        
        return {"status": "error", "message": "Invalid email or password"}
    
    def get_user_by_session(self, session_token: str) -> Optional[User]:
        user_id = self.sessions.get(session_token)
        if user_id:
            return self.users_db.get(user_id)
        return None