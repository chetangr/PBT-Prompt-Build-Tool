from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel
import os
from supabase import create_client
import jwt

router = APIRouter()
security = HTTPBearer()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    email: str
    password: str
    full_name: str = ""

@router.post("/login")
def login(request: LoginRequest):
    """Login with email and password"""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if response.user:
            return {
                "success": True,
                "user": response.user.model_dump(),
                "session": response.session.model_dump() if response.session else None
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/signup")
def signup(request: SignupRequest):
    """Sign up new user"""
    try:
        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {"full_name": request.full_name}
            }
        })
        
        if response.user:
            return {
                "success": True,
                "user": response.user.model_dump(),
                "message": "Check your email for confirmation link"
            }
        else:
            raise HTTPException(status_code=400, detail="Signup failed")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/logout")
def logout():
    """Logout current user"""
    try:
        supabase.auth.sign_out()
        return {"success": True, "message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/github")
def github_oauth():
    """Initiate GitHub OAuth flow"""
    try:
        response = supabase.auth.sign_in_with_oauth({
            "provider": "github",
            "options": {
                "redirect_to": f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/auth/callback"
            }
        })
        return {"auth_url": response.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/user")
def get_user(token: str = Depends(security)):
    """Get current user info"""
    try:
        # Verify JWT token
        user = supabase.auth.get_user(token.credentials)
        if user:
            return {"user": user.user.model_dump()}
        else:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Unauthorized")

def get_current_user(token: str = Depends(security)):
    """Dependency to get current user from token"""
    try:
        user = supabase.auth.get_user(token.credentials)
        if user and user.user:
            return user.user
        raise HTTPException(status_code=401, detail="Invalid token")
    except:
        raise HTTPException(status_code=401, detail="Unauthorized")