from supabase import create_client
import os
import asyncio
import logging
from typing import List, Dict, Optional

# Set up logging
logger = logging.getLogger(__name__)

try:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_ROLE"]
except KeyError as e:
    raise EnvironmentError(f"Missing required environment variable: {e}")

try:
    supabase = create_client(url, key)
except Exception as e:
    raise ConnectionError(f"Failed to initialize Supabase client: {str(e)}")

def search_similar_job_descriptions(query_embedding: List[float], match_count: int = 5) -> List[Dict[str, Any]]:
    """Search for similar job descriptions using vector similarity"""
    try:
        # Try to use vector similarity search on job_descriptions table
        result = supabase.rpc('match_jobs', {
            'query_embedding': query_embedding,
            'match_count': match_count
        }).execute()
        return result.data if result.data else []
    except Exception as e:
        logger.warning("Vector similarity search failed: %s", e)
        logger.info("Falling back to empty results")
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
        logger.warning("Vector similarity search on faq_docs failed: %s", e)
        logger.info("Falling back to direct table query from faq_docs")
        
        # Fallback: Get FAQ docs from the correct table
        result = supabase.table('faq_docs').select('*').limit(match_count).execute()
        logger.info("Retrieved %d FAQ docs from faq_docs table", len(result.data))
        return result.data




 