import ollama

MODEL_NAME = "qwen2.5-coder:7b"

   # change if using another model

SYSTEM_PROMPT = """
You are a DuckDB SQL expert.

Rules:
- Use DuckDB syntax ONLY.
- For last 7 days use: current_date - INTERVAL 7 DAY
- result_state values are UPPERCASE.
- If subtracting timestamps, cast them using:
  CAST(column AS TIMESTAMP)
- ONLY use column names EXACTLY as listed.
- NEVER invent columns.
- NEVER add suffixes like _ts unless present.
- If unsure, use existing time columns from schema.
- NEVER use alias names in HAVING or subqueries unless they are explicitly created in a CTE or SELECT statement.

Return ONLY valid DuckDB SQL.
If a time column exists, prefer using *_ts version.
Example:
period_end_time_ts
You MUST use ONLY the provided tables.
Do NOT use any other table.
IMPORTANT:
There is NO duration_minutes column.
If duration is needed, ALWAYS calculate:

EXTRACT(EPOCH FROM (
    CAST(end_time AS TIMESTAMP) -
    CAST(start_time AS TIMESTAMP)
))/60 AS duration_minutes
Rules:
- ALWAYS prefix columns with table name
- Example: jobs.job_id
- NEVER use plain job_id

"""


def _build_prompt(user_question, schema_summary):
    
    return f"""
You are a DuckDB SQL expert.

STRICT RULES:
- Use ONLY columns listed in schema.
- NEVER invent columns.
- If a column does not exist, DO NOT use it.
- If unsure, calculate using existing columns.
- Do NOT use columns like:
  status, bottleneck, duration_minutes,
  avg_execution_duration unless explicitly present.

Schema:
{schema_summary}

User Question:
{user_question}

Return ONLY SQL.
"""
def generate_sql(user_question, schema_summary):
    try:
        prompt = _build_prompt(user_question, schema_summary)

        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )

        sql = response["message"]["content"].strip()
        sql = sql.replace("```sql", "").replace("```", "").strip()

        return sql, None

    except Exception as e:
        return None, str(e)
