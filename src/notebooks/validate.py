# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# Fails the job if the pipeline produced no output, so a bad run is visible in the job history.

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema", "simple_demo")
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")

# COMMAND ----------

table = f"{catalog}.{schema}.daily_trip_summary"
row_count = spark.table(table).count()

if row_count == 0:
    raise ValueError(f"{table} is empty; the pipeline run produced no output.")

print(f"{table}: {row_count} rows")