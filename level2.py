from google.cloud import bigquery
import os

GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

client = bigquery.Client().from_service_account_json(GOOGLE_APPLICATION_CREDENTIALS)

dataset_ref = client.dataset("bigquery-public-data", project="ga_sessions_20170801")

query = """
SELECT *
FROM `bigquery-public-data.google_analytics_sample.ga_sessions_20170801`
LIMIT 10
"""

query_job = client.query(query)

results = query_job.result().to_dataframe()

print(results)
