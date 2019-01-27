import sqlite3
import os
  

class Rsqlite(object): 
  
	def __init__(self, database, path=None):
		# Connect to the database
		if not path:	
			dir_path = os.path.dirname(os.path.realpath(__file__))
			path = dir_path+'/sqlite/'
		self.connection = sqlite3.connect(path+database) 

 
	def set(self, sql, params = None):
		cur = self.connection.cursor()
		if params:
			cur.executemany(sql, params)
		else:		
			cur.execute(sql)
		self.connection.commit() 
		cur.close()
		return cur.rowcount
	
 
	def get(self, sql, params = None):  
		cur = self.connection.cursor()
		if params:
			cur.execute(sql, params)
		else:		
			cur.execute(sql)
		result = cur.fetchall()  
		cur.close()
		return result

