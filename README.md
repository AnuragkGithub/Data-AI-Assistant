# Data AI Assistant

Enterprise-grade AI-Powered Data Analytics Assistant built using **Python, Streamlit, LLM Routing, SQL Intelligence, Schema-Aware Querying, and Secure Analytics Workflows**.

The platform enables intelligent analytics over structured datasets using natural language questions, automated query generation, schema relationship mapping, and AI-driven analytical workflows.

---

# Features

- AI-Powered Natural Language Analytics
- Intelligent Query Routing
- LLM-Based Data Assistant
- Dynamic SQL Query Generation
- Schema Relationship Intelligence
- Secure SQL Validation Layer
- Streamlit Interactive Dashboard
- Metrics & Analytical Insights
- RAG-Style Schema Understanding
- Modular AI Analytics Architecture

---

# Core Capabilities

## AI Analytics Assistant

- Natural language querying
- Intelligent analytics workflows
- Context-aware query handling
- AI-driven data exploration

## Query Intelligence

- SQL query generation
- Query validation layer
- Intent routing system
- Relationship-aware querying

## Schema Intelligence

- Automated schema understanding
- Relationship graph building
- Metadata-aware analytics
- RAG-inspired schema retrieval

## Analytics & Metrics

- Runtime metrics
- Usage analytics
- Trend analysis
- Aggregation workflows

---

# Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core Development |
| Streamlit | Frontend Dashboard |
| SQLite | Data Storage |
| Pandas | Data Processing |
| SQLAlchemy | Database Layer |
| LLM Routing | AI Query Intelligence |
| JSON/YAML | Metadata Handling |
| RAG Concepts | Schema Retrieval |
| Plotly | Visualization |

---

# Project Structure

```bash
DATA_AI_ASSISTANT/
│
├── .streamlit/
│   └── config.toml
│
├── app/
│   └── main.py
│
├── core/
│   ├── data_loader.py
│   ├── intent_router.py
│   ├── llm_agent.py
│   ├── metrics.py
│   ├── query_engine.py
│   ├── relationship_builder.py
│   ├── schema_builder.py
│   ├── schema_rag.py
│   └── sql_guard.py
│
├── data/
│
├── utils/
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

# System Architecture

```text
User Question
      ↓
Intent Router
      ↓
LLM Agent
      ↓
Schema RAG Engine
      ↓
Relationship Builder
      ↓
SQL Query Engine
      ↓
SQL Guard Validation
      ↓
Analytics Output
      ↓
Streamlit Dashboard
```

---

# Features Breakdown

## Intent Router

Routes user questions into appropriate analytical workflows.

## LLM Agent

Handles AI-driven query understanding and contextual analytics.

## Schema RAG

Retrieves schema intelligence dynamically for better query generation.

## SQL Guard

Validates generated SQL queries for secure execution.

## Relationship Builder

Builds entity relationships between datasets and schemas.

---

# Installation

## 1. Clone Repository

```bash
git clone https://github.com/AnuragkGithub/Data-AI-Assistant.git

cd Data-AI-Assistant
```

---

## 2. Create Virtual Environment

### Mac/Linux

```bash
python3 -m venv .venv

source .venv/bin/activate
```

### Windows

```bash
python -m venv .venv

.venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Running the Application

```bash
streamlit run app/main.py
```

Application runs at:

```text
http://localhost:8501
```

---

# Example User Queries

```text
Show top performing datasets

Analyze runtime metrics

Find failed data pipelines

Compare workspace performance

Generate schema insights

Show creator-wise analytics
```

---

# Sample Intent Routing

```python
def route_intent(question):

    if "runtime" in question:
        return "RUNTIME_ANALYSIS"

    elif "failure" in question:
        return "FAILURE_ANALYSIS"

    return "GENERAL_ANALYTICS"
```

---

# SQL Guard Example

```python
def validate_sql(query):

    blocked_keywords = ["DROP", "DELETE"]

    for keyword in blocked_keywords:
        if keyword in query.upper():
            return False

    return True
```

---

# Schema RAG Workflow

The project includes a lightweight RAG-style architecture for:

- schema retrieval
- relationship discovery
- metadata-aware analytics
- contextual query generation

---

# Screenshots

## Streamlit Dashboard

_Add dashboard screenshot here_

## Analytics Output

_Add analytics screenshot here_

---

# Future Enhancements

- OpenAI / Groq Integration
- Vector Database Support
- Real-Time Analytics Pipelines
- Autonomous AI Agents
- Multi-Database Connectivity
- Cloud Deployment
- Authentication & RBAC
- Conversational Analytics
- Advanced RAG Pipelines

---

# Author

## Anurag Karmakar

- Python Developer
- AI & Analytics Enthusiast
- Data Engineering Explorer
- Streamlit + AI Systems Developer

---

# License

MIT License