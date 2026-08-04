# Enterprise AI Analyst

Self-healing Text-to-SQL data analyst automation for enterprise analytics workflows.

Enterprise AI Analyst is a graph-aware, stateful Text-to-SQL platform that translates natural-language questions into validated SQL, executes them against relational data, and attempts to recover from common failures through structured repair loops. The system combines schema graph modeling, relationship inference, hybrid retrieval, LangGraph orchestration, and AST-driven validation to make SQL generation more reliable, explainable, and resilient.

## System Architecture Overview

The platform is organized as a staged pipeline:

1. Schema and graph understanding
   - The ingestion and graph layers build and enrich a schema-driven knowledge graph from database metadata.
   - A custom SchemaGraph models tables, foreign-key relationships, logical joins, and table roles such as fact, dimension, and lookup tables.

2. Relationship inference
   - The relationship subsystem applies rule-based and scoring-based heuristics to infer likely joins between tables that may not be explicitly connected through foreign keys.

3. Retrieval and ranking
   - The retrieval subsystem combines semantic retrieval, value-based retrieval, graph expansion, and ranking to identify the most relevant schema context for a question.

4. LangGraph orchestration
   - The orchestration layer uses a state-driven workflow to coordinate retrieval, schema context assembly, candidate SQL generation, validation, repair, and execution.

5. SQL generation, validation, and self-healing repair
   - SQL candidates are validated with AST-based rules covering aliases, joins, aggregates, table and column existence, dangerous statements, and other structural concerns.
   - When validation fails, the repair pipeline iterates and attempts to produce a corrected candidate.

This architecture enables the system to move from raw database understanding to executable SQL through a controlled, inspectable workflow.

## Project Directory Structure

src/
agent/ # Analyst agent orchestration and shared state
config/ # Configuration, environment settings, and path helpers
embedding/ # Embedding service integration
evaluation/ # Benchmarking, replay, and evaluation utilities
graph/ # Schema graph model, graph loaders, and export logic
ingestion/ # Schema extraction, enrichment, chunking, and embedding
llm/ # LLM client integrations
orchestration/
langgraph/ # State graph, nodes, and routers
pipeline/ # Retrieval and query pipeline orchestration
planner/ # Query planning models and planning logic
relationship/ # Relationship inference rules and scoring
retrieval/ # Semantic/value retrieval, ranking, and graph expansion
sql/ # SQL generation, validation, repair, and execution
utils/ # Shared helper utilities

data/ # Schema files, graph files, evaluation data, and test fixtures
scripts/ # Database setup and initialization scripts
docker/ # Docker Compose configuration for Postgres and Qdrant
mimic-code/ # MIMIC-related assets and references
tests/ # Project tests

## Core Features Summary

### Database Graph Modeling

- Builds a schema-aware graph of tables and relationships.
- Supports explicit foreign-key edges and inferred logical relationships.
- Distinguishes between lookup, dimension, and fact-like tables to improve downstream planning and retrieval.

### Hybrid Retrieval

- Combines semantic retrieval with value-based retrieval.
- Expands retrieved schema context through graph traversal.
- Ranks candidate tables and schema context based on query relevance.

### LangGraph Orchestration

- Implements a stateful workflow with explicit nodes for retrieval, schema context construction, candidate generation, validation, repair, and execution.
- Uses conditional routing to decide whether to continue to execution, repair the candidate, or retrieve more schema context.

### AST Validation and Self-Healing

- Uses SQLGlot-based AST inspection to validate generated SQL.
- Checks for unknown tables, unknown columns, invalid joins, alias issues, grouping problems, dangerous SQL, and parse errors.
- Supports an automated repair loop so invalid SQL can be iteratively improved before execution.

## Getting Started & Prerequisites

### Prerequisites

- Python 3.13 or newer
- Docker Desktop for local infrastructure services
- Access to LLM-compatible endpoints configured in the environment
- A vector database-backed retrieval environment for semantic and value indexing

### Dependency Management

The project dependency metadata is declared in pyproject.toml. A standard local setup is:

python -m venv .venv
source .venv/bin/activate
pip install -e .

If you use uv, the equivalent workflow is:

uv sync

or, for an editable install:

uv pip install -e .

## Environment Setup & Database Scripts

The repository includes shell scripts under scripts/ to initialize the local database environment.

### Docker Services

The Docker configuration in docker/docker-compose.yml starts:

- PostgreSQL on port 5432
- Qdrant on ports 6333 and 6334

Start the containers with:

docker compose -f docker/docker-compose.yml up -d

### Database Initialization Scripts

The scripts directory contains the main setup workflow:

- scripts/setup_database.sh
  - Runs the full setup sequence
- scripts/create_schema.sh
  - Creates database schema objects
- scripts/load_data.sh
  - Loads the dataset content
- scripts/add_constraints.sh
  - Applies database constraints
- scripts/create_indexes.sh
  - Creates indexes for performance

Run the full setup flow with:

bash scripts/setup_database.sh

These scripts prepare the local relational database so the pipeline can run against the available schema and data assets.

## Usage

### Run the project entry point

The current entry point in src/main.py constructs the LangGraph workflow and runs it against a sample question:

python src/main.py

This entry point invokes the analyst workflow, which performs retrieval, schema context assembly, SQL generation, validation, repair, and execution as part of the pipeline.

### Programmatic Usage

You can also instantiate the analyst agent directly and run your own questions through the same pipeline:

from src.agent.analyst import AnalystAgent
from src.orchestration.langgraph.graph import build_graph

graph = build_graph()
agent = AnalystAgent()

result = graph.invoke({
"question": "Find the maximum lab value for creatinine for ICU admissions"
})

print(result["run"].generated_sql)
print(result["run"].error)

## Notes

- The repository includes schema and graph assets under data/ as well as MIMIC-related data references under data/mimic/ and mimic-code/.
- The project is intentionally designed as a research and engineering platform for enterprise-grade, self-healing analytics automation rather than as a simple one-shot SQL generator.
