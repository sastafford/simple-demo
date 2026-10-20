-- Bronze: raw copy of the built-in sample dataset.
CREATE OR REFRESH MATERIALIZED VIEW trips_bronze
COMMENT "Raw NYC taxi trips from the built-in samples catalog."
AS SELECT * FROM samples.nyctaxi.trips;

-- Silver: data quality rules are declared with the table, enforced on every run,
-- and recorded in the pipeline event log.
CREATE OR REFRESH MATERIALIZED VIEW trips_silver (
  CONSTRAINT positive_distance EXPECT (trip_distance > 0) ON VIOLATION DROP ROW,
  CONSTRAINT positive_fare     EXPECT (fare_amount > 0)   ON VIOLATION DROP ROW,
  CONSTRAINT dropoff_after_pickup EXPECT (tpep_dropoff_datetime > tpep_pickup_datetime)
)
COMMENT "Trips that pass data quality rules."
AS SELECT
  tpep_pickup_datetime,
  tpep_dropoff_datetime,
  trip_distance,
  fare_amount,
  pickup_zip,
  dropoff_zip
FROM trips_bronze;

-- Gold: the table the app and dashboard read.
CREATE OR REFRESH MATERIALIZED VIEW daily_trip_summary
COMMENT "Daily trip counts and averages by pickup ZIP code."
AS SELECT
  date(tpep_pickup_datetime)  AS trip_date,
  pickup_zip,
  count(*)                    AS trips,
  round(avg(fare_amount), 2)  AS avg_fare,
  round(avg(trip_distance), 2) AS avg_distance
FROM trips_silver
GROUP BY ALL;
