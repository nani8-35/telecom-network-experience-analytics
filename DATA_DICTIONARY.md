# Data dictionary

All records are generated; no source operator or subscriber data.

## incidents_raw.csv

Grain: incident / site-day / regional-day; see filename.

| Column | Type |
|---|---|
| incident_id | int64 |
| site_id | int64 |
| date | object |
| start_minute | int64 |
| end_minute | int64 |
| severity | object |
| cause | object |

## sites.csv

Grain: incident / site-day / regional-day; see filename.

| Column | Type |
|---|---|
| site_id | int64 |
| region | object |
| subscribers | int64 |

## site_daily.csv

Grain: incident / site-day / regional-day; see filename.

| Column | Type |
|---|---|
| site_id | int64 |
| date | object |
| region | object |
| observed_minutes | int64 |
| downtime_minutes | float64 |
| available_minutes | float64 |
| subscriber_minutes_affected | float64 |

## regional_kpis.csv

Grain: incident / site-day / regional-day; see filename.

| Column | Type |
|---|---|
| date | object |
| region | object |
| observed_minutes | int64 |
| downtime_minutes | float64 |
| available_minutes | float64 |
| subscriber_minutes_affected | float64 |
| incidents | float64 |
| sla_met | float64 |
| resolution_minutes | float64 |

## incidents.csv

Grain: incident / site-day / regional-day; see filename.

| Column | Type |
|---|---|
| incident_id | int64 |
| site_id | int64 |
| date | object |
| start_minute | int64 |
| end_minute | int64 |
| severity | object |
| cause | object |
| duration_minutes | int64 |
| sla_minutes | int64 |
| sla_met | int64 |

## Units and keys

Monetary amounts: INR per month. Rates in CSV: fractions (0–1). Uptime/SLA percentages in summary JSON/SQL: percent (0–100). Network durations: minutes. `customer_id`, `incident_id`, and `site_id` are synthetic keys. Aggregated rows are uniquely identified by region and period. See `reports/findings.md` for exact KPI contracts.