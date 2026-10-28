# Synthetic network findings

- 1,800 site-days across 30 sites and 60 observation days.
- Removed 12 duplicate raw incidents; retained 420 unique incidents.
- Uptime 98.785%; incident SLA compliance 76.67%; MTTR 75.19 minutes.
- Lowest simulated regional uptime: East (98.569%).

## Recommendations
Review recurring causes and the worst-performing sites before prioritizing preventive maintenance. Validate customer impact with real ticket and survey data before making commercial decisions.

## Metric contract and limitations
Uptime = union-adjusted available site-minutes / observed site-minutes. Every site has a 24-hour observation denominator, including days without incidents. Overlapping incidents count once for downtime; incident counts and MTTR count each unique incident. SLA is resolution time <= severity target (Critical 60, Major 120, Minor 240 minutes). All generated incidents are resolved within one observation day; cleaning fails on missing times or invalid durations. Subscriber-minutes affected assumes all subscribers at an affected site lose service, a proxy rather than measured satisfaction. There is no measured CSAT/NPS or real operator data.
