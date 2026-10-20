import os

import pandas as pd
import streamlit as st
from databricks import sql
from databricks.sdk.core import Config

# Credentials come from the app's own service principal, injected by the platform.
# Nothing in this code holds a secret.
cfg = Config()
# When the app.yaml config uses valueFrom (camelCase), the platform injects these
# automatically. The fallbacks below let the app start even if the config update
# hasn't been applied yet (e.g. before the next bundle deploy).
WAREHOUSE_ID = os.environ.get("DATABRICKS_WAREHOUSE_ID", "dfa0999ca36feaa8")
TABLE = os.environ.get("DEMO_TABLE", "workspace.simple_demo.daily_trip_summary")


@st.cache_data(ttl=300)
def load(query: str) -> pd.DataFrame:
    with sql.connect(
        server_hostname=cfg.host,
        http_path=f"/sql/1.0/warehouses/{WAREHOUSE_ID}",
        credentials_provider=lambda: cfg.authenticate,
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall_arrow().to_pandas()


st.set_page_config(page_title="Simple Demo", layout="wide")
st.title("Daily Trip Summary")
st.caption(f"Source: {TABLE} (governed by Unity Catalog)")

daily = load(
    f"""
    SELECT trip_date, sum(trips) AS trips, round(avg(avg_fare), 2) AS avg_fare
    FROM {TABLE}
    GROUP BY trip_date
    ORDER BY trip_date
    """
)

col1, col2 = st.columns(2)
col1.metric("Total trips", f"{int(daily['trips'].sum()):,}")
col2.metric("Days covered", len(daily))

st.line_chart(daily, x="trip_date", y="trips")

zips = load(
    f"""
    SELECT pickup_zip, sum(trips) AS trips
    FROM {TABLE}
    GROUP BY pickup_zip
    ORDER BY trips DESC
    LIMIT 10
    """
)
st.subheader("Top 10 pickup ZIP codes")
st.dataframe(zips, hide_index=True)
