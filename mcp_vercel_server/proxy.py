#!/usr/bin/env python3
import asyncio
import json
import sys
import requests
from typing import Any, List

# Vercel API configuration
VERCEL_API_URL = "https://mcp-test-jhxtl8tof-brians-projects-76cf6a1c.vercel.app/api/search-and-generate"
API_KEY = "123123"

class MCPProxy:
    def __init__(self):
        self.request_id = 0

    async def handle_request(self, request: dict) -> dict:
        """Handle MCP requests and forward to Vercel API"""
        method = request.get("method")
        request_id = request.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "jd-generator-proxy", "version": "1.0.0"}
                }
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
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
                        }
                    ]
                }
            }

        elif method == "tools/call":
            tool_name = request.get("params", {}).get("name")
            arguments = request.get("params", {}).get("arguments", {})

            if tool_name == "search_and_generate":
                try:
                    # Forward to Vercel API
                    response = requests.post(
                        VERCEL_API_URL,
                        headers={
                            "Content-Type": "application/json",
                            "x-api-key": API_KEY
                        },
                        json={
                            "title": arguments.get("title"),
                            "department": arguments.get("department"),
                            "requirements": arguments.get("requirements", [])
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result_data = response.json()
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": result_data.get("result", "No result returned")
                                    }
                                ]
                            }
                        }
                    else:
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {"code": -32603, "message": f"Vercel API error: {response.status_code} - {response.text}"}
                        }
                        
                except Exception as e:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32603, "message": f"Request failed: {str(e)}"}
                    }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                }

        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Unknown method: {method}"}
            }

    async def run(self):
        """Main loop to handle stdin/stdout communication"""
        proxy = MCPProxy()
        
        while True:
            try:
                # Read request from stdin
                line = sys.stdin.readline()
                if not line:
                    break
                    
                request = json.loads(line.strip())
                
                # Handle the request
                response = await proxy.handle_request(request)
                
                # Send response to stdout
                print(json.dumps(response), flush=True)
                
            except json.JSONDecodeError:
                # Skip invalid JSON
                continue
            except EOFError:
                break
            except Exception as e:
                # Send error response
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
                }
                print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    proxy = MCPProxy()
    asyncio.run(proxy.run()) 