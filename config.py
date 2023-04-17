import os

creds = {
    "host" : "127.0.0.1",
    "port" : 5432,
    "database" : "deident",
    "connect_timeout" : 10,
    "user" : "webapp",
}


def make_url():
    password = os.environ['DATABASE_PASSWORD']
    return 'postgresql://%s:%s@%s:%d/%s' % (creds['user'],
                                            password,
                                            creds['host'],
                                            creds['port'],
                                            creds['database']) 

if 'DATABASE_URL' in os.environ and os.environ['DATABASE_URL']:
    url = os.environ['DATABASE_URL']
else:
    print("DATABASE_URL unknown, connecting to local database")
    url = make_url()
