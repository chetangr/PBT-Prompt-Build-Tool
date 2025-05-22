from fastapi import APIRouter, Body, HTTPException, Depends
from pydantic import BaseModel
import os
from supabase import create_client
from routes.auth import get_current_user

router = APIRouter()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

class PromptPackCreate(BaseModel):
    name: str
    description: str
    content: str
    version: str = "0.1.0"
    tags: list = []
    category: str = "general"
    price: float = 0.0
    is_public: bool = True

class PromptPackUpdate(BaseModel):
    description: str = None
    content: str = None
    tags: list = None
    category: str = None
    price: float = None
    is_public: bool = None

@router.get("/list")
def list_prompt_packs(category: str = None, user_id: str = None):
    """List all public prompt packs"""
    try:
        query = supabase.table("prompt_packs").select("*").eq("is_public", True)
        
        if category and category != "all":
            query = query.eq("category", category)
        if user_id:
            query = query.eq("user_id", user_id)
            
        response = query.order("created_at", desc=True).execute()
        return {"prompts": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/marketplace")
def get_marketplace_packs():
    """Get prompt packs for the marketplace"""
    try:
        response = supabase.table("prompt_packs").select("""
            *,
            profiles:user_id(username, avatar_url)
        """).eq("is_public", True).order("downloads", desc=True).execute()
        
        # Add some mock data for demonstration
        marketplace_data = response.data or []
        
        # Add featured flag and other marketplace-specific data
        for pack in marketplace_data:
            pack["featured"] = pack.get("downloads", 0) > 100
            pack["author"] = pack.get("profiles", {}).get("username", "Anonymous")
            pack["rating"] = 4.2 + (hash(pack["name"]) % 20) / 20  # Mock rating
            
        return {"packs": marketplace_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create")
def create_prompt_pack(pack: PromptPackCreate, current_user = Depends(get_current_user)):
    """Create a new prompt pack"""
    try:
        pack_data = {
            **pack.dict(),
            "user_id": current_user.id,
            "downloads": 0,
            "stars": 0
        }
        
        response = supabase.table("prompt_packs").insert(pack_data).execute()
        return {"success": True, "pack": response.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{pack_id}")
def get_prompt_pack(pack_id: str):
    """Get a specific prompt pack"""
    try:
        response = supabase.table("prompt_packs").select("""
            *,
            profiles:user_id(username, avatar_url)
        """).eq("id", pack_id).single().execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Prompt pack not found")
            
        return {"pack": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{pack_id}")
def update_prompt_pack(pack_id: str, updates: PromptPackUpdate, current_user = Depends(get_current_user)):
    """Update a prompt pack"""
    try:
        # Check ownership
        existing = supabase.table("prompt_packs").select("user_id").eq("id", pack_id).single().execute()
        if not existing.data or existing.data["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this pack")
        
        # Update only provided fields
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        response = supabase.table("prompt_packs").update(update_data).eq("id", pack_id).execute()
        
        return {"success": True, "pack": response.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{pack_id}")
def delete_prompt_pack(pack_id: str, current_user = Depends(get_current_user)):
    """Delete a prompt pack"""
    try:
        # Check ownership
        existing = supabase.table("prompt_packs").select("user_id").eq("id", pack_id).single().execute()
        if not existing.data or existing.data["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this pack")
        
        supabase.table("prompt_packs").delete().eq("id", pack_id).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{pack_id}/download")
def download_prompt_pack(pack_id: str):
    """Increment download count for a prompt pack"""
    try:
        # Increment download count
        supabase.rpc("increment_downloads", {"pack_id": pack_id}).execute()
        
        # Get the updated pack data
        response = supabase.table("prompt_packs").select("*").eq("id", pack_id).single().execute()
        return {"success": True, "pack": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save")
def save_prompt_pack(
    name: str = Body(...),
    version: str = Body(...),
    content: str = Body(...),
    description: str = Body(""),
    tags: list = Body([])
):
    """Save a prompt pack (for demo purposes, doesn't require auth)"""
    try:
        pack_data = {
            "name": name,
            "version": version,
            "yaml_content": content,
            "description": description,
            "tags": tags,
            "user_id": "demo-user",  # For demo purposes
            "is_public": True,
            "downloads": 0,
            "stars": 0,
            "category": "generated"
        }
        
        response = supabase.table("prompt_packs").insert(pack_data).execute()
        return {"success": True, "pack": response.data[0]}
    except Exception as e:
        return {"success": False, "error": str(e)}