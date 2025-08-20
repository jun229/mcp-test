import requests, os
from typing import List

def embed(text: str) -> List[float]:
    try:
        api_key = os.environ['OPENAI_API_KEY']
    except KeyError:
        raise EnvironmentError("OPENAI_API_KEY environment variable not set")
    
    try:
        r = requests.post("https://api.openai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": "text-embedding-3-small", "input": text},
            timeout=30)
        r.raise_for_status()  # Raises exception for 4xx/5xx status codes
        
        response_data = r.json()
        return response_data["data"][0]["embedding"]
        
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