#!/usr/bin/env python3
"""
Test script for RAG extraction with real Supabase data
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the mcp_server directory to Python path
sys.path.append('mcp_server')

from mcp_server.lib.embeddings import embed
from mcp_server.lib.supabase import search_similar_job_descriptions
from mcp_server.lib.generate import generate_jd

def test_rag_with_real_data():
    """Test the complete RAG pipeline with real Supabase data"""
    
    # Test parameters
    test_title = 'Senior Software Engineer'
    test_department = 'Engineering'
    test_requirements = ['5+ years experience', 'Python knowledge', 'Team collaboration']

    print('🧪 TESTING RAG EXTRACTION WITH REAL SUPABASE DATA')
    print('=' * 60)

    print(f'🔍 Searching for jobs similar to: {test_title} in {test_department}')
    print(f'📋 User requirements: {test_requirements}')

    # Create search query and get embedding
    search_text = f'{test_title} {test_department} {" ".join(test_requirements)}'
    print(f'🔎 Search query: "{search_text}"')

    try:
        print('\n📡 Getting embedding from OpenAI...')
        query_embedding = embed(search_text)
        print(f'✅ Embedding generated (dimension: {len(query_embedding)})')

        print('\n🗄️ Searching Supabase for similar job descriptions...')
        similar_chunks = search_similar_job_descriptions(query_embedding, match_count=5)
        print(f'✅ Found {len(similar_chunks)} similar job chunks')

        # Show what we found
        print('\n📊 SIMILAR JOBS FOUND:')
        for i, chunk in enumerate(similar_chunks, 1):
            job_title = chunk.get('chunk_heading', 'Unknown Job')
            department = chunk.get('department', 'Unknown Dept')
            content_preview = chunk.get('content', '')[:1000] + '...'
            print(f'   {i}. {job_title} ({department})')
            print(f'      Preview: {content_preview}')

        print(f'\n{"="*60}')

        # Test the generation with real data
        result = generate_jd(
            title=test_title,
            department=test_department, 
            requirements=test_requirements,
            similar_chunks=similar_chunks
        )

        print('\n🎯 FINAL GENERATED JOB DESCRIPTION:')
        print('=' * 60)
        import json
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f'❌ Error during testing: {e}')
        print(f'💡 Make sure your .env file has SUPABASE_URL, SUPABASE_SERVICE_ROLE, and OPENAI_API_KEY')

if __name__ == "__main__":
    test_rag_with_real_data()
