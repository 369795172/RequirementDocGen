# External Projects

This directory contains Git submodules for external GitHub projects that are frequently referenced during development.

## Purpose

External projects added as submodules here will be automatically indexed by Cursor's `@codebase` feature, allowing AI assistants to search and understand the codebase without requiring network access.

## When to Use Submodules

Consider adding a project as a submodule if:
- You reference it **more than 3 times per week**
- You need to **search through implementation details** (not just API docs)
- The project is **actively maintained** and you want to track updates

For projects where you only need API documentation or occasional reference, use the **GitHub MCP Server** instead (configured in `~/.cursor/mcp.json`).

## Adding a Submodule

```bash
# From project root
git submodule add https://github.com/owner/repo.git external/repo-name

# Initialize and update (for new clones)
git submodule update --init --recursive
```

## Updating Submodules

```bash
# Update all submodules to latest from their remotes
git submodule update --remote --merge

# Or update a specific submodule
cd external/repo-name
git pull origin main
cd ../..
git add external/repo-name
git commit -m "Update external/repo-name submodule"
```

## For Large Projects

If a project is very large (>500MB), consider using sparse checkout:

```bash
git submodule add https://github.com/owner/repo.git external/repo-name
cd external/repo-name
git sparse-checkout init --cone
git sparse-checkout set src/ docs/  # Only checkout specific directories
```

## Current Submodules

*None yet. Add external projects here as needed.*

