def build_schema_chunks(tables):
    
    chunks = []

    for name, df in tables.items():

        cols = ", ".join(df.columns)

        chunk = f"""
Table: {name}
Columns: {cols}
"""

        chunks.append(chunk)

    return chunks
