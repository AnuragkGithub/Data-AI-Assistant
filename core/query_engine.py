import duckdb


def run_sql(sql: str, tables: dict):

    con = duckdb.connect()

    try:
        # Register tables
        for name, df in tables.items():
            con.register(name, df)

        # -------------------------------
        # FORCE CAST TIME COLUMNS
        # -------------------------------
        for name, df in tables.items():
            for col in df.columns:
                if "time" in col.lower():
                    try:
                        con.execute(
                            f"""
                            CREATE OR REPLACE VIEW {name}_view AS
                            SELECT *,
                            TRY_CAST({col} AS TIMESTAMP) AS {col}_ts
                            FROM {name}
                            """
                        )
                    except:
                        pass

        result = con.execute(sql).df()

        return result, None

    except Exception as e:
        return None, str(e)

    finally:
        con.close()
