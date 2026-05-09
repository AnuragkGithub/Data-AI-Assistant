import re
from core.metrics import METRICS


def detect_metric(question: str):

    q = question.lower()

    for metric_name, config in METRICS.items():
        for keyword in config["keywords"]:

            if keyword in q:

                match = re.search(r"(\d+)\s*day", q)
                days = match.group(1) if match else "7"

                if "sql_template" in config:
                    sql = config["sql_template"].format(days=days)
                else:
                    sql = config["sql"]

                # return SAME structure as LLM
                return sql, None, config["viz"]

    return None, None, None
def detect_domain(question: str):
    
    q = question.lower()

    if "pipeline" in q:
        return "pipeline"

    if "warehouse" in q:
        return "warehouse"

    if "dataset" in q:
        return "dataset"

    if "job" in q:
        return "job"

    return "general"
