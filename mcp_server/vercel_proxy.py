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

def load_leveling_context(target_level: str = "uni3") -> str:
    """Load relevant leveling guide context based on target level (uni1-7, m3-7)"""
    
    # Input validation
    if not isinstance(target_level, str):
        raise TypeError(f"target_level must be a string, got {type(target_level)}")
    
    if not target_level or not target_level.strip():
        raise ValueError("target_level cannot be empty")
    
    target_level = target_level.strip().lower()
    
    # Validate target level format
    valid_levels = [f"uni{i}" for i in range(1, 8)] + [f"m{i}" for i in range(3, 8)]
    if target_level not in valid_levels:
        raise ValueError(f"Invalid target_level '{target_level}'. Must be one of: {', '.join(valid_levels)}")
    
    context = ""
    leveling_dir = os.path.join(os.path.dirname(__file__), "leveling_guides")
    
    if not os.path.exists(leveling_dir):
        return "No leveling guides found. Please create a 'leveling_guides' directory with reference text files."
    
    if not os.path.isdir(leveling_dir):
        return f"leveling_guides exists but is not a directory: {leveling_dir}"
    
    # Load all .md files, but prioritize ones matching the target level
    try:
        md_files = glob.glob(os.path.join(leveling_dir, "*.md"))
    except Exception as e:
        return f"Error reading leveling guides directory: {str(e)}"
    
    # Sort files - prioritize files that match the target level pattern
    filename_lower = [os.path.basename(f).lower() for f in md_files]
    
    # Exact match first (e.g., "uni3.md" for target "uni3")
    exact_files = [f for f in md_files if target_level.lower() in os.path.basename(f).lower()]
    
    # Then similar levels (e.g., other "uni" files for "uni3", or "m" files for "m5")
    level_type = "uni" if target_level.startswith("uni") else "m" if target_level.startswith("m") else ""
    similar_files = [f for f in md_files if level_type and level_type in os.path.basename(f).lower() and f not in exact_files]
    
    # Finally, general files
    other_files = [f for f in md_files if f not in exact_files and f not in similar_files]
    
    # Always include UNICode if it exists
    unicode_file = os.path.join(leveling_dir, "UNICode.md")
    if os.path.exists(unicode_file) and unicode_file not in (exact_files + similar_files + other_files):
        other_files.insert(0, unicode_file)  # Add at beginning of other_files
    
    # Load files in priority order: exact match → similar level → general (including UNICode)
    files_to_load = (exact_files + similar_files + other_files)[:5]  # Limit to 5 most relevant files
    
    for file_path in files_to_load:
        try:
            # Security: Ensure file is within leveling_guides directory
            real_file_path = os.path.realpath(file_path)
            real_leveling_dir = os.path.realpath(leveling_dir)
            
            if not real_file_path.startswith(real_leveling_dir):
                context += f"\n--- Security error: {file_path} outside leveling_guides directory ---\n"
                continue
            
            # Check file size to prevent memory issues
            file_size = os.path.getsize(file_path)
            if file_size > 1024 * 1024:  # 1MB limit
                context += f"\n--- Warning: {os.path.basename(file_path)} too large ({file_size} bytes), skipping ---\n"
                continue
            
            if file_size == 0:
                context += f"\n--- Warning: {os.path.basename(file_path)} is empty, skipping ---\n"
                continue
            
            # Read file with proper error handling
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                filename = os.path.basename(file_path)
                content = f.read()
                
                # Sanitize content - remove or replace problematic characters
                if not content.strip():
                    context += f"\n--- Warning: {filename} contains no readable content ---\n"
                    continue
                
                # Limit content length to prevent context overflow
                if len(content) > 50000:  # 50k character limit per file
                    content = content[:50000] + "\n... [TRUNCATED - file too long]"
                
                context += f"\n--- {filename} ---\n{content}\n"
                
        except PermissionError:
            context += f"\n--- Permission denied reading {os.path.basename(file_path)} ---\n"
        except UnicodeDecodeError:
            context += f"\n--- Encoding error reading {os.path.basename(file_path)} (not valid UTF-8) ---\n"
        except FileNotFoundError:
            context += f"\n--- File not found: {os.path.basename(file_path)} ---\n"
        except Exception as e:
            context += f"\n--- Error loading {os.path.basename(file_path)}: {str(e)} ---\n"
    
    if not context:
        return "No readable markdown files found in leveling_guides directory."
    
    return context

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

FORMATTING REQUIREMENTS:
- Keep each section concise: 3-4 bullet points maximum unless specified otherwise
- Use direct, impact-focused language that emphasizes ownership and results
- Always end "Nice to Have" section with "Love for unicorns :)" as the final bullet
- Write in human terms that anyone can understand - avoid jargon and complexity
- Emphasize people-first thinking, collaborative problem-solving, and building for the long-term
- Include language about pushing through ambiguity, iterating fast, and creating clarity from complexity

Focus on:
- Years of experience requirements aligned with level
- Level of autonomy and decision-making authority
- Scope of impact and cross-functional responsibility  
- Technical depth vs breadth expectations
- Leadership/mentoring requirements for the level
"""
    
    return prompt

if __name__ == "__main__":
    mcp.run(transport='stdio') 