from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
import os
from anthropic import Anthropic

router = APIRouter()

class SEORequest(BaseModel):
    prompt_name: str
    description: str
    tags: list = []
    target_keywords: list = []

anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

@router.post("/optimize")
def optimize_seo(request: SEORequest):
    """Generate SEO-optimized metadata for a prompt pack"""
    
    system_prompt = f"""You are an SEO expert. Generate optimized metadata for this prompt pack:

Name: {request.prompt_name}
Description: {request.description}
Tags: {request.tags}
Target Keywords: {request.target_keywords}

Generate:
1. SEO-optimized title (under 60 chars)
2. Meta description (under 160 chars)
3. 5-10 relevant tags/keywords
4. Open Graph title and description
5. Schema.org structured data suggestions

Return as JSON with these fields:
{{
  "title": "optimized title",
  "meta_description": "description",
  "keywords": ["keyword1", "keyword2"],
  "og_title": "Open Graph title",
  "og_description": "OG description",
  "schema_type": "SoftwareApplication",
  "structured_data": {{"@type": "SoftwareApplication", "name": "..."}}
}}"""

    try:
        response = anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=800,
            messages=[{"role": "user", "content": system_prompt}]
        )
        
        content = response.content[0].text
        
        # Try to parse as JSON
        import json
        try:
            seo_data = json.loads(content)
            return {"success": True, "seo_metadata": seo_data}
        except json.JSONDecodeError:
            return {"success": False, "raw_content": content}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating SEO metadata: {str(e)}")

@router.post("/analyze")
def analyze_seo(content: str = Body(...), target_keywords: list = Body(...)):
    """Analyze SEO performance of prompt pack content"""
    
    system_prompt = f"""Analyze the SEO quality of this content:

Content: {content}
Target Keywords: {target_keywords}

Provide:
1. Keyword density analysis
2. Content readability score (1-10)
3. SEO recommendations
4. Missing elements
5. Overall SEO score (1-100)

Return as JSON."""

    try:
        response = anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=600,
            messages=[{"role": "user", "content": system_prompt}]
        )
        
        content = response.content[0].text
        
        import json
        try:
            analysis = json.loads(content)
            return {"success": True, "analysis": analysis}
        except json.JSONDecodeError:
            return {"success": False, "raw_content": content}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing SEO: {str(e)}")

@router.post("/sitemap")
def generate_sitemap(prompt_packs: list = Body(...)):
    """Generate XML sitemap for prompt packs"""
    
    sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">"""
    
    base_url = os.getenv("FRONTEND_URL", "https://promptbuildtool.com")
    
    for pack in prompt_packs:
        sitemap_xml += f"""
  <url>
    <loc>{base_url}/packs/{pack.get('name', '')}</loc>
    <lastmod>{pack.get('updated_at', '2024-01-01')}</lastmod>
    <priority>0.8</priority>
  </url>"""
    
    sitemap_xml += """
</urlset>"""
    
    return {"sitemap_xml": sitemap_xml}