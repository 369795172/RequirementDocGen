# External Project References

This document contains detailed references to external GitHub projects that are frequently used during development. AI assistants can use this context to understand dependencies, APIs, and integration patterns without requiring repeated explanations.

## How to Use External Project Context

1. **GitHub MCP Server** (configured in `~/.cursor/mcp.json`): For real-time access to any GitHub repository you have access to. Use format: `owner/repo-name` when asking AI to read files.

2. **Git Submodules**: For projects that are frequently referenced, check the `external/` directory for local clones.

3. **Context7**: For well-known open-source libraries, AI can query documentation via the Context7 MCP server.

## Adding New External Project References

When adding a new external project, include:
- **Repo**: Full GitHub URL
- **Purpose**: What this project does and why it's referenced
- **Key Components**: Important files, modules, or APIs
- **Integration Notes**: How this project integrates with the current codebase
- **Common Patterns**: Code snippets or usage examples

---

## External Projects

### Example Entry

```markdown
### Project: some-api-service
- **Repo**: https://github.com/owner/some-api-service
- **Purpose**: Provides user authentication and authorization services
- **Key Endpoints**:
  - `POST /auth/login` - User login
  - `GET /auth/verify` - Verify JWT token
- **Integration Notes**: 
  - Uses JWT tokens with 24h expiration
  - Requires `X-API-Key` header for all requests
  - Base URL configured in `.env` as `API_SERVICE_URL`
- **Common Patterns**:
  ```python
  # Example usage
  headers = {"X-API-Key": os.getenv("API_SERVICE_KEY")}
  response = requests.post(f"{API_SERVICE_URL}/auth/login", headers=headers)
  ```
```

---

*Note: External projects can be accessed via GitHub MCP Server. Simply mention the repository (e.g., "owner/repo-name") when asking AI to read specific files or understand the codebase.*

