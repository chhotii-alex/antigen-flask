import os
from sqlalchemy import create_engine
from sqlalchemy import text

creds = {
    "host" : "127.0.0.1",
    "port" : 5432,
    "database" : "deident",
    "connect_timeout" : 10,
    "user" : "webapp",
    "password" : "LieutenantCommander"
}


def make_url():
    return 'postgresql://%s:%s@%s:%d/%s' % (creds['user'],
                                            creds['password'],
                                            creds['host'],
                                            creds['port'],
                                            creds['database']) 

if 'DATABASE_URL' in os.environ:
    url = os.environ['DATABASE_URL']
else:
    print("DATABASE_URL unknown, connecting to local database")
    url = make_url()

db = create_engine(url)
with db.connect() as connection:
    sample_query = "select count(*) from DeidentResults"
    result = connection.execute(text(sample_query))
    for row in result:
        print(row)
    
"""
with psycopg2.connect(url) as connection:
    print("Connected to database!")

    with connection.cursor() as cursor:
        cursor.execute("select count(*) from DeidentResults")
        while True:
            row = cursor.fetchone()
            if not row:
                break
            print(row)
"""
