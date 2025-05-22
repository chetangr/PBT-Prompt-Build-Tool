from fastapi import APIRouter, Query, HTTPException
import os
from supabase import create_client
from datetime import datetime, timedelta

router = APIRouter()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

@router.get("/dashboard")
def get_dashboard_stats():
    """Get overall dashboard statistics"""
    try:
        # Get total prompt packs
        prompts_response = supabase.table("prompt_packs").select("id", count="exact").execute()
        total_prompts = prompts_response.count

        # Get total evaluations
        evals_response = supabase.table("evaluations").select("id", count="exact").execute()
        total_evaluations = evals_response.count

        # Get average score
        scores_response = supabase.table("evaluations").select("score").execute()
        scores = [eval_data["score"] for eval_data in scores_response.data if eval_data["score"]]
        avg_score = sum(scores) / len(scores) if scores else 0

        # Get recent activity
        activity_response = supabase.table("analytics_events").select("*").order("created_at", desc=True).limit(10).execute()
        recent_activity = activity_response.data

        return {
            "totalPrompts": total_prompts,
            "totalEvaluations": total_evaluations,
            "avgScore": avg_score,
            "recentActivity": recent_activity
        }
    except Exception as e:
        return {
            "totalPrompts": 0,
            "totalEvaluations": 0,
            "avgScore": 0,
            "recentActivity": []
        }

@router.get("/usage")
def get_usage_analytics(
    timeframe: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    prompt_id: str = Query(None)
):
    """Get usage analytics for specified timeframe"""
    try:
        # Calculate date range
        days_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
        days = days_map.get(timeframe, 30)
        start_date = datetime.now() - timedelta(days=days)

        query = supabase.table("analytics_events").select("*").gte("created_at", start_date.isoformat())
        
        if prompt_id:
            query = query.eq("prompt_id", prompt_id)
            
        response = query.order("created_at", desc=True).execute()
        events = response.data

        # Aggregate data
        event_counts = {}
        daily_usage = {}
        
        for event in events:
            event_type = event["event_type"]
            event_date = event["created_at"][:10]  # Extract date part
            
            # Count by event type
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            # Count by day
            daily_usage[event_date] = daily_usage.get(event_date, 0) + 1

        return {
            "timeframe": timeframe,
            "total_events": len(events),
            "event_counts": event_counts,
            "daily_usage": daily_usage,
            "events": events[:50]  # Return last 50 events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/popular")
def get_popular_prompts(limit: int = Query(10, le=50)):
    """Get most popular prompt packs"""
    try:
        response = supabase.table("prompt_packs").select("""
            id, name, description, downloads, stars, category, created_at
        """).order("downloads", desc=True).limit(limit).execute()
        
        return {"popular_prompts": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends")
def get_usage_trends(days: int = Query(30, le=365)):
    """Get usage trends over time"""
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        # Get daily download counts
        downloads_response = supabase.table("analytics_events").select(
            "created_at"
        ).eq("event_type", "prompt_download").gte("created_at", start_date.isoformat()).execute()
        
        # Get daily evaluation counts
        evals_response = supabase.table("evaluations").select(
            "created_at"
        ).gte("created_at", start_date.isoformat()).execute()
        
        # Aggregate by day
        daily_downloads = {}
        daily_evaluations = {}
        
        for event in downloads_response.data:
            date = event["created_at"][:10]
            daily_downloads[date] = daily_downloads.get(date, 0) + 1
            
        for eval_event in evals_response.data:
            date = eval_event["created_at"][:10]
            daily_evaluations[date] = daily_evaluations.get(date, 0) + 1
        
        # Create trend data
        dates = []
        downloads = []
        evaluations = []
        
        current_date = start_date
        while current_date <= datetime.now():
            date_str = current_date.strftime("%Y-%m-%d")
            dates.append(date_str)
            downloads.append(daily_downloads.get(date_str, 0))
            evaluations.append(daily_evaluations.get(date_str, 0))
            current_date += timedelta(days=1)
        
        return {
            "dates": dates,
            "downloads": downloads,
            "evaluations": evaluations,
            "total_downloads": sum(downloads),
            "total_evaluations": sum(evaluations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories")
def get_category_stats():
    """Get statistics by prompt category"""
    try:
        response = supabase.table("prompt_packs").select("category, id").execute()
        prompts = response.data
        
        category_counts = {}
        for prompt in prompts:
            category = prompt.get("category", "general")
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            "category_counts": category_counts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/track")
def track_event(
    event_type: str,
    prompt_id: str = None,
    metadata: dict = None
):
    """Track an analytics event"""
    try:
        event_data = {
            "event_type": event_type,
            "prompt_id": prompt_id,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat()
        }
        
        response = supabase.table("analytics_events").insert(event_data).execute()
        return {"success": True, "event_id": response.data[0]["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Legacy endpoint
@router.get("/usage")
def usage_dashboard():
    """Legacy usage dashboard endpoint"""
    return {
        "total_prompts_run": 1234,
        "model_breakdown": {
            "gpt-4": 680,
            "claude-3": 410,
            "mistral": 144
        },
        "top_users": [
            {"user": "alice@example.com", "runs": 312},
            {"user": "bob@corp.com", "runs": 207},
            {"user": "carol@edu.org", "runs": 150}
        ],
        "timestamp": datetime.utcnow().isoformat()
    }