from fastapi import APIRouter, Body, HTTPException, Depends
import os
from supabase import create_client
from routes.auth import get_current_user

router = APIRouter()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

@router.post("/{prompt_id}")
def star_prompt(prompt_id: str, current_user = Depends(get_current_user)):
    """Star or unstar a prompt pack"""
    try:
        user_id = current_user.id
        
        # Check if already starred
        existing = supabase.table("prompt_stars").select("id").eq("user_id", user_id).eq("prompt_id", prompt_id).execute()
        
        if existing.data:
            # Unstar - remove the star
            supabase.table("prompt_stars").delete().eq("user_id", user_id).eq("prompt_id", prompt_id).execute()
            action = "unstarred"
        else:
            # Star - add the star
            supabase.table("prompt_stars").insert({
                "user_id": user_id,
                "prompt_id": prompt_id
            }).execute()
            action = "starred"
        
        # Update star count on prompt pack
        supabase.rpc("increment_stars", {"pack_id": prompt_id}).execute()
        
        # Get updated star count
        stars_response = supabase.table("prompt_stars").select("id", count="exact").eq("prompt_id", prompt_id).execute()
        star_count = stars_response.count
        
        return {
            "success": True,
            "action": action,
            "star_count": star_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{prompt_id}")
def get_prompt_stars(prompt_id: str):
    """Get star count and star status for a prompt"""
    try:
        # Get total star count
        stars_response = supabase.table("prompt_stars").select("id", count="exact").eq("prompt_id", prompt_id).execute()
        star_count = stars_response.count
        
        # Get recent stargazers
        stargazers_response = supabase.table("prompt_stars").select("""
            created_at,
            profiles:user_id(username, avatar_url)
        """).eq("prompt_id", prompt_id).order("created_at", desc=True).limit(10).execute()
        
        stargazers = [
            {
                "username": star["profiles"]["username"] if star["profiles"] else "Anonymous",
                "avatar_url": star["profiles"]["avatar_url"] if star["profiles"] else None,
                "starred_at": star["created_at"]
            }
            for star in stargazers_response.data
        ]
        
        return {
            "star_count": star_count,
            "stargazers": stargazers
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}")
def get_user_starred_prompts(user_id: str):
    """Get all prompts starred by a user"""
    try:
        response = supabase.table("prompt_stars").select("""
            created_at,
            prompt_packs:prompt_id(id, name, description, category, downloads, stars)
        """).eq("user_id", user_id).order("created_at", desc=True).execute()
        
        starred_prompts = [
            {
                "starred_at": star["created_at"],
                "prompt": star["prompt_packs"]
            }
            for star in response.data
        ]
        
        return {"starred_prompts": starred_prompts}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rate")
def rate_prompt(prompt_id: str = Body(...), rating: int = Body(...), current_user = Depends(get_current_user)):
    """Rate a prompt pack (1-5 stars)"""
    if not 1 <= rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    try:
        user_id = current_user.id
        
        # Check if user already rated this prompt
        existing = supabase.table("prompt_ratings").select("id").eq("user_id", user_id).eq("prompt_id", prompt_id).execute()
        
        if existing.data:
            # Update existing rating
            supabase.table("prompt_ratings").update({
                "rating": rating
            }).eq("user_id", user_id).eq("prompt_id", prompt_id).execute()
        else:
            # Create new rating
            supabase.table("prompt_ratings").insert({
                "user_id": user_id,
                "prompt_id": prompt_id,
                "rating": rating
            }).execute()
        
        # Calculate new average rating
        ratings_response = supabase.table("prompt_ratings").select("rating").eq("prompt_id", prompt_id).execute()
        ratings = [r["rating"] for r in ratings_response.data]
        average_rating = sum(ratings) / len(ratings) if ratings else 0
        
        return {
            "success": True,
            "average_rating": round(average_rating, 2),
            "total_ratings": len(ratings)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/popular")
def get_popular_prompts(limit: int = 10):
    """Get most starred prompt packs"""
    try:
        response = supabase.table("prompt_packs").select("""
            id, name, description, stars, downloads, category, created_at
        """).order("stars", desc=True).limit(limit).execute()
        
        return {"popular_prompts": response.data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Legacy endpoint for backwards compatibility
@router.post("/rate")
def rate_prompt_legacy(name: str = Body(...), stars: int = Body(...)):
    """Legacy rating endpoint"""
    # This is a simplified in-memory version for backwards compatibility
    ratings = {}  # In reality, this would be persistent storage
    ratings[name] = ratings.get(name, [])
    ratings[name].append(stars)
    return { 
        "average": sum(ratings[name]) / len(ratings[name]), 
        "votes": len(ratings[name]) 
    }