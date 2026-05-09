import os
import pandas as pd

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data"
)

EXPECTED_FILES = {
    "jobs": "jobs.csv",
    "job_run_timeline": "job_run_timeline.csv",
    "job_task_run_timeline": "job_task_run_timeline.csv",
    "job_tasks": "job_tasks.csv",
}


def load_dataframes():
    tables = {}

    for file in os.listdir(DATA_DIR):

        # ignore mac hidden files
        if file.startswith("._"):
            continue

        if not file.endswith(".csv"):
            continue

        table_name = file.replace(".csv", "")
        path = os.path.join(DATA_DIR, file)

        try:
            df = pd.read_csv(path)

            # auto convert time/date columns
            for col in df.columns:
                if "time" in col.lower() or "date" in col.lower():
                    df[col] = pd.to_datetime(
                        df[col],
                        errors="coerce",
                        format="mixed"
                    )

            tables[table_name] = df

        except Exception as e:
            print(f"Skipping {file}: {e}")

    return tables

def get_schema_summary(tables):
    lines = []

    for name, df in tables.items():
        cols = ", ".join(
            [f"{c} ({str(t)})" for c, t in df.dtypes.items()]
        )

        lines.append(
            f"Table: {name}\nColumns: {cols}\n"
        )

    return "\n".join(lines)
def detect_relationships(tables):
    """
    Auto-detect table relationships using common column names.
    """

    relationships = []

    table_names = list(tables.keys())

    for i, t1 in enumerate(table_names):
        cols1 = set(tables[t1].columns)

        for t2 in table_names[i+1:]:
            cols2 = set(tables[t2].columns)

            common_cols = cols1.intersection(cols2)

            for col in common_cols:

                # strong relationship candidates
                if (
                    col.endswith("_id")
                    or col in ["id", "workspace_id", "job_id", "warehouse_id"]
                ):
                    relationships.append(
                        (t1, t2, col)
                    )

    return relationships
def build_join_clause(tables_needed, relationships):
    """
    Dynamically build JOIN clause using detected relationships.
    """

    if len(tables_needed) == 1:
        return f"FROM {tables_needed[0]}"

    base = tables_needed[0]
    join_sql = f"FROM {base}"

    joined = {base}

    for table in tables_needed[1:]:

        for t1, t2, col in relationships:

            if t1 in joined and t2 == table:
                join_sql += f"\nJOIN {t2} ON {t1}.{col} = {t2}.{col}"
                joined.add(t2)
                break

            elif t2 in joined and t1 == table:
                join_sql += f"\nJOIN {t1} ON {t2}.{col} = {t1}.{col}"
                joined.add(t1)
                break

    return join_sql
