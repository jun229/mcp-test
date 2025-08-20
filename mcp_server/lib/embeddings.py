import requests, os
from typing import List

def embed(text: str) -> List[float]:
    # Input validation and sanitization
    if not isinstance(text, str):
        raise TypeError(f"Expected string input, got {type(text)}")
    
    if not text or not text.strip():
        raise ValueError("Input text cannot be empty or whitespace-only")
    
    # OpenAI has a token limit (~8192 tokens, roughly 32k characters for safety)
    if len(text) > 32000:
        raise ValueError(f"Text too long: {len(text)} chars (max 32000)")
    
    # Sanitize text - remove null bytes and control characters that could break JSON
    sanitized_text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    try:
        api_key = os.environ['OPENAI_API_KEY']
        if not api_key or not api_key.strip():
            raise EnvironmentError("OPENAI_API_KEY is set but empty")
    except KeyError:
        raise EnvironmentError("OPENAI_API_KEY environment variable not set")
    
    try:
        r = requests.post("https://api.openai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {api_key.strip()}"},
            json={"model": "text-embedding-3-small", "input": sanitized_text},
            timeout=30)
        r.raise_for_status()  # Raises exception for 4xx/5xx status codes
        
        response_data = r.json()
        
        # Validate response structure
        if not isinstance(response_data, dict):
            raise ValueError("OpenAI API returned non-dict response")
        
        if "data" not in response_data:
            raise ValueError("OpenAI API response missing 'data' field")
        
        if not response_data["data"] or len(response_data["data"]) == 0:
            raise ValueError("OpenAI API returned empty data array")
        
        embedding = response_data["data"][0]["embedding"]
        
        # Validate embedding format
        if not isinstance(embedding, list):
            raise ValueError("Embedding is not a list")
        
        if len(embedding) != 1536:  # text-embedding-3-small dimension
            raise ValueError(f"Unexpected embedding dimension: {len(embedding)}, expected 1536")
        
        # Validate embedding values are numbers
        if not all(isinstance(x, (int, float)) for x in embedding):
            raise ValueError("Embedding contains non-numeric values")
        
        return embedding
        
    except requests.ConnectionError:
        raise ConnectionError("Failed to connect to OpenAI API")
    except requests.Timeout:
        raise TimeoutError("OpenAI API request timed out")
    except requests.HTTPError as e:
        raise RuntimeError(f"OpenAI API error: {e.response.status_code} - {e.response.text}")
    except KeyError as e:
        raise ValueError(f"Unexpected OpenAI API response format: missing {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error calling OpenAI API: {str(e)}") 