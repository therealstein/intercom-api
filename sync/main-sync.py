import dataset
import datetime
import time
import schedule
import os
import psycopg2

mydb = 'mysql://root:'+os.environ['IC_DBPassword']+'@intercom-db/'+os.environ['IC_Database']
t_host = os.environ['DB_HOST']
t_port = os.environ['DB_PORT']
t_dbname = os.environ['DB_NAME']
t_user = os.environ['DB_USER']
t_pw = os.environ['DB_PASS']


def get_users():
    db_conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_dbname, user=t_user, password=t_pw)
    db_cursor = db_conn.cursor()
    # SQL to get records from Postgres
    s = "SELECT * FROM users"
    # Error trapping
    try:
        # Execute the SQL
        db_cursor.execute(s)
        # Retrieve records from Postgres into a Python List
        list_users = db_cursor.fetchall()
        db = dataset.connect(mydb,engine_kwargs={'pool_recycle': 3600})
        for i in list_users:
            db['wiki_users'].upsert(dict(wiki_id=i[0],email=i[1],name=i[2]), ['wiki_id'])
        db.executable.close()
    except psycopg2.Error as e:
        t_message = "Database error"
        return
    # Close the database cursor and connection
    db_cursor.close()
    db_conn.close()
    return

def get_groups():
    db_conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_dbname, user=t_user, password=t_pw)
    db_cursor = db_conn.cursor()
    # SQL to get records from Postgres
    s = "SELECT * FROM groups"
    # Error trapping
    try:
        # Execute the SQL
        db_cursor.execute(s)
        # Retrieve records from Postgres into a Python List
        list_groups = db_cursor.fetchall()
        db = dataset.connect(mydb,engine_kwargs={'pool_recycle': 3600})
        print(list_groups)
        for i in list_groups:
            db['wiki_groups'].upsert(dict(wiki_id=i[0],name=i[1]), ['wiki_id'])
        db.executable.close()
    except psycopg2.Error as e:
        t_message = "Database error"
        return
    # Close the database cursor and connection
    db_cursor.close()
    db_conn.close()
    return

def update_db():
    return

def job():
    get_groups()
    get_users()
    return

get_groups()
get_users()
schedule.every(5).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)

