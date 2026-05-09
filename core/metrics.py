# -------------------------------------------
# Semantic Metric Layer
# -------------------------------------------

METRICS = {
    "total_jobs": {
        "keywords": ["total jobs", "how many jobs", "count jobs"],
        "sql": """
            SELECT COUNT(*) AS total_jobs
            FROM jobs
        """,
        "viz": "kpi"
    },

    "jobs_by_status": {
        "keywords": ["jobs by status", "status distribution", "total jobs by status"],
        "sql": """
            SELECT result_state AS status,
                   COUNT(*) AS total_jobs
            FROM job_run_timeline
            GROUP BY result_state
        """,
        "viz": "bar"
    },

    "failed_jobs_last_days": {
        "keywords": ["failed jobs", "jobs failed", "failure count"],
        "sql_template": """
            SELECT COUNT(*) AS failed_jobs
            FROM job_run_timeline
            WHERE result_state = 'FAILED'
              AND period_end_time >= CURRENT_DATE - INTERVAL {days} DAY
        """,
        "viz": "kpi"
    },

    "failure_rate": {
        "keywords": ["failure rate", "fail percentage"],
        "sql_template": """
            SELECT
                SUM(CASE WHEN result_state='FAILED' THEN 1 ELSE 0 END)*1.0
                / COUNT(*) AS failure_rate
            FROM job_run_timeline
            WHERE period_end_time >= CURRENT_DATE - INTERVAL {days} DAY
        """,
        "viz": "kpi"
    },

    "longest_running_jobs": {
        "keywords": ["longest running", "slowest jobs", "job duration"],
        "sql": """
            SELECT
                j.job_id,
                j.name,
                EXTRACT(EPOCH FROM
                    (jrt.period_end_time - jrt.period_start_time)
                ) / 60 AS duration_minutes
            FROM jobs j
            JOIN job_run_timeline jrt
              ON j.job_id = jrt.job_id
            ORDER BY duration_minutes DESC
            LIMIT 10
        """,
        "viz": "bar"
    },
    "unstable_execution": {
    "keywords": ["unstable execution", "runtime variability"],
    "sql": """(SQL ABOVE HERE)""",
    "viz": "bar"
}
}
