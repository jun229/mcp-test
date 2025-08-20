from supabase import create_client
import os
import asyncio
from typing import List, Dict, Optional

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_SERVICE_ROLE"]
supabase = create_client(url, key)

def search_similar_job_descriptions(query_embedding, match_count=5):
    """Search for similar job descriptions using vector similarity"""
    try:
        # Try to use vector similarity search on job_descriptions table
        result = supabase.rpc('match_jobs', {
            'query_embedding': query_embedding,
            'match_count': match_count
        }).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"⚠️ Vector similarity search failed: {e}")
        print("🔄 Falling back to empty results...")
        return []


def search_similar_faq_docs(query_embedding, match_count=5):
    """Search for similar FAQ documents using vector similarity"""
    try:
        # Try to use vector similarity search on faq_docs table
        result = supabase.rpc('match_chunks', {
            'query_embedding': query_embedding,
            'match_count': match_count
        }).execute()
        return result.data
    except Exception as e:
        print(f"⚠️ Vector similarity search on faq_docs failed: {e}")
        print("🔄 Falling back to direct table query from faq_docs...")
        
        # Fallback: Get FAQ docs from the correct table
        result = supabase.table('faq_docs').select('*').limit(match_count).execute()
        print(f"✅ Retrieved {len(result.data)} FAQ docs from faq_docs table")
        return result.data


def search_similar_chunks(query_embedding, match_count=5):
    """Legacy function - defaults to job descriptions for backward compatibility"""
    return search_similar_job_descriptions(query_embedding, match_count)


async def search_with_reranking(
    title: str,
    department: str,
    requirements: List[str],
    query_embedding: List[float],
    final_count: int = 5,
    initial_retrieval: int = 10,
    use_reranking: bool = True
) -> List[Dict]:
    """
    Enhanced search with Cohere reranking for better relevance
    
    Args:
        title: Job title
        department: Department name  
        requirements: List of requirements
        query_embedding: Vector embedding for search
        final_count: Final number of results wanted
        initial_retrieval: How many to retrieve before reranking
        use_reranking: Whether to apply Cohere reranking
        
    Returns:
        List of reranked job descriptions
    """
    
    # Step 1: Get initial candidates from vector search
    # print(f"🔍 Retrieving {initial_retrieval} candidates from vector search...")
    vector_results = search_similar_job_descriptions(query_embedding, initial_retrieval)
    
    if not vector_results:
        print("No vector search results found")
        return []
    
    # print(f"📊 Found {len(vector_results)} vector search results")
    
    # Step 2: Apply reranking if enabled
    if use_reranking:
        try:
            # Import here to avoid circular imports
            from .rerank import rerank_job_descriptions
            
            # print(f"🔄 Applying Cohere reranking...")
            reranked_results = await rerank_job_descriptions(
                title=title,
                department=department,
                requirements=requirements,
                similar_chunks=vector_results,
                final_count=final_count
            )
            
           #  print(f"✅ Reranking complete: {len(reranked_results)} final results")
            return reranked_results
            
        except ImportError:
            print("⚠️ Cohere reranking not available, using vector search only")
        except Exception as e:
            print(f"⚠️ Reranking failed: {e}, falling back to vector search")
    
    # Fallback: return top vector search results
    print(f"📋 Returning top {final_count} vector search results")
    return vector_results[:final_count]


async def search_large_corpus_with_reranking(
    title: str,
    department: str, 
    requirements: List[str],
    query_embedding: List[float],
    corpus_size: int = 15000,
    final_count: int = 5
) -> List[Dict]:
    """
    Handle large corpus search (15k+ documents) with efficient reranking
    
    Strategy:
    1. Vector search gets top 1000-2000 candidates  
    2. Cohere reranks to final top K
    3. Cost optimization through smart pre-filtering
    """
    
    # print(f"🔍 Large corpus search: targeting {corpus_size} documents")
    
    # Adaptive pre-filtering based on corpus size
    if corpus_size >= 15000:
        pre_filter_count = 1500  # Top 1500 for very large corpus
    elif corpus_size >= 5000:
        pre_filter_count = 800   # Top 800 for medium corpus
    else:
        pre_filter_count = 500   # Top 500 for smaller corpus
        
    return await search_with_reranking(
        title=title,
        department=department,
        requirements=requirements,
        query_embedding=query_embedding,
        final_count=final_count,
        initial_retrieval=pre_filter_count,
        use_reranking=True
    ) 