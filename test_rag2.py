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
from mcp_server.lib.supabase import search_similar_faq_docs
import openai
import os

def generate_faq_response(query: str, faq_chunks: list, custom_prompt: str = None) -> str:
    """Generate a custom AI response using FAQ chunks and a custom prompt"""
    
    # Default prompt if none provided
    if not custom_prompt:
        custom_prompt = """You are a helpful HR assistant for Uniswap Labs. 
Answer the user's question using the provided FAQ information. 
Be friendly, concise, and helpful. If the information isn't in the FAQs, say so politely. Keep response to under 200 words."""
    
    # Combine FAQ content
    faq_context = "\n\n".join([
        f"FAQ: {chunk.get('chunk_heading', 'Unknown')}\n{chunk.get('content', '')}"
        for chunk in faq_chunks[:5]  # Use top 3 results
    ])
    
    # Create the full prompt
    full_prompt = f"""{custom_prompt}

FAQ Information:
{faq_context}

User Question: {query}

Answer:"""

    try:
        # Initialize OpenAI client
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Generate response using GPT
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # You can change this to gpt-4, gpt-3.5-turbo, etc.
            messages=[
                {"role": "system", "content": custom_prompt},
                {"role": "user", "content": f"Based on this FAQ information:\n\n{faq_context}\n\nQuestion: {query}"}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Error generating AI response: {e}"

def test_faq_search():
    """Test FAQ search with real Supabase data"""

    # Create search query and get embedding
    query = "what gym benefits do we offer"
    print(f'🔍 FAQ Query: "{query}"')

    try:
        query_embedding = embed(query)
        similar_chunks = search_similar_faq_docs(query_embedding, match_count=5)

        # Show what we found
        print('\n📋 FAQ RESULTS:')
        print('=' * 60)
        
        for i, chunk in enumerate(similar_chunks, 1):
            title = chunk.get('chunk_heading', 'Unknown Topic')
            content = chunk.get('content', 'No content available')
            
            print(f'\n{i}. {title}')
            print('-' * 40)
            print(content)
            print()

        # Generate AI response with custom prompt
        if similar_chunks:
            print('\n🤖 GENERATING AI RESPONSE...')
            
            # Custom prompt - you can modify this!
            custom_prompt = """You are a friendly and helpful HR assistant for Uniswap Labs. 
Answer employee questions about benefits and company policies using the FAQ information provided.
Be conversational, warm, and include specific details from the FAQs.
If you don't have the exact information, suggest who they could contact for more details."""
            
            ai_response = generate_faq_response(query, similar_chunks, custom_prompt)
            
            print('\n🎯 AI-GENERATED FAQ ANSWER:')
            print('=' * 60)
            print(f"Question: {query}")
            print(f"Answer: {ai_response}")
            print(f"\nModel Used: gpt-4o-mini")
            
            # Also show raw FAQ for comparison
            print('\n📋 RAW FAQ DATA (for comparison):')
            print('-' * 40)
            best_match = similar_chunks[0]
            print(f"Title: {best_match.get('chunk_heading', 'Unknown')}")
            print(f"Content: {best_match.get('content', 'No content')}")
        else:
            print('\n❌ No FAQ entries found for your query.')
        
    except Exception as e:
        print(f'❌ Error during testing: {e}')
        print(f'💡 Make sure your .env file has SUPABASE_URL, SUPABASE_SERVICE_ROLE, and OPENAI_API_KEY')

if __name__ == "__main__":
    test_faq_search()
