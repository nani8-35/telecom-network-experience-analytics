from pathlib import Path
import json, sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parent

def dashboard(frame, title, metrics, period):
    """Offline dashboard; aggregate numerators before deriving filtered ratios."""
    template = (ROOT / 'dashboard_template.html').read_text()
    payload = dict(rows=frame.to_dict('records'), title=title, metrics=metrics, period=period)
    (ROOT/'reports'/'dashboard.html').write_text(template.replace('__PAYLOAD__', json.dumps(payload)), encoding='utf8')

def save_table(conn, frame, name):
    frame.to_sql(name, conn, index=False, if_exists='replace')
