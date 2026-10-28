import unittest,sys,sqlite3
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from analysis import *
class NetworkTests(unittest.TestCase):
    def test_interval_union(self):
        self.assertEqual(union_minutes([(10,30),(20,50),(50,60)]),50)
        self.assertEqual(union_minutes([(-10,5),(1430,1500)]),15)
        self.assertEqual(union_minutes([]),0)
    def test_cleaning_and_sla_boundary(self):
        _,raw=generate();clean=clean_incidents(raw);self.assertEqual(len(raw)-len(clean),12)
        fixture=clean.iloc[:1].copy();fixture['severity']='Critical';fixture['start_minute']=0;fixture['end_minute']=60
        self.assertEqual(clean_incidents(fixture).sla_met.iloc[0],1)
        fixture['end_minute']=-1
        with self.assertRaises(ValueError):clean_incidents(fixture)
    def test_exposure_and_sql(self):
        sites,raw=generate();inc=clean_incidents(raw);daily=daily_exposure(sites,inc)
        self.assertEqual(len(daily),1800);self.assertTrue(daily.downtime_minutes.between(0,1440).all())
        self.assertTrue((daily.available_minutes+daily.downtime_minutes==1440).all())
        with sqlite3.connect(':memory:') as conn:
            for name,frame in [('sites',sites),('incidents',inc),('site_daily',daily)]:save_table(conn,frame,name)
            got=pd.read_sql_query((ROOT/'sql/analysis.sql').read_text(),conn)
        self.assertEqual(got.incidents.sum(),len(inc));self.assertEqual(got.observed_minutes.sum(),1800*1440)
        self.assertAlmostEqual(got.available_minutes.sum()/got.observed_minutes.sum()*100,daily.available_minutes.sum()/daily.observed_minutes.sum()*100)
if __name__=='__main__':unittest.main()
