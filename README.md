# Enterprise AI Analyst

Self-healing, graph-aware **Text-to-SQL data analyst** for enterprise analytics workflows.

Enterprise AI Analyst is a stateful, agentic Text-to-SQL platform that translates natural-language questions into validated SQL, executes them against relational data, and attempts to recover from common failures through structured repair loops. The system combines schema graph modeling, relationship inference, hybrid retrieval, conversational question rewriting, LangGraph orchestration, AST-driven validation, persistent conversations, and MCP-based access.

The system is designed to go beyond one-shot Text-to-SQL by treating database querying as a multi-stage, inspectable, and recoverable agent workflow.

---

## Quick Start

### Prerequisites

- **Python 3.13+**
- **Docker Desktop** (for PostgreSQL and Qdrant)
- **uv** package manager (`pip install uv`)
- **PostgreSQL connection string** (or use Docker Compose)
- **LLM API key** (Anthropic, OpenRouter, or Gemini)

### 1. Clone and Install

```bash
git clone https://github.com/adeeb018/enterprise-ai-analyst.git
cd enterprise-ai-analyst

# Install dependencies
uv sync
```

### 2. Start Infrastructure (Docker)

```bash
# Start PostgreSQL and Qdrant containers
docker compose -f docker/docker-compose.yml up -d

# Verify services are running
docker ps
```

Expected output:

- PostgreSQL listening on `localhost:5432`
- Qdrant listening on `localhost:6333`

### 3. Configure Environment

Create a `.env` file in the project root:

```bash
touch .env
```

Add the following variables (see **Environment Variables** section below for details):

```env
# Database
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/hospital

# Qdrant Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=hospital_schema
QDRANT_VALUE_COLLECTION=value_embeddings
VECTOR_DIMENSION=384

# Embeddings
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5

# LLM (Anthropic via OpenRouter)
LLM_API_BASE=https://openrouter.ai/api/v1
LLM_API_KEY=sk_...
LLM_MODEL=anthropic/claude-3.5-sonnet

# Optional: Gemini LLM (for repair/fallback)
GEMINI_LLM_API_BASE=https://generativelanguage.googleapis.com/v1beta/openai/
GEMINI_LLM_API_KEY=...
GEMINI_LLM_MODEL=gemini-2.0-flash

# MCP Server
MCP_ALLOWED_HOST=127.0.0.1
PORT=8001
```

**⚠️ Never commit `.env` to git.** It's in `.gitignore` by default.

### 4. Initialize Database

```bash
# Run the full database setup (creates schema, loads data, adds indexes)
bash scripts/setup_database.sh

# Or run setup steps individually:
# bash scripts/create_schema.sh
# bash scripts/load_data.sh
# bash scripts/create_indexes.sh
# bash scripts/add_constraints.sh
```

This script:

- Creates the hospital schema in PostgreSQL
- Loads MIMIC-IV clinical data
- Builds indexes for performance
- Applies foreign-key and data constraints

### 5. Start the MCP Server

```bash
# Start the FastAPI + FastMCP server
uv run python server.py
```

Expected output:

```
INFO:     Uvicorn running on http://127.0.0.1:8001
```

The MCP endpoint is available at: `http://127.0.0.1:8001/mcp/`

### 6. Test with Python Client (Optional)

In another terminal:

```bash
# Interactive MCP client for testing
uv run python src/mcp_client.py
```

You'll be prompted to enter natural-language questions. The analyst will:

1. Plan the query
2. Retrieve relevant schema
3. Generate SQL
4. Validate and repair if needed
5. Execute and return results

---

## Environment Variables

### Database Configuration

| Variable       | Required | Description                  | Example                                                          |
| -------------- | -------- | ---------------------------- | ---------------------------------------------------------------- |
| `DATABASE_URL` | ✅       | PostgreSQL connection string | `postgresql+psycopg://postgres:postgres@localhost:5432/hospital` |

### Qdrant Vector Database

| Variable                  | Required | Default | Description                        |
| ------------------------- | -------- | ------- | ---------------------------------- | ------------------ |
| `QDRANT_HOST`             | ✅       | —       | Qdrant server hostname             | `localhost`        |
| `QDRANT_PORT`             | ✅       | `6333`  | Qdrant API port                    | `6333`             |
| `QDRANT_COLLECTION`       | ✅       | —       | Schema embeddings collection       | `hospital_schema`  |
| `QDRANT_VALUE_COLLECTION` | ✅       | —       | Value/entity embeddings collection | `value_embeddings` |
| `VECTOR_DIMENSION`        | ✅       | `384`   | Embedding vector dimension         | `384`              |

