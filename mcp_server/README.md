# MCP Server

This is a minimal MCP server in Python using FastAPI.

## Local Development

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Set up environment variables:**
    Create a `.env` file in the `mcp_server` directory and add the following:
    ```ini
    SUPABASE_URL=...
    SUPABASE_SERVICE_ROLE=...
    OPENAI_API_KEY=...
    MCP_API_KEY=DEV_LOCAL_KEY
    ```

3.  **Run the server:**
    ```bash
    uvicorn main:app --reload --port 8787
    ```

## Vercel Deployment

1.  **Install Vercel CLI:**
    ```bash
    npm install -g vercel
    ```

2.  **Deploy:**
    ```bash
    vercel
    ```

## Example `curl` Commands

### Search and Generate
```bash
curl -X POST http://localhost:8787/mcp/search_and_generate \
  -H "Content-Type: application/json" -H "x-api-key: DEV_LOCAL_KEY" \
  -d '{"title":"Senior SWE","department":"Engineering","requirements":["Python","Postgres"]}'
```

### Search Stream
```bash
curl -N -X POST http://localhost:8787/mcp/search_stream \
  -H "Content-Type: application/json" -H "x-api-key: DEV_LOCAL_KEY" \
  -d '{"title":"Senior SWE","department":"Engineering","requirements":["Python","Postgres"]}'
``` 