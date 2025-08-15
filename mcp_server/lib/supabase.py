from supabase import create_client
import os

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
    print("⚠️ Using legacy search_similar_chunks - consider using search_similar_job_descriptions")
    return search_similar_job_descriptions(query_embedding, match_count) 