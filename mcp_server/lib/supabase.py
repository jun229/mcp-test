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
    
    # Input validation
    if not isinstance(query_embedding, list):
        raise TypeError(f"query_embedding must be a list, got {type(query_embedding)}")
    
    if len(query_embedding) != 1536:
        raise ValueError(f"query_embedding must have 1536 dimensions, got {len(query_embedding)}")
    
    if not all(isinstance(x, (int, float)) for x in query_embedding):
        raise ValueError("query_embedding must contain only numbers")
    
    if not isinstance(match_count, int):
        raise TypeError(f"match_count must be an integer, got {type(match_count)}")
    
    if match_count < 1 or match_count > 100:
        raise ValueError(f"match_count must be between 1 and 100, got {match_count}")
    
    try:
        # Try to use vector similarity search on job_descriptions table
        result = supabase.rpc('match_jobs', {
            'query_embedding': query_embedding,
            'match_count': match_count
        }).execute()
        
        # Validate result structure
        if not hasattr(result, 'data'):
            logger.error("Supabase result missing 'data' attribute")
            return []
        
        if result.data is None:
            logger.info("No matching job descriptions found")
            return []
        
        if not isinstance(result.data, list):
            logger.error("Supabase returned non-list data: %s", type(result.data))
            return []
        
        # Validate each result item
        validated_results = []
        for item in result.data:
            if not isinstance(item, dict):
                logger.warning("Skipping non-dict result item: %s", type(item))
                continue
            
            # Ensure required fields exist
            if 'id' not in item or 'content' not in item:
                logger.warning("Skipping result item missing required fields")
                continue
                
            validated_results.append(item)
        
        logger.info("Found %d valid job description matches", len(validated_results))
        return validated_results
        
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




 