### Embeddings

| Variable          | Required | Default                  | Description                 |
| ----------------- | -------- | ------------------------ | --------------------------- | ------------------------ |
| `EMBEDDING_MODEL` | ✅       | `BAAI/bge-small-en-v1.5` | HuggingFace embedding model | `BAAI/bge-small-en-v1.5` |

### LLM Configuration

The system supports OpenAI-compatible endpoints (OpenRouter, Azure, local Ollama, etc.).

| Variable       | Required | Description           | Example                        |
| -------------- | -------- | --------------------- | ------------------------------ |
| `LLM_API_BASE` | ✅       | LLM provider endpoint | `https://openrouter.ai/api/v1` |
| `LLM_API_KEY`  | ✅       | LLM provider API key  | `sk_...`                       |
| `LLM_MODEL`    | ✅       | Model identifier      | `anthropic/claude-3.5-sonnet`  |

### Gemini LLM (Optional)

Use Gemini for query repair or as fallback LLM:

| Variable              | Required | Description                                                |
| --------------------- | -------- | ---------------------------------------------------------- |
| `GEMINI_LLM_API_BASE` | ❌       | `https://generativelanguage.googleapis.com/v1beta/openai/` |
| `GEMINI_LLM_API_KEY`  | ❌       | Google API key                                             |
| `GEMINI_LLM_MODEL`    | ❌       | `gemini-2.0-flash`                                         |

### MCP Server Configuration

| Variable           | Required | Default     | Description                 |
| ------------------ | -------- | ----------- | --------------------------- | ----------- |
| `MCP_ALLOWED_HOST` | ❌       | `127.0.0.1` | Host for MCP server binding | `127.0.0.1` |
| `PORT`             | ❌       | `8001`      | Server port                 | `8001`      |
| `MCP_API_KEY`      | ❌       | —           | Optional auth token for MCP | —           |

---

## Running Locally

### Option A: Python Entry Point (Direct Execution)

Run a single query through the analyst workflow:

```bash
uv run python src/main.py
```

This uses the question configured in `src/main.py` and prints:

- Generated SQL
- Execution results
- Any errors

### Option B: FastAPI + FastMCP Server

Run the full MCP server with interactive conversation support:

```bash
uv run python server.py
```

Then connect via:

- Python MCP client: `uv run python src/mcp_client.py`
- Claude Desktop (configure in `claude_desktop_config.json`)
- Any MCP-compatible client

### Option C: Programmatic Usage

```python
from src.agent.analyst import AnalystAgent
from src.orchestration.langgraph.graph import build_graph

# Build the analyst workflow
graph = build_graph()
agent = AnalystAgent()

# Run a question
result = graph.invoke({
    "question": "How many patients were admitted to the ICU?",
    "conversation_id": None,  # Optional: provide existing conversation ID
})

# Access results
print(f"Generated SQL: {result['run'].generated_sql}")
print(f"Answer: {result['run'].answer}")
print(f"Error (if any): {result['run'].error}")
```

---

## Project Structure

```text
src/
├── agent/                      # Analyst orchestration and state management
├── config/                     # Configuration and environment settings
│   ├── settings.py            # Pydantic Settings (env var parsing)
│   ├── database.py            # Database connection setup
│   ├── qdrant.py              # Qdrant client initialization
│   └── paths.py               # File path helpers
├── conversation/               # Persistent conversation management
├── embedding/                  # Embedding service integration
├── evaluation/                 # Benchmarking and evaluation utilities
├── graph/                      # Schema graph model and loaders
├── ingestion/                  # Schema extraction and enrichment
├── llm/                        # LLM client integrations (Anthropic, Gemini)
├── mcp_client.py              # Python MCP client for local testing
├── orchestration/
│   └── langgraph/             # LangGraph state graph and nodes
├── pipeline/                   # Retrieval and query pipeline
├── planner/                    # Query planning models
├── relationship/               # Relationship inference rules
├── retrieval/                  # Semantic/value retrieval and ranking
├── server/                     # FastAPI + FastMCP application
│   ├── app.py                 # FastAPI app and MCP endpoints
│   ├── auth.py                # Authentication helpers
│   └── server.py              # Uvicorn runner
├── sql/                        # SQL generation, validation, repair, execution
└── utils/                      # Shared utilities

data/
├── graph.json                  # Schema relationship graph
└── schema/                     # Database schema artifacts

scripts/
├── setup_database.sh          # Full setup orchestration
├── create_schema.sh           # Create database tables
├── load_data.sh               # Load MIMIC-IV data
├── create_indexes.sh          # Create performance indexes
└── add_constraints.sh         # Add FK and data constraints

docker/
└── docker-compose.yml         # PostgreSQL + Qdrant services

tests/                         # Unit and integration tests
Dockerfile                     # Container definition
pyproject.toml                 # Project metadata and dependencies
uv.lock                        # Locked dependency versions
server.py                      # Top-level MCP server entry point
main.py                        # Top-level analyst workflow entry point
README.md                      # This file
.env                          # Local environment (git-ignored)
```

