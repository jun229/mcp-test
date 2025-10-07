# Job Description Generator - MCP Server

A lightweight MCP (Model Context Protocol) server that helps generate and level job descriptions. This tool can search for similar job postings and generate new ones, plus rewrite job descriptions to match specific experience levels.

## Quick Start

### Step 1: Direct Claude Desktop Integration

Add this to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "JD_Tools": {
      "command": "/Users/YOUR_USERNAME/.local/bin/uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "--with",
        "requests",
        "mcp",
        "run",
        "/path/to/your/mcp-test/mcp_server/vercel_proxy.py"
      ]
    }
  }
}
```

**Replace:**
- `YOUR_USERNAME` with your actual username
- `/path/to/your/mcp-test/` with the actual path to this repository

### Step 2: Local Development Setup

If you want to run and modify the server locally:

1. **Install uv (if not already installed):**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone and navigate to the project:**
   ```bash
   git clone <your-repo-url>
   cd mcp-test/mcp_server
   ```

3. **Create and activate environment:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```bash
   uv pip install -r proxy_requirements.txt
   ```

5. **Run the proxy server:**
   ```bash
   python vercel_proxy.py
   ```

## 🛠️ What This Tool Does

### Available Functions:

1. **`search_and_generate`** - Creates a new job description by searching for similar roles
2. **`leveling_guide`** - Rewrites job descriptions to match specific experience levels (uni1-7, m3-7)

### Example Usage in Claude:

Once connected, you can ask Claude:
- *"Generate a job description for a Senior Software Engineer in the Data team requiring Python and PostgreSQL"*
- *"Rewrite this job description to match a uni5 level"*
- *"Create a job posting for a Frontend Developer with React experience"*

## 📁 File Structure

```
mcp_server/
├── vercel_proxy.py          # Main proxy server (lightweight)
├── proxy_requirements.txt   # Minimal dependencies 
├── main.py                 # Full FastAPI server (for advanced use)
├── requirements.txt        # Full dependencies
└── lib/                    # Additional modules
```

## 🔧 Troubleshooting

### Common Issues:

1. **"uv not found"**
   - Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Restart your terminal

2. **"Permission denied"**
   - Make sure the path in your Claude config is correct
   - Check that `vercel_proxy.py` is executable: `chmod +x vercel_proxy.py`

3. **"Module not found"**
   - Run: `uv pip install -r proxy_requirements.txt`

### Testing the Connection:

You can test if the server is working by running:
```bash
python vercel_proxy.py
```

The server will start and wait for MCP protocol messages.

## 📋 Dependencies

Minimal setup only requires:
- `mcp[cli]` - MCP protocol support
- `requests>=2.32.0` - HTTP requests

## 🌐 Architecture

This proxy forwards requests to a Vercel-hosted API, making it lightweight and easy to run on multiple computers without complex setup or database connections. 
