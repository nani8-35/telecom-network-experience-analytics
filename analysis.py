"""Synthetic network reliability analytics with interval-union downtime."""
from common import *
import numpy as np

def union_minutes(intervals):
    """Union of half-open minute intervals, clipped to the observation day."""
    clean=sorted((max(0,float(s)),min(1440,float(e))) for s,e in intervals if min(1440,float(e))>max(0,float(s)))
    total=0;end=0
    for start,stop in clean:
        total+=max(0,stop-max(start,end));end=max(end,stop)
    return total

def generate(seed=84):
    rng=np.random.default_rng(seed)
    sites=pd.DataFrame({'site_id':range(1,31),'region':np.repeat(['North','South','East'],10),'subscribers':rng.integers(100,1000,30)})
    rows=[]
    for i in range(420):
        day=str(pd.Timestamp('2026-01-01').date()+pd.Timedelta(days=int(rng.integers(0,60))))
        start=int(rng.integers(0,1300));duration=int(rng.integers(5,140));severity=str(rng.choice(['Critical','Major','Minor']))
        rows.append([i+1,int(rng.integers(1,31)),day,start,start+duration,severity,str(rng.choice(['Power','Fiber','Configuration','Hardware']))])
    incidents=pd.DataFrame(rows,columns=['incident_id','site_id','date','start_minute','end_minute','severity','cause'])
    # Intentional raw duplicates demonstrate deterministic de-duplication.
    return sites,pd.concat([incidents,incidents.iloc[:12]],ignore_index=True)

def clean_incidents(raw):
    df=raw.drop_duplicates('incident_id').copy()
    required=['incident_id','site_id','date','start_minute','end_minute','severity']
    if df[required].isna().any().any():raise ValueError('Missing mandatory incident fields')
    if (df.end_minute<=df.start_minute).any():raise ValueError('Resolution must follow incident start')
    if not df.severity.isin(['Critical','Major','Minor']).all():raise ValueError('Unknown severity')
    df['duration_minutes']=df.end_minute-df.start_minute
    df['sla_minutes']=df.severity.map({'Critical':60,'Major':120,'Minor':240})
    df['sla_met']=(df.duration_minutes<=df.sla_minutes).astype(int)
    return df

def daily_exposure(sites,incidents):
    rows=[]
    lookup={k:list(zip(g.start_minute,g.end_minute)) for k,g in incidents.groupby(['site_id','date'])}
    for day in pd.date_range('2026-01-01',periods=60):
        date=str(day.date())
        for site in sites.itertuples():
            down=union_minutes(lookup.get((site.site_id,date),[]))
            rows.append([site.site_id,date,site.region,1440,down,1440-down,down*site.subscribers])
    return pd.DataFrame(rows,columns=['site_id','date','region','observed_minutes','downtime_minutes','available_minutes','subscriber_minutes_affected'])

def main():
    for d in ['data','reports']:(ROOT/d).mkdir(exist_ok=True)
    sites,raw=generate();raw.to_csv(ROOT/'data/incidents_raw.csv',index=False);sites.to_csv(ROOT/'data/sites.csv',index=False)
    inc=clean_incidents(raw);inc.to_csv(ROOT/'data/incidents.csv',index=False)
    daily=daily_exposure(sites,inc);daily.to_csv(ROOT/'data/site_daily.csv',index=False)
    reliability=daily.groupby(['date','region'],as_index=False).sum(numeric_only=True).drop(columns='site_id')
    grouped=inc.merge(sites,on='site_id',validate='many_to_one').groupby(['date','region'],as_index=False).agg(incidents=('incident_id','size'),sla_met=('sla_met','sum'),resolution_minutes=('duration_minutes','sum'))
    result=reliability.merge(grouped,on=['date','region'],how='left').fillna(0)
    result.to_csv(ROOT/'data/regional_kpis.csv',index=False)
    with sqlite3.connect(ROOT/'reports/analytics.sqlite') as conn:
        for name,frame in [('sites',sites),('incidents',inc),('site_daily',daily)]:save_table(conn,frame,name)
        sql=pd.read_sql_query((ROOT/'sql/analysis.sql').read_text(),conn);sql.to_csv(ROOT/'reports/sql_regions.csv',index=False)
    metrics={'raw_rows':len(raw),'clean_incidents':len(inc),'duplicates_removed':len(raw)-len(inc),'site_days':len(daily),'uptime_pct':float(daily.available_minutes.sum()/daily.observed_minutes.sum()*100),'sla_compliance_pct':float(inc.sla_met.mean()*100),'mttr_minutes':float(inc.duration_minutes.mean())}
    (ROOT/'reports/metrics.json').write_text(json.dumps(metrics,indent=2))
    dashboard(result,'Telecom Network & Customer Experience Analytics',[
        dict(label='Network uptime',numerator='available_minutes',denominator='observed_minutes',scale=100,format='percent'),
        dict(label='SLA compliance',numerator='sla_met',denominator='incidents',scale=100,format='percent'),
        dict(label='MTTR (minutes)',numerator='resolution_minutes',denominator='incidents',scale=1,format='number'),
        dict(label='Service incidents',numerator='incidents',format='number')],'date')
    worst=sql.sort_values('uptime_pct').iloc[0]
    (ROOT/'reports/findings.md').write_text(f"# Synthetic network findings\n\n- {len(daily):,} site-days across 30 sites and 60 observation days.\n- Removed {metrics['duplicates_removed']} duplicate raw incidents; retained {len(inc)} unique incidents.\n- Uptime {metrics['uptime_pct']:.3f}%; incident SLA compliance {metrics['sla_compliance_pct']:.2f}%; MTTR {metrics['mttr_minutes']:.2f} minutes.\n- Lowest simulated regional uptime: {worst['region']} ({worst['uptime_pct']:.3f}%).\n\n## Recommendations\nReview recurring causes and the worst-performing sites before prioritizing preventive maintenance. Validate customer impact with real ticket and survey data before making commercial decisions.\n\n## Metric contract and limitations\nUptime = union-adjusted available site-minutes / observed site-minutes. Every site has a 24-hour observation denominator, including days without incidents. Overlapping incidents count once for downtime; incident counts and MTTR count each unique incident. SLA is resolution time <= severity target (Critical 60, Major 120, Minor 240 minutes). All generated incidents are resolved within one observation day; cleaning fails on missing times or invalid durations. Subscriber-minutes affected assumes all subscribers at an affected site lose service, a proxy rather than measured satisfaction. There is no measured CSAT/NPS or real operator data.\n")
    print(json.dumps(metrics,indent=2))

if __name__=='__main__':main()