---

## Architecture Overview

The analyst workflow operates as a multi-stage pipeline:

```
User Question
    ↓
Conversation Context Resolution
    ↓
Planning & Intent Analysis
    ↓
Hybrid Retrieval
    ├─ Semantic schema retrieval (tables/columns)
    ├─ Value/entity retrieval (lookup entities)
    └─ Graph expansion (join paths)
    ↓
Schema Context Ranking & Merging
    ↓
SQL Generation (via LLM)
    ↓
SQLGlot Validation
    ├─ Check: unknown tables/columns
    ├─ Check: invalid joins, aliases, groups
    └─ Check: dangerous SQL
    ↓
Validation Pass?
    ├─ YES → Execute & Answer Generation
    └─ NO  → Failure Analysis → Retrieve More Schema → Repair SQL (loop)
    ↓
Natural Language Answer
    ↓
Conversation Persistence
```

### Core Subsystems

**1. Schema Graph Modeling**

- Builds a relationship graph from database metadata
- Supports explicit FKs and inferred logical joins
- Models table roles (fact, dimension, lookup)

**2. Relationship Inference**

- Rule-based scoring: column names, PKs, lookups, shared identifiers
- Produces evidence-backed relationship candidates

**3. Hybrid Retrieval**

- Semantic retrieval: finds relevant tables/columns
- Value retrieval: resolves entities to database codes
- Graph expansion: discovers related tables
- Ranking: filters to most relevant schema context

**4. Conversational Question Rewriting**

- Maintains multi-turn conversation history
- Resolves pronouns and references ("them", "those patients")
- Converts contextual follow-ups to standalone questions

**5. LangGraph Orchestration**

- Stateful workflow with explicit nodes
- Conditional routing (execute vs. repair vs. retrieve more)
- Inspectable intermediate results

**6. AST Validation & Self-Healing**

- SQLGlot-based validation
- Detects structural errors
- Automated repair loop retrieves more schema when needed

---

## Environment Setup Details

### Using Docker Compose (Recommended for Local Development)

PostgreSQL and Qdrant will run as containers. The application runs on your host machine.

```bash
# Start containers
docker compose -f docker/docker-compose.yml up -d

# Check status
docker ps

# View logs
docker compose -f docker/docker-compose.yml logs -f postgres
docker compose -f docker/docker-compose.yml logs -f qdrant
```

### Using External/Cloud Databases

To use cloud-hosted Qdrant and PostgreSQL:

```env
# PostgreSQL on Neon
DATABASE_URL=postgresql+psycopg://user:password@ep-xxxx.neon.tech:5432/hospital

# Qdrant Cloud
QDRANT_HOST=your-qdrant-instance.qdrant.io
QDRANT_PORT=6333
```

---

## Key Workflows

### Query Execution Flow

```bash
# Start the server
uv run python server.py

# In another terminal, use the client
uv run python src/mcp_client.py

# Example interaction:
# > How many patients were admitted?
# Generated SQL: SELECT COUNT(*) FROM admissions;
# Answer: There were 550 patients admitted.
```

### Conversation Management

```python
from src.conversation.manager import ConversationManager

manager = ConversationManager()

# Create conversation
conv = manager.create(title="ICU Analysis")
conversation_id = conv.id

# Ask question in context
result = graph.invoke({
    "question": "How many of them were admitted to the ICU?",
    "conversation_id": conversation_id,
})

# Retrieve full history
history = manager.get(conversation_id)
print(history.turns)  # List of (question, answer, sql) tuples
```

### Evaluation & Debugging

```bash
# Run benchmarks
uv run python -m src.evaluation.runner --benchmark dataset.json

# Replay a failed run
uv run python -m src.evaluation.replayer --run failed_run.json
```

---

## Troubleshooting

### "Connection refused" (PostgreSQL)

