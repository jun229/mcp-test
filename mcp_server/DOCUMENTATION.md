# 📋 Job Description Generator - MCP Server Documentation

## 📖 Overview

The Job Description Generator is a **robust, production-ready** AI-powered system that creates and optimizes job descriptions using RAG (Retrieval-Augmented Generation) technology. It integrates with Claude Desktop via the Model Context Protocol (MCP) to provide intelligent job description generation and leveling based on existing job postings stored in a vector database.

### Key Features
- 🔍 **Semantic Search**: Uses OpenAI embeddings to find similar job descriptions via vector similarity
- 🤖 **RAG-Powered Prompts**: Provides context-rich prompts for Claude to generate job descriptions
- 📈 **Experience Leveling**: Automatically adjusts job descriptions for specific experience levels (uni1-7, m3-7)
- 🛡️ **Enterprise-Grade Robustness**: Comprehensive input validation, error handling, and monitoring
- 💬 **Claude Desktop Integration**: Seamless integration via MCP protocol
- ☁️ **Distributed Architecture**: Lightweight local proxy + cloud backend
- 📊 **Operational Monitoring**: Request logging, health checks, and performance metrics
- 🔒 **Security Hardened**: Input sanitization, directory traversal protection, resource limits

### Architecture
```
Claude Desktop → MCP Protocol → Local Proxy → Vercel API → Vector DB (Supabase)
                                                    ↓
                                      OpenAI Embeddings (text-embedding-3-small)
```

---

## 🗂️ Project Structure

```
mcp_server/
├── vercel_proxy.py          # MCP server entry point (robust file handling)
├── api.py                   # FastAPI backend with comprehensive monitoring
├── lib/                     # Core modules with enterprise-grade validation
│   ├── embeddings.py        # OpenAI integration with full input/output validation
│   └── supabase.py          # Vector database interface with error recovery
├── leveling_guides/         # Experience level references (15 files)
├── requirements.txt         # Streamlined dependencies (6 packages)
├── config.json              # Local configuration (gitignored)
├── TODO.md                  # Completed improvements tracker
└── DOCUMENTATION.md        # This file
```

---

## 📦 Core Modules

### `vercel_proxy.py` - MCP Server
**Purpose**: Local MCP protocol server with robust file handling and configuration management.

**Key Features**:
- **Smart Configuration**: Environment variables → config file → fallback defaults
- **Input Validation**: Comprehensive validation for all MCP tool parameters  
- **File Security**: Directory traversal protection, size limits, encoding safety
- **Leveling Intelligence**: Prioritizes exact matches → similar levels → general guides

**MCP Tools Exposed**:
```python
@mcp.tool()
async def search_and_generate(title: str, department: str, requirements: List[str] = None) -> str
    # Generates job descriptions with RAG-based context

@mcp.tool() 
async def leveling_guide(job_description: str, target_level: str = "uni3") -> str
    # Adjusts job descriptions to specific experience levels
```

**Robustness Features**:
- ✅ **Input sanitization** - Validates title, department, target_level format
- ✅ **File safety** - 1MB file size limit, UTF-8 encoding with error replacement
- ✅ **Resource protection** - 50k character limit per leveling guide file
- ✅ **Security hardening** - Prevents directory traversal attacks

### `api.py` - FastAPI Backend
**Purpose**: Cloud-hosted API with enterprise-grade monitoring and error handling.

**Key Features**:
- **Request/Response Middleware**: Automatic logging of all API calls with timing
- **Comprehensive Health Checks**: Tests database, environment, file system, memory
- **Specific Error Handling**: Different handling for configuration, connection, timeout, data errors
- **MCP Protocol Compliance**: Full JSON-RPC 2.0 implementation

**API Endpoints**:
- `POST /mcp` - MCP protocol handler (primary interface)
- `POST /api/search-and-generate` - REST API for external clients  
- `GET /health` - Comprehensive system health with diagnostics
- `GET /` - Basic service status

