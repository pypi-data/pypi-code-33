from . import db3
import psycopg2
from .dbtypes import DB_PGSQL, DB_SQLITE3

class open (db3.open):
	def __init__ (self, dbname, user, password, host = '127.0.0.1', port = 5432, dir = None, auto_reload = False):
		self.conn = psycopg2.connect (host=host, dbname=dbname, user=user, password=password, port = port)
		self.__init (dir, auto_reload, DB_PGSQL)		
		
	def field_names (self):
		return [x.name for x in self.description]
		
		