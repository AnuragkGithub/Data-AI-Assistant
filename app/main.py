import streamlit as st
import sys
import os
import plotly.express as px

# ---------------------------------------------------
# Fix import path
# ---------------------------------------------------
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.sql_guard import (
    fix_sql,
    fix_interval_sum,
    fix_table_names,
    fix_distinct_on,
    fix_invalid_sum,
    fix_cte_syntax,
    fix_missing_aliases,
    fix_duration_column,
    validate_columns
)

from core.intent_router import detect_metric, detect_domain
from core.data_loader import (
    load_dataframes,
    get_schema_summary,
    detect_relationships
)

from core.llm_agent import generate_sql
from core.query_engine import run_sql
from core.schema_rag import retrieve_schema

# ---------------------------------------------------
# Page config
# ---------------------------------------------------
st.set_page_config(
    page_title="Data AI Assistant",
    layout="wide"
)

st.title("🤖 Data AI Assistant")
st.caption(
    "Ask questions about your CSV data. "
    "Answers are generated from your data only."
)

# ---------------------------------------------------
# Load data
# ---------------------------------------------------
@st.cache_data
def _load():
    return load_dataframes()

tables = _load()

if not tables:
    st.error("No CSV files found in data/. Please add your files.")
    st.stop()

# ---------------------------------------------------
# Relationships
# ---------------------------------------------------
relationships = detect_relationships(tables)

with st.expander("Loaded tables"):
    for name, df in tables.items():
        st.write(f"**{name}** — {df.shape[0]} rows × {df.shape[1]} cols")

schema_summary = get_schema_summary(tables)

schema_summary += """

IMPORTANT RULES:
- jobs table does NOT contain column 'name'
- Use job_name or pipeline_name when available
- NEVER invent columns
"""

relationship_text = "\n".join(
    [f"{a} JOIN {b} USING ({c})" for a, b, c in relationships]
)

enhanced_schema = f"""
{schema_summary}

Detected Relationships:
{relationship_text}

Rules:
- Use DuckDB syntax only.
- Do NOT use UNNEST.
- ALWAYS prefix columns with table name when joins exist.
- If calculating duration:
  EXTRACT(EPOCH FROM (end - start))/60
"""

schema_context = schema_summary + "\nDetected Relationships:\n" + relationship_text

# ---------------------------------------------------
# Session state
# ---------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------------------------------------------
# Chat input
# ---------------------------------------------------
user_question = st.chat_input("Ask a question about your data...")

if user_question:

    st.session_state.chat_history.append(("user", user_question))

    with st.spinner("Generating SQL..."):

        sql = None
        err = None
        preferred_viz = None

        # --------------------------------------------
        # Metric detection (hardcoded SQL)
        # --------------------------------------------
        metric_result = detect_metric(user_question)

        if metric_result:
            if len(metric_result) == 3:
                sql, err, preferred_viz = metric_result
            elif len(metric_result) == 2:
                sql, preferred_viz = metric_result

        # --------------------------------------------
        # Domain-based RAG
        # --------------------------------------------
        domain = detect_domain(user_question)

        if domain != "general":
            rag_context = retrieve_schema(domain)
        else:
            rag_context = retrieve_schema(user_question)

        full_context = schema_context + "\n\nRelevant Schema:\n" + str(rag_context)

        # --------------------------------------------
        # LLM fallback
        # --------------------------------------------
        if not sql:
            sql, err = generate_sql(user_question, full_context)

    # ------------------------------------------------
    # Error from LLM
    # ------------------------------------------------
    if err:
        st.session_state.chat_history.append(
            ("assistant", f"LLM error: {err}")
        )

    else:

        # --------------------------------------------
        # SQL GUARD PIPELINE (SAFE ORDER)
        # --------------------------------------------
        sql = fix_sql(sql)
        sql = fix_table_names(sql, tables)
        sql = fix_missing_aliases(sql)
        sql = fix_distinct_on(sql)
        sql = fix_duration_column(sql)
        sql = fix_interval_sum(sql)
        sql = fix_invalid_sum(sql)
        sql = fix_cte_syntax(sql)
        invalid_cols = validate_columns(sql, tables)

        if invalid_cols:
         st.session_state.chat_history.append(
        ("assistant",
         f"SQL blocked: unknown columns detected → {invalid_cols}")
         )
         st.stop()

# --------------------------------------------
# EXECUTE SQL
# --------------------------------------------


        result, qerr = run_sql(sql, tables)

        # --------------------------------------------
        # Auto SQL fix retry
        # --------------------------------------------
        if qerr:

            fix_prompt = f"""
Fix this DuckDB SQL.

SQL:
{sql}

Error:
{qerr}

Return ONLY corrected SQL.
"""

            fixed_sql, fix_err = generate_sql(
                fix_prompt,
                full_context
            )

            if fixed_sql:
                fixed_sql = fix_sql(fixed_sql)

            if not fix_err:
                result, qerr = run_sql(fixed_sql, tables)
                sql = fixed_sql

        # --------------------------------------------
        # Store results
        # --------------------------------------------
        if qerr:
            st.session_state.chat_history.append(
                ("assistant", f"SQL error: {qerr}")
            )
        else:
            st.session_state.chat_history.append(("assistant_sql", sql))
            st.session_state.chat_history.append(("assistant_df", result))

# ---------------------------------------------------
# Render chat history
# ---------------------------------------------------
for role, content in st.session_state.chat_history:

    if role == "user":
        with st.chat_message("user"):
            st.write(content)

    elif role == "assistant":
        with st.chat_message("assistant"):
            st.write(content)

    elif role == "assistant_sql":
        with st.chat_message("assistant"):
            st.code(content, language="sql")

    elif role == "assistant_df":
        with st.chat_message("assistant"):

            df = content
            st.dataframe(df, use_container_width=True)

            if df.empty:
                st.warning("No data returned.")
                continue

            numeric_cols = df.select_dtypes(
                include=["int64", "float64"]
            ).columns.tolist()

            categorical_cols = df.select_dtypes(
                include=["object"]
            ).columns.tolist()

            st.markdown("### 📊 Visualization Settings")

            chart_type = st.selectbox(
                "Chart Type",
                ["None", "Bar", "Line", "Pie"],
                key=f"type_{id(df)}"
            )

            if chart_type == "None":
                continue

            if chart_type in ["Bar", "Line"]:

                if not numeric_cols:
                    st.warning("No numeric columns available.")
                    continue

                x_axis = st.selectbox("X-axis", df.columns, key=f"x_{id(df)}")
                y_axis = st.selectbox("Y-axis", numeric_cols, key=f"y_{id(df)}")

                if chart_type == "Bar":
                    fig = px.bar(df, x=x_axis, y=y_axis, color=x_axis, template="plotly_dark")
                else:
                    fig = px.line(df, x=x_axis, y=y_axis, markers=True, template="plotly_dark")

                st.plotly_chart(fig, use_container_width=True)

            elif chart_type == "Pie":

                if not numeric_cols or not categorical_cols:
                    st.warning("Pie chart needs categorical + numeric columns.")
                    continue

                names = st.selectbox("Category", categorical_cols, key=f"pie_cat_{id(df)}")
                values = st.selectbox("Values", numeric_cols, key=f"pie_val_{id(df)}")

                fig = px.pie(df, names=names, values=values, hole=0.4, template="plotly_dark")

                st.plotly_chart(fig, use_container_width=True)