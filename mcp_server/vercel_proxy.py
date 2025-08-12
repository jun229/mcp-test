#!/usr/bin/env python3
"""
Lightweight MCP proxy that forwards requests to Vercel API.
This allows multi-computer hosting while maintaining MCP compatibility.
"""
import json
import requests
from mcp.server.fastmcp import FastMCP
from typing import List

# Vercel configuration - update this URL for your deployment
VERCEL_API_URL = "https://mcp-test-3p5bwgfx7-brians-projects-76cf6a1c.vercel.app/api/search-and-generate"
API_KEY = "123123"

mcp = FastMCP("jd-generator-vercel")

@mcp.tool()
async def search_and_generate(title: str, department: str, requirements: List[str]) -> str:
    """Search for similar job descriptions and generate a new one using Vercel backend"""
    
    try:
        # Forward request to Vercel API
        response = requests.post(
            VERCEL_API_URL,
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

if __name__ == "__main__":
    mcp.run(transport='stdio') 