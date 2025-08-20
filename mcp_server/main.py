#!/usr/bin/env python3
from typing import Any, List
import json
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

from lib.supabase import supabase, search_similar_chunks, search_large_corpus_with_reranking
from lib.embeddings import embed
from lib.generate import generate_jd

# Initializing FastMCP server
mcp = FastMCP("jd-generator")   

@mcp.tool()
async def search_and_generate(
    title: str, 
    department: str, 
    requirements: List[str],
    use_reranking: bool = True,
    corpus_size: int = 15000
) -> str:
    """Search for similar job descriptions and generate a new one with optional Cohere reranking"""
    
    # Create search query from inputs
    search_text = f"{title} {department} {' '.join(requirements)}"
    
    # Get embedding for search query
    query_embedding = embed(search_text)
    
    print(f"\n🚀 Starting job description generation for {title} in {department}")
    print(f"📋 Requirements: {requirements}")
    print(f"🔄 Reranking enabled: {use_reranking}")
    print(f"📊 Target corpus size: {corpus_size}")
    
    # Search for similar chunks with reranking
    if use_reranking:
        similar_chunks = await search_large_corpus_with_reranking(
            title=title,
            department=department,
            requirements=requirements,
            query_embedding=query_embedding,
            corpus_size=corpus_size,
            final_count=5
        )
    else:
        # Fallback to basic vector search
        similar_chunks = search_similar_chunks(query_embedding, match_count=5)
    
    print(f"✅ Retrieved {len(similar_chunks)} similar job chunks")
    
    # Generate job description using similar content
    result = generate_jd(title, department, requirements, similar_chunks)
    
    # Prepare response with reranking metadata
    response = {
        "generated_jd": result,
        "similar_chunks": similar_chunks,
        "search_query": search_text,
        "reranking_used": use_reranking,
        "corpus_size": corpus_size
    }
    
    # Add Cohere scoring info if available
    if similar_chunks and 'cohere_score' in similar_chunks[0]:
        response["reranking_scores"] = [
            {
                "position": i+1,
                "cohere_score": chunk.get('cohere_score', 0),
                "similarity": chunk.get('similarity', 0),
                "job_title": chunk.get('job_title', 'Unknown')
            }
            for i, chunk in enumerate(similar_chunks[:3])
        ]
    
    return json.dumps(response, indent=2)

if __name__ == "__main__":
    mcp.run(transport='stdio') 