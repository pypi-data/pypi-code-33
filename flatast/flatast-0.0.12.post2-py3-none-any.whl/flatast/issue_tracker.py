import sqlite3

class IssueTracker(object):

	def __init__(self):
		self.id = None
		self.summary = None
		self.description = None
		self.type = None
		self.status = None
		self.priority = None
		self.owner = None
		self.creater = None
		self.is_private = False
		self.crate_date = None
		self.update_date = None
		self.patch_list = []

	def issue_exists_in_database(self):
		conn = sqlite3.connect('gitlog.db')
		c = conn.cursor()
		c.execute("select id from issues where id = %d" % self.id)
		conn.commit()
		if len(c.fetchall()) == 0:
			conn.close()
			return False
		conn.close()
		return True
 
	def save_to_database(self):
            if not self.issue_exists_in_database():
                conn = sqlite3.connect('gitlog.db')
                c = conn.cursor()
                c.execute("insert into issues values(?,?,?,?,?,?,?,?,?,?,?)", (self.id, self.summary, self.description, self.type, self.priority, self.status, self.owner, self.creater, self.is_private, self.create_date, self.update_date))
                conn.commit()
                for patch in self.patch_list:
                    if not patch.patch_exists_in_database():
                        touched_files = ""
                        for file in patch.touched_files:
                            if touched_files == "":
                                touched_files = file
                            else:
                                touched_files = touched_files + " " + file
                        c.execute("insert into patches values(?,?,?,?,?)", (patch.id, self.id, patch.time, touched_files, patch.content))
                        conn.commit()
                conn.close()

	def print(self):
		print('issue id: {}'.format(self.id))
		print('summary: {}'.format(self.summary))
		print('description: {}'.format(self.description))
		print('type: {}'.format(self.type))
		print('priority: {}'.format(self.priority))
		print('status: {}'.format(self.status))
		print('owner: {}'.format(self.owner))
		print('creater: {}'.format(self.creater))
		print('is_private: {}'.format(self.is_private))
		print('create_date: {}'.format(self.create_date))
		print('update_date: {}'.format(self.update_date))
		print('************************')
		print('patch_list: ')
		for patch in self.patch_list:
			print('patch_id: {}'.format(patch.id))
			print('touched_files:')
			for file in patch.touched_files:
				print(file)
			print('***********************')
