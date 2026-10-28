-- Aggregate the two fact tables separately to avoid multiplying exposure by incidents.
WITH exposure AS (
 SELECT region,SUM(observed_minutes) AS observed_minutes,SUM(available_minutes) AS available_minutes,
 SUM(downtime_minutes) AS downtime_minutes FROM site_daily GROUP BY region
), incident_summary AS (
 SELECT s.region,COUNT(*) AS incidents,SUM(i.sla_met) AS sla_met,
 SUM(i.duration_minutes) AS resolution_minutes
 FROM incidents i JOIN sites s ON i.site_id=s.site_id GROUP BY s.region
), kpis AS (
 SELECT e.*,COALESCE(i.incidents,0) AS incidents,COALESCE(i.sla_met,0) AS sla_met,
 100.0*available_minutes/NULLIF(observed_minutes,0) AS uptime_pct,
 100.0*i.sla_met/NULLIF(i.incidents,0) AS sla_compliance_pct,
 1.0*i.resolution_minutes/NULLIF(i.incidents,0) AS mttr_minutes
 FROM exposure e LEFT JOIN incident_summary i ON e.region=i.region
)
SELECT *,DENSE_RANK() OVER(ORDER BY uptime_pct ASC) AS reliability_priority FROM kpis;
