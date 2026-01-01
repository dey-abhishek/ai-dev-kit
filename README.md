# Databricks AI Dev Kit

Build Databricks projects with AI coding assistants (Claude Code, Cursor, etc.) using MCP (Model Context Protocol).

## Overview

The AI Dev Kit provides everything you need to build on Databricks using AI assistants:

- **High-level Python functions** for Databricks operations
- **MCP server** that exposes these functions as tools for AI assistants
- **Skills** that teach AI assistants best practices and patterns

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Your Project                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────────┐        ┌─────────────────────────────────┐   │
│   │   databricks-skills/    │        │   .claude/mcp.json              │   │
│   │                         │        │                                 │   │
│   │   Knowledge & Patterns  │        │   MCP Server Config             │   │
│   │   • dabs-writer         │        │   → databricks-mcp-server       │   │
│   │   • sdp-writer          │        │                                 │   │
│   │   • synthetic-data-gen  │        └───────────────┬─────────────────┘   │
│   │   • databricks-sdk      │                        │                      │
│   └───────────┬─────────────┘                        │                      │
│               │                                      │                      │
│               │    SKILLS teach                      │    TOOLS execute     │
│               │    HOW to do things                  │    actions on        │
│               │                                      │    Databricks        │
│               ▼                                      ▼                      │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                          Claude Code                                 │  │
│   │                                                                      │  │
│   │   "Create a DAB with a DLT pipeline and deploy to dev/prod"         │  │
│   │                                                                      │  │
│   │   → Uses SKILLS to know the patterns and best practices             │  │
│   │   → Uses MCP TOOLS to execute SQL, create pipelines, etc.           │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

                                    │
                                    │ MCP Protocol
                                    ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│                        databricks-mcp-server                                 │
│                                                                              │
│   Exposes Python functions as MCP tools via stdio transport                 │
│   • execute_sql, execute_sql_multi                                          │
│   • get_table_details, list_warehouses                                      │
│   • run_python_file_on_databricks                                           │
│   • ka_create, mas_create, genie_create (Agent Bricks)                      │
│   • create_pipeline, start_pipeline (SDP)                                   │
│   • ... and more                                                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Python imports
                                    ▼

┌─────────────────────────────────────────────────────────────────────────────┐
│                         databricks-mcp-core                                  │
│                                                                              │
│   Pure Python library with high-level Databricks functions                  │
│                                                                              │
│   ├── sql/                    SQL execution, warehouses, table stats        │
│   ├── unity_catalog/          Catalogs, schemas, tables                     │
│   ├── compute/                Execution contexts, run code on clusters      │
│   ├── spark_declarative_pipelines/   DLT/SDP pipeline management            │
│   └── agent_bricks/           Genie, Knowledge Assistants, MAS              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ API calls
                                    ▼

                          ┌─────────────────────┐
                          │  Databricks         │
                          │  Workspace          │
                          └─────────────────────┘
```

## Quick Start

### Step 1: Clone and install

```bash
# Clone the repository
git clone https://github.com/databricks-solutions/ai-dev-kit.git
cd ai-dev-kit

# Install the core library
cd databricks-mcp-core
uv pip install -e .

# Install the MCP server
cd ../databricks-mcp-server
uv pip install -e .
```

### Step 2: Configure Databricks authentication

```bash
# Option 1: Environment variables
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="your-token"

# Option 2: Use a profile from ~/.databrickscfg
export DATABRICKS_CONFIG_PROFILE="your-profile"
```

### Step 3: Add MCP server to your project

In your project directory, create `.claude/mcp.json`:

```json
{
  "mcpServers": {
    "databricks": {
      "command": "uv",
      "args": ["run", "python", "-m", "databricks_mcp_server.server"],
      "cwd": "/path/to/ai-dev-kit/databricks-mcp-server",
      "defer_loading": true
    }
  }
}
```

**Replace `/path/to/ai-dev-kit`** with the actual path where you cloned the repo.

### Step 4: Install Databricks skills to your project (recommended)

Skills teach Claude best practices and patterns:

```bash
# In your project directory
curl -sSL https://raw.githubusercontent.com/databricks-solutions/ai-dev-kit/main/databricks-skills/install_skills.sh | bash
```

This installs to `.claude/skills/`:
- **dabs-writer**: Databricks Asset Bundles patterns
- **sdp-writer**: Spark Declarative Pipelines (DLT)
- **synthetic-data-generation**: Realistic test data generation
- **databricks-python-sdk**: SDK and API usage

### Step 5: Start Claude Code

```bash
cd /path/to/your/project
claude
```

Claude now has both **skills** (knowledge) and **MCP tools** (actions) for Databricks!

## Components

| Component | Description |
|-----------|-------------|
| [databricks-mcp-core](databricks-mcp-core/) | Pure Python library with Databricks functions |
| [databricks-mcp-server](databricks-mcp-server/) | MCP server wrapping core functions as tools |
| [databricks-skills](databricks-skills/) | Skills for Claude Code with patterns & examples |

## Using the Core Library Directly

The core library can be used without the MCP server:

```python
from databricks_mcp_core.sql import execute_sql, get_table_details, TableStatLevel

# Execute SQL
results = execute_sql("SELECT * FROM my_catalog.my_schema.customers LIMIT 10")

# Get table statistics
stats = get_table_details(
    catalog="my_catalog",
    schema="my_schema",
    table_names=["customers", "orders"],
    table_stat_level=TableStatLevel.DETAILED
)

# Run Python on a cluster
from databricks_mcp_core.compute import run_python_file_on_databricks

result = run_python_file_on_databricks(
    cluster_id="your-cluster-id",
    file_path="scripts/generate_data.py"
)
```

## Documentation

- [databricks-mcp-core README](databricks-mcp-core/README.md) - Core library details, all functions
- [databricks-mcp-server README](databricks-mcp-server/README.md) - Server configuration
- [databricks-skills README](databricks-skills/README.md) - Skills installation and usage

## Development

```bash
# Clone the repo
git clone https://github.com/databricks-solutions/ai-dev-kit.git
cd ai-dev-kit

# Install with uv
uv pip install -e databricks-mcp-core
uv pip install -e databricks-mcp-server

# Run tests
cd databricks-mcp-core
uv run pytest tests/integration/ -v
```

## License

© 2025 Databricks, Inc. All rights reserved. The source in this project is provided subject to the [Databricks License](https://databricks.com/db-license-source).

## Third-Party Package Licenses

| Package | License | Copyright |
|---------|---------|-----------|
| [databricks-sdk](https://github.com/databricks/databricks-sdk-py) | Apache License 2.0 | Copyright (c) Databricks, Inc. |
| [fastmcp](https://github.com/jlowin/fastmcp) | MIT License | Copyright (c) 2024 Jeremiah Lowin |
| [pydantic](https://github.com/pydantic/pydantic) | MIT License | Copyright (c) 2017 Samuel Colvin |
| [sqlglot](https://github.com/tobymao/sqlglot) | MIT License | Copyright (c) 2022 Toby Mao |
| [sqlfluff](https://github.com/sqlfluff/sqlfluff) | MIT License | Copyright (c) 2019 Alan Cruickshank |
