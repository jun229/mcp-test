#!/usr/bin/env python3
"""
Lightweight MCP proxy that forwards requests to Vercel API.
This allows multi-computer hosting while maintaining MCP compatibility.
"""
import json
import requests
import os
import glob
from mcp.server.fastmcp import FastMCP
from typing import List, Tuple

def get_config() -> Tuple[str, str]:
    """Get configuration from environment, config file, or fallback to defaults"""
    # Try environment variables first
    vercel_url = os.environ.get('VERCEL_API_URL')
    api_key = os.environ.get('MCP_API_KEY')
    
    # Try config file if env vars not found
    if not vercel_url or not api_key:
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    vercel_url = vercel_url or config.get('VERCEL_API_URL')
                    api_key = api_key or config.get('API_KEY')
            except Exception:
                pass
    
    # Fallback to defaults (for development only)
    vercel_url = vercel_url or "https://your-deployment.vercel.app"
    api_key = api_key or "dev-api-key"
    
    return vercel_url, api_key

VERCEL_API_URL, API_KEY = get_config()

mcp = FastMCP("jd-generator-vercel")

def load_prompt(prompt_name: str) -> str:
    """Load prompt template from subagents folder"""
    prompt_path = os.path.join(os.path.dirname(__file__), "subagents", f"{prompt_name}.md")
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        return f"Error: Prompt file '{prompt_name}.md' not found"
    except Exception as e:
        return f"Error loading prompt '{prompt_name}.md': {str(e)}"

def load_leveling_context(target_level: str = "uni3") -> str:
    """Load all leveling guide files as context"""
    
    leveling_dir = os.path.join(os.path.dirname(__file__), "leveling_guides")
    
    if not os.path.exists(leveling_dir):
        return "No leveling guides found."
    
    context = ""
    try:
        md_files = glob.glob(os.path.join(leveling_dir, "*.md"))
        for file_path in sorted(md_files):  # Sort for consistent order
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    filename = os.path.basename(file_path)
                    content = f.read().strip()
                    if content:
                        context += f"\n--- {filename} ---\n{content}\n"
            except Exception:
                continue  # Skip files that can't be read
    except Exception:
        return "Error loading leveling guides."
    
    return context if context else "No readable leveling guides found."

@mcp.tool()
async def generate_jd(title: str, department: str, requirements: List[str] = None) -> str:
    """Search for similar job descriptions and generate a new one using Vercel backend.
    
    Args:
        title: Job title (required)
        department: Department name (required) 
        requirements: Specific requirements (optional - leave empty to infer from examples)
    """

    # Validate inputs
    if not title or not title.strip():
        return "Error: Job title is required"
    
    if not department or not department.strip():
        return "Error: Department is required"
    
    if requirements is None:
        requirements = []
        
    # API call to Vercel
    try:
        # Forward request to Vercel REST API endpoint
        response = requests.post(
            f"{VERCEL_API_URL}/api/search-and-generate",
            headers={
                "Content-Type": "application/json",
                "x-api-key": API_KEY
            },
            json={
                "title": title,
                "department": department,
                "requirements": requirements
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result_data = response.json()
            return result_data.get("result", "No result returned from Vercel API")
        else:
            return f"Vercel API Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Failed to connect to Vercel API: {str(e)}"

@mcp.tool()
async def leveling_guide(job_description: str, target_level: str = "uni3") -> str:
    """Rewrite a job description to match a specific level (uni1-7, m3-7) using context from reference files"""
    
    # Load prompt template and leveling context
    prompt_template = load_prompt("leveling_guide")
    leveling_context = load_leveling_context(target_level)
    
    # Format the prompt with variables
    return prompt_template.format(
        leveling_context=leveling_context,
        job_description=job_description,
        target_level=target_level
    )

@mcp.tool()
async def create_rubric(job_description: str, target_level: str = "uni3") -> str:
    """Create comprehensive interview rubric from job description and target level"""
    
    # Load prompt template and leveling context
    prompt_template = load_prompt("rubric_creator")
    leveling_context = load_leveling_context(target_level)
    
    # Format the prompt with variables
    return prompt_template.format(
        target_level=target_level.upper(),
        target_level_lower=target_level,
        leveling_context=leveling_context,
        job_description=job_description
    )

if __name__ == "__main__":
    mcp.run(transport='stdio') 