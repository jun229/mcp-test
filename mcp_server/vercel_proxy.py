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
from typing import List

VERCEL_API_URL = "https://mcp-test-pc1y5o5bw-brians-projects-76cf6a1c.vercel.app"
API_KEY = "123123"

mcp = FastMCP("jd-generator-vercel")

def load_leveling_context(target_level: str = "uni3") -> str:
    """Load relevant leveling guide context based on target level (uni1-7, m3-7)"""
    context = ""
    leveling_dir = os.path.join(os.path.dirname(__file__), "leveling_guides")
    
    if not os.path.exists(leveling_dir):
        return "No leveling guides found. Please create a 'leveling_guides' directory with reference text files."
    
    # Load all .md files, but prioritize ones matching the target level
    md_files = glob.glob(os.path.join(leveling_dir, "*.md"))
    
    # Sort files - prioritize files that match the target level pattern
    filename_lower = [os.path.basename(f).lower() for f in md_files]
    
    # Exact match first (e.g., "uni3.md" for target "uni3")
    exact_files = [f for f in md_files if target_level.lower() in os.path.basename(f).lower()]
    
    # Then similar levels (e.g., other "uni" files for "uni3", or "m" files for "m5")
    level_type = "uni" if target_level.startswith("uni") else "m" if target_level.startswith("m") else ""
    similar_files = [f for f in md_files if level_type and level_type in os.path.basename(f).lower() and f not in exact_files]
    
    # Finally, general files
    other_files = [f for f in md_files if f not in exact_files and f not in similar_files]
    
    # Load files in priority order: exact match → similar level → general
    files_to_load = (exact_files + similar_files + other_files)[:3]  # Limit to 8 most relevant files
    
    for file_path in files_to_load:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                filename = os.path.basename(file_path)
                content = f.read()[:3000]  # Truncate each file to 3000 chars
                context += f"\n--- {filename} ---\n{content}\n"
        except Exception as e:
            context += f"\n--- Error loading {file_path}: {str(e)} ---\n"
    
    if not context:
        return "No readable markdown files found in leveling_guides directory."
    
    return context

@mcp.tool()
async def search_and_generate(title: str, department: str, requirements: List[str]) -> str:
    """Search for similar job descriptions and generate a new one using Vercel backend"""
    
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
    
    # Context from reference leveling guides
    leveling_context = load_leveling_context(target_level)
    
    prompt = f"""You are a job description leveling expert. Use the LEVELING GUIDES below as reference:

{leveling_context}

CURRENT JOB DESCRIPTION:
{job_description}

TARGET LEVEL: {target_level}

Your task:
- Rewrite the job description to match the {target_level} level
- Adjust responsibilities, requirements, and expectations accordingly
- Use the leveling guides as reference for appropriate language and expectations
- Keep the same role essence but adjust complexity, autonomy, and impact level
- Output in the same markdown format as the input

Focus on:
- Years of experience requirements
- Level of autonomy and decision-making
- Scope of impact and responsibility  
- Technical depth vs breadth
- Leadership/mentoring expectations
"""
    
    return prompt

if __name__ == "__main__":
    mcp.run(transport='stdio') 