# Put settings in this file that will change depending on the
# machine, such as database hosts and external resource paths.
# One of these files exist for each enviornment this app will run in.

debug = True
cache_engine = 'redis' # or 'redis', 'locmem', 'database'
cache_host = 'localhost'

auth_engine = 'database' # or a `KeyValue` object.

db_engine = 'sqlite3'
db_name = 'sqlite.db'

#db_engine = 'postgres' # or 'mysql'
#db_name = 'my_project'
#db_port = 5433
#db_host = 'localhost'
#db_username = 'postgres'
#db_password = 'password'