```bash
# Check if Docker container is running
docker ps | grep postgres

# If not running, start it
docker compose -f docker/docker-compose.yml up -d postgres

# Verify connection
psql postgresql://postgres:postgres@localhost:5432/hospital -c "SELECT 1;"
```

### "Connection refused" (Qdrant)

```bash
# Check if Qdrant is running
docker ps | grep qdrant

# If not, start it
docker compose -f docker/docker-compose.yml up -d qdrant

# Check Qdrant health
curl http://localhost:6333/health
```

### "No schema context retrieved"

- Verify embeddings are loaded in Qdrant
- Check that `QDRANT_COLLECTION` and `QDRANT_VALUE_COLLECTION` exist
- Run `scripts/load_data.sh` to ensure data is populated

### "LLM API error"

- Verify `LLM_API_KEY` and `LLM_API_BASE` are correct
- Check your API quota/rate limits
- Try an alternative LLM model

### "Invalid SQL generated"

- Check the validation error in the output
- The system should attempt repair automatically
- If repair fails, check schema retrieval with: `uv run python -m src.evaluation.replayer --stage retrieval`

---

## Technology Stack

| Component           | Technology                          |
| ------------------- | ----------------------------------- |
| Language            | Python 3.13                         |
| Agent Orchestration | LangGraph                           |
| API Framework       | FastAPI                             |
| MCP Protocol        | FastMCP + Streamable HTTP           |
| Database            | PostgreSQL (via Psycopg/SQLAlchemy) |
| Vector DB           | Qdrant                              |
| Embeddings          | BAAI/bge-small-en-v1.5              |
| LLM Providers       | Anthropic, Gemini, OpenRouter       |
| SQL Validation      | SQLGlot                             |
| Package Management  | uv                                  |
| Containerization    | Docker                              |
| Dataset             | MIMIC-IV Clinical Database Demo     |

---

## Development Philosophy

The project follows these principles:

1. **Retrieval before generation** — Give LLMs focused schema context, not the full DB
2. **Multiple retrieval signals** — Combine semantic, value, and graph-based retrieval
3. **Validate generated SQL** — Never trust LLM output without checking
4. **Recover instead of failing** — Re-retrieve more schema and repair queries
5. **Separate and inspect stages** — Keep planning, retrieval, generation, validation independent
6. **Persist complete runs** — Store enough info to reproduce failures
7. **Preserve conversation context** — Resolve follow-ups from previous turns
8. **Expose via MCP** — Make the agent accessible to external clients

---

## Security

**Never commit these to git:**

```
.env
API keys
Database passwords
Qdrant credentials
MCP authentication tokens
```

**Best practices:**

- Store secrets in environment variables
- Use `.gitignore` (already configured)
- For production, use platform secret management (Render, AWS Secrets, etc.)
- Consider OAuth for public MCP endpoints

---

## Current Status

### Implemented ✅

- [x] Natural-language database querying
- [x] LangGraph orchestration
- [x] Conversational question rewriting
- [x] Semantic schema retrieval
- [x] Value/entity retrieval
- [x] Schema graph construction
- [x] Logical relationship inference
- [x] Graph expansion
- [x] SQL generation (Anthropic, Gemini)
- [x] SQLGlot validation
- [x] Automated SQL repair
- [x] Retrieve-more-schema recovery
- [x] SQL execution
- [x] Natural-language answer generation
- [x] Persistent conversation management
- [x] MCP server (FastAPI + FastMCP)
- [x] Evaluation framework with replay
- [x] Docker containerization
- [x] Claude Desktop integration

### Evaluation Results

On a validation set of 20 unseen queries:

- **90% first-pass SQL execution success**
- **100% success after automated repair**
- **10/10 on schema relationship inference**

(Metrics based on MIMIC-IV demo dataset — vary with real datasets)

---

## Future Improvements

- [ ] OAuth authentication for public MCP
- [ ] Enhanced production observability
- [ ] Larger benchmark datasets
- [ ] Semantic SQL equivalence evaluation
- [ ] Latency optimization and caching
- [ ] Cost/token monitoring
- [ ] Rate limiting
- [ ] CI/CD regression testing

---

## License & Attribution

This repository uses the **MIMIC-IV Clinical Database Demo** as the demonstration dataset.

When using MIMIC-derived data, follow the applicable MIMIC data-use and access requirements.

---

## Questions or Contributions?

For issues, feature requests, or discussions:

- **GitHub Issues:** https://github.com/adeeb018/enterprise-ai-analyst/issues
- **GitHub Discussions:** https://github.com/adeeb018/enterprise-ai-analyst/discussions

---

**Last updated:** August 2026
