from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Import lib modules
from lib.supabase import supabase, search_similar_chunks
from lib.embeddings import embed
from lib.generate import generate_jd

app = FastAPI(title="JD Generator API", version="1.0.0")

# Security dependency for REST endpoints
async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing x-api-key header")
    if x_api_key != os.environ.get("MCP_API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid x-api-key")
    return x_api_key

# Security check for MCP endpoints
def verify_mcp_api_key(headers: Dict[str, str]) -> bool:
    api_key = headers.get("x-api-key")
    return api_key == os.environ.get("MCP_API_KEY")

# Request models
class SearchRequest(BaseModel):
    title: str
    department: str
    requirements: List[str]

class IngestRequest(BaseModel):
    content: str

class JsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Any
    method: str
    params: Optional[Dict[str, Any]] = None

# Job description generation uses the generate_jd function directly

# Tool functions
async def search_and_generate_tool(title: str, department: str, requirements: List[str]) -> str:
    """Search for similar job descriptions and generate a new one"""
    
    try:
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
    except Exception as e:
        return json.dumps({
            "error": f"Failed to generate job description: {str(e)}",
            "title": title,
            "department": department,
            "requirements": requirements
        }, indent=2)

async def ingest_tool(content: str) -> str:
    """Add job description content to the database"""
    try:
        # For now, we'll use a simple approach to add content to Supabase
        # In a real implementation, you might want to chunk the content
        # and generate embeddings for better search
        
        # Generate embedding for the content
        embedding = embed(content)
        
        # Insert into the chunks table (assuming this table structure exists)
        result = supabase.table('chunks').insert({
            'content': content,
            'embedding': embedding
        }).execute()
        
        if result.data:
            return "Successfully added job description to database"
        else:
            return "Failed to add job description to database"
            
    except Exception as e:
        return f"Error adding to database: {str(e)}"

# MCP Protocol Handler
@app.post("/mcp")
@app.options("/mcp")
async def mcp_handler(request: Request):
    """Handle MCP protocol requests from Claude Desktop"""
    
    # Handle OPTIONS requests for CORS
    if request.method == "OPTIONS":
        return JSONResponse(
            content={},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, x-api-key",
            }
        )
    
    try:
        # Get request body and headers
        body = await request.json()
        headers = dict(request.headers)
        
        # Verify API key for MCP requests
        if not verify_mcp_api_key(headers):
            return JSONResponse(
                status_code=401,
                content={"jsonrpc": "2.0", "id": body.get("id"), "error": {"code": -32001, "message": "Invalid API key"}}
            )
        
        jsonrpc_req = JsonRpcRequest(**body)
        
        if jsonrpc_req.method == "initialize":
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "id": jsonrpc_req.id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "jd-generator",
                        "version": "1.0.0"
                    }
                }
            })
        
        elif jsonrpc_req.method == "tools/list":
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "id": jsonrpc_req.id,
                "result": {
                    "tools": [
                        {
                            "name": "search_and_generate",
                            "description": "Search for similar job descriptions and generate a new one",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Job title"},
                                    "department": {"type": "string", "description": "Department name"},
                                    "requirements": {"type": "array", "items": {"type": "string"}, "description": "List of requirements"}
                                },
                                "required": ["title", "department", "requirements"]
                            }
                        },
                        {
                            "name": "ingest",
                            "description": "Add job description content to the database for future reference",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "content": {"type": "string", "description": "Job description content to add to the database"}
                                },
                                "required": ["content"]
                            }
                        }
                    ]
                }
            })
        
        elif jsonrpc_req.method == "tools/call":
            tool_name = jsonrpc_req.params.get("name")
            arguments = jsonrpc_req.params.get("arguments", {})
            
            if tool_name == "search_and_generate":
                result = await search_and_generate_tool(
                    title=arguments.get("title"),
                    department=arguments.get("department"),
                    requirements=arguments.get("requirements", [])
                )
                
                return JSONResponse(content={
                    "jsonrpc": "2.0",
                    "id": jsonrpc_req.id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result
                            }
                        ]
                    }
                })
            elif tool_name == "ingest":
                result = await ingest_tool(
                    content=arguments.get("content", "")
                )
                
                return JSONResponse(content={
                    "jsonrpc": "2.0",
                    "id": jsonrpc_req.id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result
                            }
                        ]
                    }
                })
            else:
                return JSONResponse(content={
                    "jsonrpc": "2.0",
                    "id": jsonrpc_req.id,
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                })
        
        else:
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "id": jsonrpc_req.id,
                "error": {"code": -32601, "message": f"Unknown method: {jsonrpc_req.method}"}
            })
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": body.get("id") if 'body' in locals() else None,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            }
        )

# REST API endpoints (kept for other clients)
@app.post("/api/search-and-generate")
async def api_search_and_generate(
    request: SearchRequest,
    _: str = Depends(verify_api_key)
):
    try:
        result = await search_and_generate_tool(
            title=request.title,
            department=request.department,
            requirements=request.requirements
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ingest")
async def api_ingest(
    request: IngestRequest,
    _: str = Depends(verify_api_key)
):
    try:
        result = await ingest_tool(content=request.content)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"status": "ok", "message": "JD Generator API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 