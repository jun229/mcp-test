#!/usr/bin/env python3
from typing import Any, List
import json
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

from lib.supabase import supabase, search_similar_chunks
from lib.embeddings import embed
from lib.generate import generate_jd

# Initializing FastMCP server
mcp = FastMCP("jd-generator")   

@mcp.tool()
async def search_and_generate(title: str, department: str, requirements: List[str]) -> str:
    """Search for similar job descriptions and generate a new one"""
    
    # Create search query from inputs
    search_text = f"{title} {department} {' '.join(requirements)}"
    
    # Get embedding for search query
    query_embedding = embed(search_text)
    
    # Search for similar chunks
    similar_chunks = search_similar_chunks(query_embedding, match_count=5)
    
    # Generate job description using similar content
    result = generate_jd(title, department, requirements, similar_chunks)
    
    return json.dumps({
        "generated_jd": result,
        "similar_chunks": similar_chunks,
        "search_query": search_text
    }, indent=2)

if __name__ == "__main__":
    mcp.run(transport='stdio') 