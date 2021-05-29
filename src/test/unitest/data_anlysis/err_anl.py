import psycopg2
import unittest
from concurrent.futures import ThreadPoolExecutor,as_completed

def w():
    dsn = "postgresql://postgres:123456@10.130.160.114:60030/my_test"
    con = psycopg2.connect(dsn)
    cur = con.cursor()
    cur.execute("select * from wake_up;")
    print(cur.fetchall())

def w2():
    con = psycopg2.connect(host="172.16.101.118", user="gpadmin", password="gpadmin", database="cs_model_v3_210304")
    cur = con.cursor()
    # cur.execute("SELECT pg_sleep(10);")
    print(cur.fetchall())

class ErrorAnlTestCase(unittest.TestCase):
    def setUp(self):
        pool = ThreadPoolExecutor(max_workers=1000)
        v_ = []
        self.dsn = "postgresql://postgres:123456@10.130.160.114:60030/my_test"
        for i in range(20000):
            v_.append(pool.submit(w2))
        for x in as_completed(v_):
            x.result()
        self.con = psycopg2.connect(self.dsn)
        self.cur = self.con.cursor()


    # def tearDown(self):
    #     self.cur.close()
    #     self.con.close()



    def perf_anl(self):
        parent_id = "610993"
        sql = f"""
                SELECT c.delta,c.sub_id,c.t from 
                	(select a.sub_id as sub_id, a.timestamp,b.timestamp,b.timestamp-a.timestamp as delta,a.timestamp as t from 
                		(SELECT sub_id,timestamp,state from task_track where parent_id='{parent_id}' and state='0') as a 
                			join 
                		(SELECT sub_id,timestamp,state from task_track where parent_id='{parent_id}' and state='1') as b 
                			on 
                		a.sub_id=b.sub_id
                	) as c order by c.sub_id;
                """

    def test_err_anl(self):
        root_id = "1008984"
        sql = f'''SELECT name,location,"desc" from task_track where root_id='{root_id}' and state=2'''
        # forget about it
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for r in res:
            func_name = r[0]
            loc = r[1]
            desc = r[2]
            print(func_name,loc)
            print("---------------------")
            print(desc)
            print("=====================")

if __name__ == '__main__':
    unittest.main()