**Health Check Response Example**:
```json
{
  "status": "healthy",
  "timestamp": 1703123456.789,
  "checks": {
    "environment": "✅ All required variables present",
    "database": "✅ Connected",
    "openai_config": "✅ API key configured", 
    "file_system": "✅ Leveling guides accessible",
    "memory": "✅ Normal usage: 45.3MB"
  },
  "details": {
    "db_response_time_ms": 234.5,
    "db_has_data": true,
    "leveling_guide_files": 15
  }
}
```

### `lib/embeddings.py` - OpenAI Integration
**Purpose**: Robust wrapper for OpenAI embedding API with comprehensive validation.

**Key Function**:
```python
def embed(text: str) -> List[float]:
    """Convert text to 1536-dimensional embedding with full validation"""
```

**Robustness Features**:
- ✅ **Input validation** - Type checking, empty detection, length limits (32k chars)
- ✅ **Text sanitization** - Removes control characters that break JSON
- ✅ **API key validation** - Checks for empty/whitespace-only keys
- ✅ **Response validation** - Ensures 1536-dimensional numeric vectors
- ✅ **Specific error handling** - Connection, timeout, HTTP, parsing errors

**Usage**:
```python
from lib.embeddings import embed

try:
    vector = embed("Senior Software Engineer Python PostgreSQL")
    # Returns List[float] with 1536 dimensions
except ValueError as e:
    # Handle input validation errors
except ConnectionError as e:
    # Handle API connection issues
```

### `lib/supabase.py` - Vector Database
**Purpose**: Interface to Supabase vector database with comprehensive error recovery.

**Key Functions**:
```python
def search_similar_job_descriptions(query_embedding: List[float], match_count: int = 5) -> List[Dict[str, Any]]
def search_similar_faq_docs(query_embedding: List[float], match_count: int = 5) -> List[Dict[str, Any]]
```

**Robustness Features**:
- ✅ **Vector validation** - Ensures 1536-dimensional numeric embeddings
- ✅ **Parameter bounds checking** - match_count between 1-100
- ✅ **Response structure validation** - Validates database response format
- ✅ **Result item validation** - Ensures required fields (id, content) present
- ✅ **Graceful degradation** - Returns empty arrays on failure, logs issues

**Database Tables**:
- `job_descriptions` - Job postings with vector embeddings (via `match_jobs` RPC)
- `faq_docs` - FAQ documents with embeddings (via `match_chunks` RPC)

### `leveling_guides/` - Experience References
**Purpose**: Reference documentation for different experience levels (15 markdown files).

**Structure**:
- `UNICode.md` - Universal coding standards
- `uni1.md` to `uni7.md` - University graduate levels (junior to senior)  
- `m3.md` to `m7.md` - Management levels
- `general_framework.md` - General leveling principles
- Additional role-specific guides (VP, SVP levels)

**Smart Loading**:
- Prioritizes exact matches (e.g., `uni3.md` for target "uni3")
- Falls back to similar levels (other uni files for uni targets)
- Includes general guidance files
- Limited to 5 most relevant files per request

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8+
- uv package manager (recommended) or pip
- Claude Desktop application
- API keys: OpenAI, Supabase (required for full functionality)

### Quick Start

