import chromadb
from sentence_transformers import SentenceTransformer

# --------------------------------------------------
# Load embedding model
# --------------------------------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# --------------------------------------------------
# Chroma client
# --------------------------------------------------
client = chromadb.Client()
collection = client.get_or_create_collection("schema")

# --------------------------------------------------
# RELATIONSHIP DEFINITIONS (ADD YOUR REAL ONES HERE)
# --------------------------------------------------
RELATIONSHIPS = [
    "jobs.job_id = job_run_timeline.job_id",
    "jobs.workspace_id = job_run_timeline.workspace_id",
    "jobs.account_id = job_run_timeline.account_id",

    "jobs.job_id = job_tasks.job_id",
    "job_tasks.job_id = job_task_run_timeline.job_id",

    "workspace.workspace_id = jobs.workspace_id",

    "warehouse_usage.warehouse_id = job_run_timeline.warehouse_id",
]

# --------------------------------------------------
# Index schema + relationships
# --------------------------------------------------
def index_schema(chunks):

    all_chunks = list(chunks)

    # Add relationships as extra knowledge
    for rel in RELATIONSHIPS:
        all_chunks.append(f"RELATIONSHIP: {rel}")

    for i, chunk in enumerate(all_chunks):

        emb = model.encode(chunk).tolist()

        collection.add(
            ids=[str(i)],
            embeddings=[emb],
            documents=[chunk]
        )


# --------------------------------------------------
# Retrieve schema context
# --------------------------------------------------
def retrieve_schema(question, k=5):

    emb = model.encode(question).tolist()

    results = collection.query(
        query_embeddings=[emb],
        n_results=k
    )

    docs = results["documents"][0]

    # Force relationship visibility
    relationship_context = "\n".join(
        [d for d in docs if "RELATIONSHIP:" in d]
    )

    schema_context = "\n".join(docs)

    final_context = f"""
SCHEMA CONTEXT:
{schema_context}

KNOWN TABLE RELATIONSHIPS:
{relationship_context}

IMPORTANT:
- ONLY use relationships listed above.
- NEVER invent join columns.
"""

    return final_context
