from supabase import create_client
import os

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_SERVICE_ROLE"]
supabase = create_client(url, key)

def search_similar_chunks(query_embedding, match_count=5):
    """Search for similar chunks using the match_chunks function"""
    result = supabase.rpc('match_chunks', {
        'query_embedding': query_embedding,
        'match_count': match_count
    }).execute()
    return result.data 