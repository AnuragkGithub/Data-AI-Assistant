import itertools


def detect_relationships(tables):
    """
    Automatically detect relationships between tables
    based on shared column names.
    """

    relationships = []

    table_names = list(tables.keys())

    for t1, t2 in itertools.combinations(table_names, 2):

        cols1 = set(tables[t1].columns)
        cols2 = set(tables[t2].columns)

        common_cols = cols1.intersection(cols2)

        # only meaningful keys
        key_cols = [
            c for c in common_cols
            if c.endswith("_id")
            or "id" in c.lower()
        ]

        for key in key_cols:
            relationships.append(
                f"{t1}.{key} = {t2}.{key}"
            )

    return relationships
