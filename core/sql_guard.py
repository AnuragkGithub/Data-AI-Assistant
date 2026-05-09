import re
import difflib

# =====================================================
# GENERAL SQL FIXES (DuckDB compatibility)
# =====================================================
def fix_sql(sql: str) -> str:
    """
    Basic SQL normalization for DuckDB.
    """

    # DATE_ADD -> DuckDB interval syntax
    sql = re.sub(
        r"DATE_ADD\('day',\s*-(\d+),\s*CURRENT_DATE\)",
        r"CURRENT_DATE - INTERVAL '\1 DAY'",
        sql,
        flags=re.IGNORECASE
    )

    sql = re.sub(
        r"dateadd\(day,\s*-(\d+),\s*current_date\)",
        r"CURRENT_DATE - INTERVAL '\1 DAY'",
        sql,
        flags=re.IGNORECASE
    )

    # normalize failure states
    sql = re.sub(
        r"result_state\s*=\s*'(failure|fail)'",
        "result_state = 'FAILED'",
        sql,
        flags=re.IGNORECASE
    )

    return sql


# =====================================================
# INTERVAL FIXER (DuckDB safe)
# =====================================================
def fix_interval_sum(sql: str) -> str:
    """
    Convert interval arithmetic to numeric minutes.
    """

    # SUM(end - start)
    sql = re.sub(
        r"SUM\s*\(\s*([a-zA-Z0-9_\.]+)\s*-\s*([a-zA-Z0-9_\.]+)\s*\)",
        r"SUM(EXTRACT(EPOCH FROM (\1 - \2)))/60",
        sql,
        flags=re.IGNORECASE
    )

    # SUM(CAST(...) - CAST(...))
    sql = re.sub(
        r"SUM\s*\(\s*CAST\((.*?)AS\s+TIMESTAMP\)\s*-\s*CAST\((.*?)AS\s+TIMESTAMP\)\s*\)",
        r"SUM(EXTRACT(EPOCH FROM (CAST(\1 AS TIMESTAMP) - CAST(\2 AS TIMESTAMP))))/60",
        sql,
        flags=re.IGNORECASE
    )

    # CAST((end-start) AS DOUBLE)
    sql = re.sub(
        r"CAST\s*\(\s*\((.*?)\s*-\s*(.*?)\)\s*AS\s+DOUBLE\s*\)",
        r"EXTRACT(EPOCH FROM (\1 - \2))",
        sql,
        flags=re.IGNORECASE
    )

    # (CAST(end)-CAST(start))/60
    sql = re.sub(
        r"\(\s*CAST\((.*?)AS\s+TIMESTAMP\)\s*-\s*CAST\((.*?)AS\s+TIMESTAMP\)\s*\)\s*/\s*60",
        r"EXTRACT(EPOCH FROM (CAST(\1 AS TIMESTAMP) - CAST(\2 AS TIMESTAMP)))/60",
        sql,
        flags=re.IGNORECASE
    )

    return sql


# =====================================================
# TABLE NAME FIXER
# =====================================================
def fix_table_names(sql: str, tables: dict) -> str:
    """
    Auto-correct slightly wrong table names.
    """

    table_names = list(tables.keys())

    matches = re.findall(
        r"(FROM|JOIN)\s+([a-zA-Z0-9_]+)",
        sql,
        re.IGNORECASE
    )

    for _, used_table in matches:

        if used_table not in table_names:

            closest = difflib.get_close_matches(
                used_table,
                table_names,
                n=1,
                cutoff=0.5
            )

            if closest:
                sql = re.sub(
                    rf"\b{used_table}\b",
                    closest[0],
                    sql
                )

    return sql


# =====================================================
# MISSING ALIAS FIX
# =====================================================
def fix_missing_aliases(sql: str) -> str:
    """
    Fix common alias missing issues.
    """

    if "j." in sql and " jobs j" not in sql:
        sql = sql.replace("FROM jobs", "FROM jobs j")

    if "jrt." in sql and " job_run_timeline jrt" not in sql:
        sql = sql.replace(
            "FROM job_run_timeline",
            "FROM job_run_timeline jrt"
        )

    if "jt." in sql and " job_tasks jt" not in sql:
        sql = sql.replace(
            "FROM job_tasks",
            "FROM job_tasks jt"
        )

    return sql


# =====================================================
# DISTINCT ON FIX (Postgres -> DuckDB)
# =====================================================
def fix_distinct_on(sql: str) -> str:
    """
    Convert DISTINCT ON to DuckDB-compatible DISTINCT.
    """

    sql = re.sub(
        r"DISTINCT\s+ON\s*\(\s*([^)]+)\s*\)",
        r"DISTINCT \1",
        sql,
        flags=re.IGNORECASE
    )

    return sql


# =====================================================
# DURATION COLUMN FIX
# =====================================================
def fix_duration_column(sql: str) -> str:
    """
    Replace hallucinated duration_minutes column.
    """

    sql = sql.replace(
        "duration_minutes",
        "EXTRACT(EPOCH FROM (CAST(end_time AS TIMESTAMP) - CAST(start_time AS TIMESTAMP)))/60"
    )

    return sql


# =====================================================
# INVALID SUM FIX (dataset-specific)
# =====================================================
def fix_invalid_sum(sql: str) -> str:
    """
    Prevent SUM on non-numeric compute_ids.
    """

    return sql.replace(
        "SUM(jrt.compute_ids)",
        "COUNT(jrt.compute_ids)"
    )


# =====================================================
# CTE SYNTAX FIX
# =====================================================
def fix_cte_syntax(sql: str) -> str:
    """
    Fix common LLM CTE comma mistakes.
    """

    sql = re.sub(r"\),\s*,", "),", sql)

    sql = re.sub(
        r"\),\s*SELECT",
        ") SELECT",
        sql,
        flags=re.IGNORECASE
    )

    return sql
def validate_columns(sql: str, tables: dict):
    """
    Block SQL if unknown columns appear.
    """

    import re

    all_cols = set()

    for _, df in tables.items():
        if hasattr(df, "columns"):
            all_cols.update(df.columns)

    used_cols = re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b", sql)

    blocked = []

    for col in used_cols:
        if col in [
            "SELECT","FROM","WHERE","JOIN","ON","AND","OR",
            "GROUP","BY","ORDER","LIMIT","AS","AVG","SUM",
            "COUNT","MIN","MAX","CAST","EXTRACT","EPOCH"
        ]:
            continue

        if col.endswith("_id"):
            continue

        if col not in all_cols:
            blocked.append(col)

    return blocked