import psycopg2
# twine upload dist/*


class Rpostgres(object): 
  
	def __init__(self, host, database, user, password, port=5432 ):
		# Connect to the database
		self.connection = psycopg2.connect(host=host, database=database, user=user, password=password, port=port) 

 
	def set(self, sql, params = None):
		cur = self.connection.cursor()
		cur.execute(sql, params)
		self.connection.commit() 
		cur.close()
		return cur.rowcount
	
 
	def get(self, sql, params = None):  
		cur = self.connection.cursor()
		cur.execute(sql, params)
		result = cur.fetchall()  
		cur.close()
		return result

