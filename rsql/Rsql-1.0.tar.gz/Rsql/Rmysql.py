import pymysql.cursors  
# twine upload dist/*


class Rmysql(object): 
  
	def __init__(self, host, database, user, password, port=3306 ):
		# Connect to the database
		self.connection = pymysql.connect(host=host, database=database, user=user, password=password, port=port, 
		cursorclass=pymysql.cursors.DictCursor) 

 
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

