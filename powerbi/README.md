# Power BI report source

Open `Analytics.pbip` in current Power BI Desktop on Windows (enable Power BI Project / PBIR preview features if prompted). The clean sample CSV is embedded in the semantic model, so no file-path edits or external credentials are needed. Refresh the model after opening. This is a native editable PBIP/PBIR source project, not a `.pbix` binary.

The report defines four KPI cards, a regional bar chart, a region slicer and a date slicer. `measures.dax` contains the DAX measures. `query.pq` contains the Power Query import and type conversions. Run `python analysis.py` and regenerate the PBIP sources to embed newly generated data.

**Validation boundary:** JSON definitions are checked against Microsoft PBIR schemas. The Python/SQL metric calculations and offline dashboard are separately tested. Native Power BI Desktop rendering and DAX engine execution have NOT been performed in this macOS environment. Open and verify the report in Desktop before calling it a validated Power BI dashboard or claiming professional proficiency.

Churn measures use weighted subscriber-month exposure. End MRR and ARPU use the latest month in the current filter context; summing point-in-time MRR across months would be misleading. Network uptime uses union-adjusted available minutes; SLA/MTTR use unique incident counts. The report model uses one pre-aggregated KPI fact table, deliberately avoiding fact-to-fact join fanout. Customer satisfaction is not directly measured.

Reference: https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report

Regenerate embedded model/report files with `python tools/build_powerbi.py` from the repository root.
