from fastapi import APIRouter, Body, Query
from backend.llms.config import generate_prompt_llm, judge_prompt_output
import os
from supabase import create_client
from datetime import datetime, timedelta

router = APIRouter()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

@router.post("/judge")
def judge_outputs(reference: str = Body(...), outputs: list = Body(...), criteria: str = Body("similarity")):
    """Judge prompt outputs using Claude as an evaluator"""
    evals = []
    for out in outputs:
        result = judge_prompt_output(reference, out, criteria)
        evals.append(result)
    return {"evaluations": evals}

@router.get("/chart")
def get_evaluation_chart(range: str = Query("30d"), prompt_id: str = Query(None)):
    """Get evaluation data for charts"""
    try:
        # Calculate date range
        days = int(range.rstrip('d')) if range.endswith('d') else 30
        start_date = datetime.now() - timedelta(days=days)
        
        query = supabase.table("evaluations").select("*")
        
        if prompt_id:
            query = query.eq("prompt_id", prompt_id)
            
        query = query.gte("created_at", start_date.isoformat())
        response = query.order("created_at", desc=True).execute()
        
        evals = response.data or []
        
        # Calculate metrics
        total_evals = len(evals)
        avg_score = sum(e.get("score", 0) for e in evals) / total_evals if total_evals > 0 else 0
        best_performing = max(evals, key=lambda x: x.get("score", 0)) if evals else None
        
        # Calculate trend (simplified)
        recent_avg = sum(e.get("score", 0) for e in evals[:total_evals//2]) / (total_evals//2) if total_evals > 4 else avg_score
        older_avg = sum(e.get("score", 0) for e in evals[total_evals//2:]) / (total_evals//2) if total_evals > 4 else avg_score
        
        trend = "improving" if recent_avg > older_avg else "declining" if recent_avg < older_avg else "stable"
        
        return {
            "evals": evals,
            "metrics": {
                "averageScore": avg_score,
                "totalEvaluations": total_evals,
                "bestPerforming": best_performing,
                "trend": trend
            }
        }
    except Exception as e:
        return {"evals": [], "metrics": {"averageScore": 0, "totalEvaluations": 0, "bestPerforming": None, "trend": "stable"}}

@router.post("/run")
def run_evaluation(prompt_id: str = Body(...), test_cases: list = Body(...), model: str = Body("claude")):
    """Run evaluation on a prompt with test cases"""
    try:
        results = []
        
        for test_case in test_cases:
            # Generate output using the specified model
            prompt_text = test_case.get("prompt", "")
            expected = test_case.get("expected", "")
            
            actual_output = generate_prompt_llm(prompt_text, model)
            evaluation = judge_prompt_output(expected, actual_output)
            
            result = {
                "test_name": test_case.get("name", "Unnamed test"),
                "prompt": prompt_text,
                "expected": expected,
                "actual": actual_output,
                "score": evaluation["score"],
                "passed": evaluation["passed"],
                "explanation": evaluation["explanation"]
            }
            results.append(result)
            
            # Save to database
            eval_data = {
                "prompt_id": prompt_id,
                "prompt_name": test_case.get("prompt_name", "Test"),
                "score": evaluation["score"],
                "pass_rate": 1.0 if evaluation["passed"] else 0.0,
                "model_used": model,
                "test_case": test_case,
                "result": result
            }
            supabase.table("evaluations").insert(eval_data).execute()
        
        # Calculate summary
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r["passed"])
        avg_score = sum(r["score"] for r in results) / total_tests if total_tests > 0 else 0
        
        return {
            "results": results,
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": total_tests - passed_tests,
                "pass_rate": passed_tests / total_tests if total_tests > 0 else 0,
                "average_score": avg_score
            }
        }
        
    except Exception as e:
        return {"error": str(e), "results": []}
