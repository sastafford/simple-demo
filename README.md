# simple-demo

A small end-to-end Databricks project packaged as a Declarative Automation Bundle (formerly Databricks Asset Bundles): a schema, a declarative pipeline, a job, an app and a dashboard, built on the built-in `samples.nyctaxi` dataset. It runs on any workspace with serverless compute, including Databricks Free Edition.

## What it deploys

| Resource | File | Notes |
|---|---|---|
| Schema `workspace.simple_demo` | `resources/schema.yml` | Created first; everything else lands here |
| Pipeline `simple-demo-trips` | `resources/pipeline.yml`, `src/pipeline/trips.sql` | Serverless, bronze → silver (data quality rules) → gold |
| Job `simple-demo-job` | `resources/job.yml`, `src/notebooks/validate.py` | Pipeline refresh, then a validation task. Schedule is paused. |
| App `simple-demo-app` | `resources/app.yml`, `src/app/` | Streamlit app that runs as its own service principal |
| Dashboard | Captured from the UI (step 5) | `bundle generate dashboard` turns it into code |

Free Edition fit: one pipeline (limit is one per type), two job tasks (limit is 5 concurrent), one app (limit is 3), and the single starter warehouse.

## Runbook

Set the profile once: `export P=<your-profile>`. On Free Edition, authenticate with `databricks auth login --host <workspace-url>` or a personal access token.

1. **Validate and deploy**
   ```bash
   databricks bundle validate -p $P
   databricks bundle deploy -p $P
   ```
2. **Run the job.** This builds the tables. The first serverless run takes a few minutes.
   ```bash
   databricks bundle run simple_demo_job -p $P
   ```
3. **Grant the app read access.** The app's service principal starts with no data access. Get its ID:
   ```bash
   databricks apps get simple-demo-app -p $P -o json | grep service_principal_client_id
   ```
   Then in the SQL editor:
   ```sql
   GRANT USE CATALOG ON CATALOG workspace TO `<service_principal_client_id>`;
   GRANT USE SCHEMA, SELECT ON SCHEMA workspace.simple_demo TO `<service_principal_client_id>`;
   ```
4. **Start the app**
   ```bash
   databricks bundle run simple_demo_app -p $P
   ```
   Free Edition stops apps 24 hours after a start or redeploy. Start it shortly before you need it.
5. **Build the dashboard in the UI, then capture it as code.** Create an AI/BI dashboard on `workspace.simple_demo.daily_trip_summary` and publish it. Then:
   ```bash
   databricks bundle generate dashboard --existing-id <dashboard-id> --key simple_demo_dashboard -p $P
   ```
   Open the generated YAML in `resources/` and add `warehouse_id: ${var.warehouse_id}`. Run `bundle deploy` again and the dashboard is now managed by the bundle.

## Reset

```bash
databricks bundle destroy -p $P
```

This removes the schema, pipeline, job, app and (if captured) the dashboard.
