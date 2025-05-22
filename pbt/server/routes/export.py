from fastapi import APIRouter, Body, HTTPException, Response
from fastapi.responses import FileResponse
import os
import csv
import json
import tempfile
from supabase import create_client
from markdownify import markdownify as md
from datetime import datetime
import requests
import io

router = APIRouter()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

@router.post("/csv")
def export_to_csv(prompt_ids: list = Body(...)):
    """Export prompt packs to CSV format"""
    try:
        # Fetch prompt data
        response = supabase.table("prompt_packs").select("*").in_("id", prompt_ids).execute()
        prompts = response.data
        
        # Create CSV in memory
        output = io.StringIO()
        fieldnames = ['name', 'version', 'description', 'category', 'tags', 'created_at', 'downloads', 'yaml_content']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        writer.writeheader()
        for prompt in prompts:
            row = {
                'name': prompt.get('name', ''),
                'version': prompt.get('version', ''),
                'description': prompt.get('description', ''),
                'category': prompt.get('category', ''),
                'tags': ','.join(prompt.get('tags', [])),
                'created_at': prompt.get('created_at', ''),
                'downloads': prompt.get('downloads', 0),
                'yaml_content': prompt.get('yaml_content', '')
            }
            writer.writerow(row)
        
        csv_content = output.getvalue()
        output.close()
        
        return Response(
            content=csv_content,
            media_type='text/csv',
            headers={"Content-Disposition": f"attachment; filename=prompt_packs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting to CSV: {str(e)}")

@router.post("/markdown")
def export_to_markdown(prompt_ids: list = Body(...)):
    """Export prompt packs to Markdown format"""
    try:
        # Fetch prompt data
        response = supabase.table("prompt_packs").select("*").in_("id", prompt_ids).execute()
        prompts = response.data
        
        # Generate Markdown content
        markdown_content = f"# Prompt Packs Export\n\n"
        markdown_content += f"Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for prompt in prompts:
            markdown_content += f"## {prompt.get('name', 'Unnamed')} v{prompt.get('version', '0.0.0')}\n\n"
            markdown_content += f"**Description:** {prompt.get('description', 'No description')}\n\n"
            markdown_content += f"**Category:** {prompt.get('category', 'general')}\n\n"
            
            if prompt.get('tags'):
                markdown_content += f"**Tags:** {', '.join(prompt.get('tags', []))}\n\n"
            
            markdown_content += f"**Downloads:** {prompt.get('downloads', 0)}\n\n"
            markdown_content += f"**Created:** {prompt.get('created_at', 'Unknown')}\n\n"
            
            if prompt.get('yaml_content'):
                markdown_content += f"### YAML Content\n\n```yaml\n{prompt.get('yaml_content', '')}\n```\n\n"
            
            markdown_content += "---\n\n"
        
        return Response(
            content=markdown_content,
            media_type='text/markdown',
            headers={"Content-Disposition": f"attachment; filename=prompt_packs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting to Markdown: {str(e)}")

@router.post("/notion")
def export_to_notion(prompt_ids: list = Body(...), notion_token: str = Body(...), database_id: str = Body(...)):
    """Export prompt packs to Notion database"""
    try:
        # Fetch prompt data
        response = supabase.table("prompt_packs").select("*").in_("id", prompt_ids).execute()
        prompts = response.data
        
        headers = {
            "Authorization": f"Bearer {notion_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        exported_count = 0
        errors = []
        
        for prompt in prompts:
            notion_data = {
                "parent": {"database_id": database_id},
                "properties": {
                    "Name": {
                        "title": [{"text": {"content": prompt.get('name', 'Unnamed')}}]
                    },
                    "Version": {
                        "rich_text": [{"text": {"content": prompt.get('version', '0.0.0')}}]
                    },
                    "Description": {
                        "rich_text": [{"text": {"content": prompt.get('description', 'No description')}}]
                    },
                    "Category": {
                        "select": {"name": prompt.get('category', 'general')}
                    },
                    "Downloads": {
                        "number": prompt.get('downloads', 0)
                    },
                    "Created": {
                        "date": {"start": prompt.get('created_at', datetime.now().isoformat())}
                    }
                },
                "children": [
                    {
                        "object": "block",
                        "type": "code",
                        "code": {
                            "caption": [],
                            "rich_text": [{"type": "text", "text": {"content": prompt.get('yaml_content', '')}}],
                            "language": "yaml"
                        }
                    }
                ]
            }
            
            try:
                response = requests.post(
                    "https://api.notion.com/v1/pages",
                    headers=headers,
                    json=notion_data
                )
                
                if response.status_code == 200:
                    exported_count += 1
                else:
                    errors.append(f"Failed to export {prompt.get('name', 'Unknown')}: {response.text}")
                    
            except Exception as e:
                errors.append(f"Error exporting {prompt.get('name', 'Unknown')}: {str(e)}")
        
        return {
            "success": True,
            "exported_count": exported_count,
            "total_prompts": len(prompts),
            "errors": errors
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting to Notion: {str(e)}")

@router.post("/json")
def export_to_json(prompt_ids: list = Body(...)):
    """Export prompt packs to JSON format"""
    try:
        # Fetch prompt data
        response = supabase.table("prompt_packs").select("*").in_("id", prompt_ids).execute()
        prompts = response.data
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_prompts": len(prompts),
            "prompts": prompts
        }
        
        json_content = json.dumps(export_data, indent=2, default=str)
        
        return Response(
            content=json_content,
            media_type='application/json',
            headers={"Content-Disposition": f"attachment; filename=prompt_packs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting to JSON: {str(e)}")

@router.get("/formats")
def get_export_formats():
    """Get available export formats"""
    return {
        "formats": [
            {
                "id": "csv",
                "name": "CSV (Comma Separated Values)",
                "description": "Spreadsheet-compatible format",
                "endpoint": "/api/export/csv"
            },
            {
                "id": "markdown",
                "name": "Markdown",
                "description": "Human-readable documentation format",
                "endpoint": "/api/export/markdown"
            },
            {
                "id": "notion",
                "name": "Notion Database",
                "description": "Export directly to Notion workspace",
                "endpoint": "/api/export/notion",
                "requires_auth": True
            },
            {
                "id": "json",
                "name": "JSON",
                "description": "Machine-readable data format",
                "endpoint": "/api/export/json"
            }
        ]
    }

# Legacy endpoints for backwards compatibility
@router.get("/markdown")
def export_markdown_legacy():
    """Legacy markdown export endpoint"""
    sample_prompts = [
        {"name": "tweet_summarizer", "description": "Summarize sarcasm", "template": "Summarize: {{ tweet }}"},
        {"name": "product_bot", "description": "Review generator", "template": "Evaluate: {{ specs }}"}
    ]
    return {"markdown": "\n\n".join([f"# {p['name']}\n{p['description']}\n```\n{p['template']}\n```" for p in sample_prompts])}

@router.get("/csv")
def export_csv_legacy():
    """Legacy CSV export endpoint"""
    sample_prompts = [
        {"name": "tweet_summarizer", "description": "Summarize sarcasm", "template": "Summarize: {{ tweet }}"},
        {"name": "product_bot", "description": "Review generator", "template": "Evaluate: {{ specs }}"}
    ]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["name", "description", "template"])
    writer.writeheader()
    writer.writerows(sample_prompts)
    return {"csv": output.getvalue()}