1. **Install uv package manager** (if not installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Setup project**:
   ```bash
   git clone <repository-url>
   cd mcp_server
   uv venv
   source .venv/bin/activate  # Linux/Mac
   # OR .venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```bash
   uv pip install -r requirements.txt
   ```

4. **Configure environment** (choose one method):

   **Method 1: Environment Variables** (Recommended)
   ```bash
   export VERCEL_API_URL="your-vercel-deployment-url"
   export MCP_API_KEY="your-api-key"  
   export OPENAI_API_KEY="your-openai-key"
   export SUPABASE_URL="your-supabase-url"
   export SUPABASE_SERVICE_ROLE="your-supabase-key"
   ```

   **Method 2: Claude Desktop Configuration**
   ```json
   {
     "mcpServers": {
       "JD_Tools": {
         "command": "/path/to/.local/bin/uv",
         "args": ["run", "--with", "mcp[cli]", "mcp", "run", "/path/to/vercel_proxy.py"],
         "env": {
           "VERCEL_API_URL": "your-deployment-url",
           "MCP_API_KEY": "your-api-key",
           "OPENAI_API_KEY": "your-openai-key"
         }
       }
     }
   }
   ```

   **Method 3: Local Config File** (Development Only)
   ```bash
   cp config.json.example config.json
   # Edit config.json with your values (ensure it's in .gitignore!)
   ```

5. **Verify installation**:
   ```bash
   # Test MCP server
   python vercel_proxy.py
   
   # Test API server (if running backend locally)
   python api.py
   
   # Check health endpoint
   curl http://localhost:8000/health
   ```

### Claude Desktop Integration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) or equivalent:

```json
{
  "mcpServers": {
    "JD_Tools": {
      "command": "/Users/YOUR_USERNAME/.local/bin/uv",
      "args": [
        "run", "--with", "mcp[cli]", "--with", "requests",
        "mcp", "run", "/path/to/mcp_server/vercel_proxy.py"
      ],
      "env": {
        "VERCEL_API_URL": "https://your-deployment.vercel.app",
        "MCP_API_KEY": "your-api-key"
      }
    }
  }
}
```

**Important**: Replace paths and URLs with your actual values.

---

## 🚀 Usage Examples

### Basic Job Description Generation
```
# In Claude Desktop (after MCP setup)
User: "Generate a job description for a Senior Frontend Engineer in the Engineering team requiring React and TypeScript"

# System workflow:
# 1. Validates inputs (title: "Senior Frontend Engineer", department: "Engineering")
# 2. Creates search embedding from "Senior Frontend Engineer Engineering React TypeScript"
# 3. Searches vector database for similar job descriptions (top 5)
# 4. Returns context-rich prompt with examples for Claude to generate new job description
```

### Experience Level Adjustment
```
User: "Rewrite this job description to match a uni5 level"

# System workflow:
# 1. Validates target_level format (uni5 is valid: uni1-7, m3-7)
# 2. Loads relevant leveling guides (uni5.md, other uni files, UNICode.md, general)
# 3. Returns comprehensive prompt with leveling context and formatting requirements
```

### Health Monitoring
```bash
# Check system health
curl http://localhost:8000/health

# Response includes:
# - Environment variable validation
# - Database connectivity with response time
# - OpenAI configuration status
# - File system access verification
# - Memory usage monitoring
```

### API Integration (External Clients)
```python
import requests

# Generate job description via REST API
response = requests.post(
    "https://your-vercel-app.vercel.app/api/search-and-generate",
    headers={"x-api-key": "your-api-key"},
    json={
        "title": "Data Scientist",
        "department": "Analytics", 
        "requirements": ["Python", "SQL", "Machine Learning"]
    }
)

if response.status_code == 200:
    prompt = response.json()["result"]
    # Use prompt with your AI model
else:
    print(f"Error: {response.status_code} - {response.text}")
```

---

## 🔧 Development & Testing

### Running in Development Mode

```bash
# Start MCP server (for Claude Desktop integration)
python vercel_proxy.py

# Start API server (for REST API testing)  
python api.py

# Monitor logs (both servers include comprehensive logging)
tail -f logs/api.log  # If logging to file
```

### Testing Individual Components

```bash
# Test embedding function
python -c "
from lib.embeddings import embed
result = embed('test text')
print(f'Embedding length: {len(result)}')
print('✅ Embedding function works')
"

# Test database connection
python -c "
from lib.supabase import search_similar_job_descriptions
import json
result = search_similar_job_descriptions([0.1]*1536, 1)
print(f'Database test: {len(result)} results')
print('✅ Database connection works')
"

# Test health endpoint
curl http://localhost:8000/health | jq .
```

### Debugging Common Issues

**1. MCP Connection Issues**
```bash
# Check Claude Desktop logs
tail -f ~/Library/Logs/Claude/claude_desktop.log

# Verify MCP server starts without errors
python vercel_proxy.py
# Should start without exceptions
```

**2. Database Connection Issues**
```bash
# Test Supabase connection
curl http://localhost:8000/health
# Check "database" and "environment" status
```

**3. Environment Variable Issues**
```bash
# Verify required vars are set
echo $SUPABASE_URL
echo $OPENAI_API_KEY
# Should output your actual values, not empty
```

---

## 🛡️ Security & Robustness

### Input Validation
- **Type checking** on all user inputs
- **Length limits** to prevent API abuse (32k chars for embeddings)
- **Format validation** for experience levels (uni1-7, m3-7)
- **Sanitization** of text inputs to remove control characters

### File System Security
- **Directory traversal protection** prevents access outside leveling_guides/
- **File size limits** (1MB per file) prevent memory exhaustion
- **Content length limits** (50k chars per file) prevent context overflow
- **Encoding safety** with UTF-8 error replacement

### Resource Management
- **Request timeouts** (30s) prevent hanging calls
- **Memory monitoring** in health checks
- **Database connection validation** with response time tracking
- **Graceful error recovery** with detailed logging

### API Security
- **API key validation** for all endpoints
- **Input sanitization** prevents injection attacks
- **Error message sanitization** prevents information leakage
- **Request logging** for audit trails

---

## 📊 Monitoring & Observability

### Request Logging
All HTTP requests automatically logged with:
```
INFO: POST /api/search-and-generate - 200 - 1.234s - 127.0.0.1
INFO: GET /health - 200 - 0.012s - 127.0.0.1
INFO: POST /mcp - 500 - 0.845s - 127.0.0.1
```

### Health Monitoring
Comprehensive health checks include:
- ✅ **Environment Variables**: All required configs present
- ✅ **Database Connectivity**: Response time and data availability  
- ✅ **API Configuration**: Service keys properly configured
- ✅ **File System Access**: Leveling guides accessible
- ✅ **Memory Usage**: Process memory monitoring

### Error Tracking
Structured error handling with specific exception types:
- `EnvironmentError`: Configuration issues
- `ConnectionError`: Database/API connectivity
- `TimeoutError`: Request timeouts
- `ValueError`: Invalid input data
- `RuntimeError`: Unexpected system errors

### Performance Metrics
- Database response times tracked
- Memory usage monitoring
- File loading performance
- Request processing times

---

## 🧪 Production Readiness

### ✅ Completed Improvements
- **Input Validation**: Comprehensive validation for all inputs
- **Error Handling**: Specific exception handling with recovery
- **Security Hardening**: Directory traversal protection, sanitization
- **Resource Management**: File size limits, memory monitoring
- **Request Logging**: Automatic request/response logging middleware
- **Health Monitoring**: Multi-component health checks with diagnostics
- **Code Quality**: Type hints, proper logging, clean architecture

### 📈 Scalability Features
- **Stateless Design**: No local state, easy horizontal scaling
- **Connection Pooling**: Database connections managed efficiently  
- **Resource Limits**: Prevents resource exhaustion under load
- **Graceful Degradation**: Continues working with partial failures
- **Caching Ready**: Architecture supports adding caching layers

### 🔍 Observability
- **Structured Logging**: JSON-formatted logs with context
- **Health Endpoints**: Machine-readable health status
- **Performance Metrics**: Response times and resource usage
- **Error Categorization**: Specific error types for monitoring

---

## 🤝 Contributing

### Development Setup
1. Follow installation instructions above
2. Install development dependencies: `uv pip install -r requirements-dev.txt` (if available)
3. Run tests: `python -m pytest` (when test suite is added)
4. Check code formatting: `black --check .` (if configured)

### Code Standards
- **Type Hints**: Required for all function signatures
- **Input Validation**: All user inputs must be validated
- **Error Handling**: Use specific exception types, not generic `Exception`
- **Logging**: Use `logging` module, not `print()` statements
- **Documentation**: Docstrings required for public functions
- **Security**: Consider security implications of all user inputs

### Testing Guidelines
- **Unit Tests**: Test individual functions with various inputs
- **Integration Tests**: Test API endpoints and database interactions
- **Error Cases**: Test validation failures and error recovery
- **Performance**: Monitor response times and resource usage

---

## 📋 Dependencies

### Core Dependencies (6 packages)
```
fastapi>=0.115.0      # Web framework
uvicorn>=0.35.0       # ASGI server  
supabase>=2.18.0      # Database client
python-dotenv>=1.1.1  # Environment management
requests>=2.32.0      # HTTP client
pydantic>=2.0.0       # Data validation
```

### Optional Dependencies
```
psutil                # Memory monitoring in health checks
pytest                # Testing framework (future)
black                 # Code formatting (future)
```

**Note**: Streamlined from 8 to 6 core dependencies during cleanup.

---

## 🐛 Troubleshooting

### Common Issues

**1. "OPENAI_API_KEY environment variable not set"**
- **Solution**: Set the environment variable or add to config.json
- **Check**: `echo $OPENAI_API_KEY` should show your key

**2. "Failed to initialize Supabase client"**
- **Solution**: Verify SUPABASE_URL and SUPABASE_SERVICE_ROLE are correct
- **Check**: Health endpoint shows specific database errors

**3. "No leveling guides found"**
- **Solution**: Ensure `leveling_guides/` directory exists with .md files
- **Check**: Health endpoint reports leveling guide file count

**4. MCP tool not appearing in Claude**
- **Solution**: Verify Claude Desktop config path and restart Claude
- **Check**: Claude Desktop logs for MCP connection errors

**5. "Request timeout" errors**
- **Solution**: Check network connectivity to OpenAI/Supabase
- **Check**: Health endpoint shows response times

### Getting Help
1. **Check health endpoint**: `curl http://localhost:8000/health`
2. **Review logs**: Look for specific error messages
3. **Validate configuration**: Ensure all required environment variables are set
4. **Test components individually**: Use the testing commands above
5. **Check Claude Desktop logs**: For MCP-specific issues

---

## 🔗 Related Resources

### Documentation Links
- [Claude Desktop Documentation](https://docs.anthropic.com/claude/docs)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Supabase Vector Documentation](https://supabase.com/docs/guides/database/extensions/pgvector)
- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)

### Architecture References
- **Vector Databases**: Supabase pgvector for semantic search
- **Embeddings**: OpenAI text-embedding-3-small (1536 dimensions)  
- **MCP Protocol**: JSON-RPC 2.0 over stdio transport
- **API Design**: RESTful endpoints with comprehensive error handling

---

## 📄 License

[LICENSE_PLACEHOLDER - Add your license information]

---

## 📞 Contact & Support

### Project Information
- **Version**: 2.0.0 (Production Ready)
- **Last Updated**: December 2024
- **Maintainer**: [MAINTAINER_PLACEHOLDER]
- **Repository**: [REPOSITORY_URL_PLACEHOLDER]

### Getting Support
1. **Health Check**: Start with `curl http://localhost:8000/health`
2. **Documentation**: Review this comprehensive guide
3. **Logs**: Check application logs for specific errors
4. **Issues**: Create detailed issue reports with error messages and steps to reproduce

---

*This documentation reflects the current production-ready state of the Job Description Generator with comprehensive robustness improvements, security hardening, and enterprise-grade monitoring capabilities.*