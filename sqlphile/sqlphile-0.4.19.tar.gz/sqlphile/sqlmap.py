from . import sql
import os
import re

class SQLMap:
	def __init__ (self, map = None, auto_reload = False, engine = "postgresql", conn = None, sqls = None):
		self._map = map
		self._auto_reload = auto_reload
		self._engine = engine
		self._conn = conn
		self._version = "1.0"
		self._sqls = sqls or {}
		self._last_modifed = 0
		if self._map:
			self._read_from_file ()
	
	def __getattr__ (self, name):		
		self._reloaderble () and self._read_from_file ()
		if self._sqls.get (name) is None:
			raise AttributeError ("SQL template '{}' not found".format (name))
		return sql.SQLTemplateRederer (self._sqls.get (name), self._engine, self._conn)
		
	def _reloaderble (self):
		return self._map and self._auto_reload and self._last_modifed != os.path.getmtime (self._map)
	
	def __resolve (self, table, alias):
		return alias and (table + " AS " + alias) or table
	
	def new (self, conn):	
		return SQLMap (None, self._auto_reload, conn.dbtype, conn, sqls = self._sqls)
	
	def execute (self, *args, **kargs):
		return self._conn.execute (*args, **kargs)
			
	def from_string (self, template):
		return sql.SQLTemplateRederer (template, self._engine, self._conn)
	
	def _render_table (self, table):
		if isinstance (table, str):
			return table
		return "({})".format (table)
			
	def insert (self, table, alias = None):
		return sql.SQLComposer ("INSERT INTO " + self.__resolve (self._render_table (table), alias) + " ({_columns}) VALUES ({_values})", self._engine, self._conn)
		
	def update (self, table, alias = None):		
		return sql.SQLComposer ("UPDATE " + self.__resolve (self._render_table (table), alias) + " SET {_pairs}", self._engine, self._conn)
		
	def select (self, table, alias = None):
		return sql.SQLComposer ("SELECT {select} FROM " + self.__resolve (self._render_table (table), alias), self._engine, self._conn).feed (select = "*")
		
	def delete (self, table, alias = None):
		return sql.SQLComposer ("DELETE FROM " + self.__resolve (self._render_table (table), alias), self._engine, self._conn)
		
	def _read_from_file (self):
		self._last_modifed = os.path.getmtime (self._map)
		with open (self._map) as f:
			self._read_from_string (f.read ())
	
	RX_NAME	= re.compile ("\sname\s*=\s*['\"](.+?)['\"]")
	RX_VERSION	= re.compile ("\sversion\s*=\s*['\"](.+?)['\"]")
	def _read_from_string (self, data):
		self._sqls = {}
		
		current_name = None
		current_data = []
		for line in data.split ("\n"):
			if not line.strip ():
				continue
			
			if line.startswith ("<sqlmap "):
				m = self.RX_VERSION.search (line)
				if m:					
					self._version = m.group (1)
				
			elif line.startswith ("</sql>"):
				if not current_name:
					raise ValueError ("unexpected end tag </sql>")
				self._sqls [current_name] = "\n".join (current_data)
				current_name, current_data = None, []				 
			
			elif line.startswith ("<sql "):
				m = self.RX_NAME.search (line)
				if not m:
					raise ValueError ("name attribute required")
				current_name = m.group (1)
			
			elif current_name:
				current_data.append (line.strip ())

