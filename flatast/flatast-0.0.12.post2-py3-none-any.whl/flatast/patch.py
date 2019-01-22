import sqlite3
class Patch(object):

	def __init__(self):
		self.id = None
		self.time = None
		self.url = None
		self.touched_files = []
		self.content = None

	def patch_exists_in_database(self):
            conn = sqlite3.connect('gitlog.db')
            c = conn.cursor()
            c.execute("select id from patches where id = %d" % self.id)
            conn.commit()
            if len(c.fetchall()) == 0:
                conn.close()
                return False
            conn.close()
            return True
