"""Generate source-controlled Power BI reports with embedded clean CSV data."""
from pathlib import Path
import json,base64

ROOT=Path(__file__).resolve().parents[1].parent
BASE='https://developer.microsoft.com/json-schemas/fabric/item/'
def write(path,data):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,indent=2))

def projection(prop,measure=False):
 return {'field':{('Measure' if measure else 'Column'):{'Expression':{'SourceRef':{'Entity':'KPI'}},'Property':prop}},'queryRef':'KPI.'+prop}

for slug,source,period,measures,chart,title in [
 ('broadband-churn-revenue-intelligence','monthly_kpis.csv','month',[
  ('Churn Rate','DIVIDE(SUM(KPI[churned]), SUM(KPI[starting_subscribers]))','0.00%'),
  ('Retention Rate','1 - [Churn Rate]','0.00%'),
  ('End MRR','VAR LatestMonth = MAX(KPI[month]) RETURN CALCULATE(SUM(KPI[end_mrr]), KPI[month] = LatestMonth)','"INR "#,0'),
  ('ARPU','VAR LatestMonth = MAX(KPI[month]) RETURN DIVIDE(CALCULATE(SUM(KPI[end_mrr]), KPI[month] = LatestMonth), CALCULATE(SUM(KPI[active_end]), KPI[month] = LatestMonth))','"INR "#,0.00')
 ],'Churn Rate','Broadband Churn and Revenue'),
 ('telecom-network-experience-analytics','regional_kpis.csv','date',[
  ('Network Uptime','DIVIDE(SUM(KPI[available_minutes]), SUM(KPI[observed_minutes]))','0.00%'),
  ('SLA Compliance','DIVIDE(SUM(KPI[sla_met]), SUM(KPI[incidents]))','0.00%'),
  ('MTTR Minutes','DIVIDE(SUM(KPI[resolution_minutes]), SUM(KPI[incidents]))','0.00'),
  ('Incident Count','SUM(KPI[incidents])','#,0')
 ],'Network Uptime','Network Performance and Experience')]:
 import pandas as pd
 root=ROOT/slug
 if not root.exists():continue
 data=pd.read_csv(root/'data'/source);pbi=root/'powerbi'
 # A portable import partition embeds the generated sample, so Desktop needs no local path.
 encoded=base64.b64encode((root/'data'/source).read_bytes()).decode()
 types=[];columns=[]
 for col in data.columns:
  numeric=pd.api.types.is_numeric_dtype(data[col]);integer=pd.api.types.is_integer_dtype(data[col])
  columns.append({'name':col,'dataType':('int64' if integer else 'double') if numeric else 'string','sourceColumn':col,'summarizeBy':'sum' if numeric else 'none'})
  types.append('{"'+col+'", '+('Int64.Type' if integer else 'type number')+'}' if numeric else '{"'+col+'", type text}')
 m='let\n Source = Csv.Document(Binary.FromText("'+encoded+'", BinaryEncoding.Base64),[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),\n Headers = Table.PromoteHeaders(Source,[PromoteAllScalars=true]),\n Typed = Table.TransformColumnTypes(Headers, {'+', '.join(types)+'}, "en-US")\nin Typed'
 write(pbi/'Analytics.pbip',{'version':'1.0','artifacts':[{'report':{'path':'Analytics.Report'}}],'settings':{'enableAutoRecovery':True}})
 write(pbi/'Analytics.SemanticModel/definition.pbism',{'$schema':BASE+'semanticModel/definitionProperties/1.0.0/schema.json','version':'4.0','settings':{}})
 write(pbi/'Analytics.SemanticModel/model.bim',{'name':'Analytics','compatibilityLevel':1600,'model':{'culture':'en-US','defaultPowerBIDataSourceVersion':'powerBI_V3','tables':[{'name':'KPI','columns':columns,'measures':[{'name':n,'expression':e,'formatString':f} for n,e,f in measures],'partitions':[{'name':'KPI','mode':'import','source':{'type':'m','expression':m.splitlines()}}]}]}})
 write(pbi/'Analytics.Report/definition.pbir',{'$schema':BASE+'report/definitionProperties/2.0.0/schema.json','version':'4.0','datasetReference':{'byPath':{'path':'../Analytics.SemanticModel'}}})
 report=pbi/'Analytics.Report/definition'
 write(report/'report.json',{'$schema':BASE+'report/definition/report/3.1.0/schema.json','themeCollection':{}})
 write(report/'pages/pages.json',{'$schema':BASE+'report/definition/pagesMetadata/1.0.0/schema.json','pageOrder':['overview'],'activePageName':'overview'})
 page=report/'pages/overview'
 write(page/'page.json',{'$schema':BASE+'report/definition/page/1.0.0/schema.json','name':'overview','displayName':title,'displayOption':'FitToPage','height':720,'width':1280})
 def visual(name,kind,x,y,w,h,roles):
  write(page/f'visuals/{name}/visual.json',{'$schema':BASE+'report/definition/visualContainer/2.0.0/schema.json','name':name,'position':{'x':x,'y':y,'z':0,'height':h,'width':w,'tabOrder':0},'visual':{'visualType':kind,'query':{'queryState':{role:{'projections':projs} for role,projs in roles.items()}},'drillFilterOtherVisuals':True}})
 for i,(n,e,f) in enumerate(measures):visual('card'+str(i),'card',20+315*i,20,295,130,{'Values':[projection(n,True)]})
 visual('region_chart','clusteredBarChart',20,170,900,500,{'Category':[projection('region')],'Y':[projection(chart,True)]})
 visual('region_filter','slicer',950,180,300,200,{'Values':[projection('region')]})
 visual('period_filter','slicer',950,410,300,260,{'Values':[projection(period)]})
 (pbi/'measures.dax').write_text('\n\n'.join(f'{n} = {e}' for n,e,f in measures))
 (pbi/'query.pq').write_text(m)
 (pbi/'README.md').write_text(f'''# Power BI report source

Open `Analytics.pbip` in current Power BI Desktop on Windows (enable Power BI Project / PBIR preview features if prompted). The clean sample CSV is embedded in the semantic model, so no file-path edits or external credentials are needed. Refresh the model after opening. This is a native editable PBIP/PBIR source project, not a `.pbix` binary.

The report defines four KPI cards, a regional bar chart, a region slicer and a {period} slicer. `measures.dax` contains the DAX measures. `query.pq` contains the Power Query import and type conversions. Run `python analysis.py` and regenerate the PBIP sources to embed newly generated data.

**Validation boundary:** JSON definitions are checked against Microsoft PBIR schemas. The Python/SQL metric calculations and offline dashboard are separately tested. Native Power BI Desktop rendering and DAX engine execution have NOT been performed in this macOS environment. Open and verify the report in Desktop before calling it a validated Power BI dashboard or claiming professional proficiency.

Churn measures use weighted subscriber-month exposure. End MRR and ARPU use the latest month in the current filter context; summing point-in-time MRR across months would be misleading. Network uptime uses union-adjusted available minutes; SLA/MTTR use unique incident counts. The report model uses one pre-aggregated KPI fact table, deliberately avoiding fact-to-fact join fanout. Customer satisfaction is not directly measured.

Reference: https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report
''')
 print(slug, len(list(pbi.rglob('*.json'))),'report JSON files')
