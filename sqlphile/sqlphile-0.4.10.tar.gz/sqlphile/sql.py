from . import utils
from .q import Q, V, batch, _Q
from .d import toval, D
from copy import deepcopy
from .dbtypes import DB_PGSQL, DB_SQLITE3

class SQL:
	def __init__ (self, template, engine = DB_PGSQL, conn = None):	
		self._template = template		
		self._engine = engine
		self._conn = conn
		self._filters = []
		self._limit = 0
		self._offset = 0
		self._order_by = None
		self._group_by = None
		self._having = None
		self._returning = None		
		self._feed = {}
		self._data = {}
		self._unionables = []
		self._transact = False
	
	def branch (self, conn = None):
		new = self.__class__ (self._template, self._engine, conn or self._conn)
		new._filters = deepcopy (self._filters)
		new._limit = deepcopy (self._limit)
		new._offset = deepcopy (self._offset)
		new._order_by = deepcopy (self._order_by)
		new._group_by = deepcopy (self._group_by)
		new._having = deepcopy (self._having)
		new._returning = deepcopy (self._returning)
		new._feed = deepcopy (self._feed)
		new._data = deepcopy (self._data)		
		return new 
			
	@property
	def query (self):
		return self.as_sql ()
	
	def render (self):
		return self.as_sql ()
		
	def __str__ (self):
		return self.as_sql ()
						
	def __getitem__(self, key):
		key.start and self.offset (key.start)
		if key.stop:
			self.limit (key.stop - (key.start or 0))
		return self
		
	def execute (self):
		object = self._conn.execute (self.query)
		if object:
			return object
		return self
	
	def fetchall (self, *args, **karg):
		return self._conn.fetchall (*args, **karg)
	
	def fetchone (self, *args, **karg):
		return self._conn.fetchone (*args, **karg)
	
	def fetchmany (self, *args, **karg):
		return self._conn.fetchmany (*args, **karg)
	
	def all (self):
		self._filters.append ("1 = 1")
		return self
						
	def exclude (self, *Qs, **filters):
		g = []
		for q in Qs + tuple (batch (**filters)):
			if not q:
				continue
			if not isinstance (q, str):
				q.render (self._engine)
			g.append (str (q))
		self._filters.append ("NOT (" + " AND ".join (g) + ")")		
		return self
	
	def returning	(self, *args):
		self._returning = "RETURNING " + ", ".join (args)
		return self
	
	def filter (self, *Qs, **filters):
		for q in Qs + tuple (batch (**filters)):
			if not q:
				continue
			if not isinstance (q, str):					
				q.render (self._engine)
			self._filters.append (str (q))		
		return self
	
	def having (self, cond):
		self._having = "HAVING " + cond
		return self
		
	def order_by (self, *by):
		self._order_by = utils.make_orders (by)
		return self
	
	def group_by (self, *by):
		self._group_by = utils.make_orders (by, "GROUP")
		return self
		
	def limit (self, val):
		self._limit = "LIMIT {}".format (val)
		return self
	
	def offset (self, val):
		self._offset = "OFFSET {}".format (val)
		return self
				
	def data (self, **karg):
		for k, v in karg.items ():
			if isinstance (v, D):
				self.addD (k, v)			
			else:	
				self._data [k] = toval (v, self._engine)
		return self
		
	def feed (self, **karg):
		for k, v in karg.items ():
			if isinstance (v, D):
				self.addD (k, v)
			else:			
				# Q need str()
				if isinstance (v, _Q) and not v:
					# for ignoring
					v = "1 = 1"					
				elif isinstance (v, (V, _Q)):
					v.render (self._engine)					
				self._feed [k] = str (v)
		return self
	
	def as_sql (self):
		raise NotImplementedError
	
	def union (self, sql, all = False):
		self._unionables.append ((sql, all))
		return self
	
	def tran (self):
		self._transact = True
			
	def union_all (self, sql):
		return self.union (sql, True)	
	
	def maybe_union (self, current):
		n_q = len (self._unionables)
		qs = []
		qs.append (current)		
		for idx, (sql, all) in enumerate (self._unionables):
			qs.append ("UNION{}".format (all and " ALL" or ""))
			qs.append (str (sql))
		r = "\n".join (qs)
		if self._transact:
			return "BEGIN TRANSACTION;\n" + r + ";\nCOMMIT;"
		return r	
		
	
class SQLTemplateRederer (SQL):
	def __call__ (self, **karg):
		return self.feed (**karg)
	
	def addD (self, prefix, D_):
		D_.encode (self._engine)
		self._data [prefix + "_columns"] = D_.columns
		self._data [prefix + "_values"] = D_.values
		self._data [prefix + "_pairs"] = D_.pairs
	
	def as_sql (self):
		data = utils.D (**self._data)
		self._feed.update (self._data)
		
		r = self._template.format (
			_filters = " AND ".join ([f for f in self._filters if f]),
			_limit = self._limit,
			_offset = self._offset,
			_order_by = self._order_by,
			_group_by = self._group_by,
			_having = self._having,
			_columns = data.columns,
			_values = data.values,
			_pairs = data.pairs,
			_returning = self._returning,
			**self._feed
		)
		return self.maybe_union (r)	

class SQLComposer (SQL):	
	def __init__ (self, template, engine = DB_PGSQL, conn = None):	
		SQL.__init__ (self, template, engine, conn)
		self._joins = []
	
	def branch (self, conn = None):
		new = SQL.branch (self, conn)
		new._joins = deepcopy (self._joins)
		return new
				
	def get (self, *columns):
		self._feed ["select"] = ", ".join (columns)
		return self
	
	def _join	(self, jtype, obj, alias, *Qs, **filters):
		_filters = []
		for q in Qs + tuple (batch (**filters)):
			if q:
				q.render (self._engine)
				_filters.append (str (q))				
		_filters = " AND ".join ([f for f in _filters if f])
		if not isinstance (obj, str):
			# SQL
			obj = "({})".format (obj)
		self._joins.append (
			"{} {} AS {} ON {}".format (jtype, obj, alias, _filters)
		)
		return self
	
	def from_	(self, obj, alias, *Qs, **filters):
		return self._join ("FROM", obj, alias, *Qs, **filters)
	
	def join	(self, obj, alias, *Qs, **filters):
		return self._join ("INNER JOIN", obj, alias, *Qs, **filters)
	
	def left_join	(self, obj, alias, *Qs, **filters):
		return self._join ("LEFT OUTER JOIN", obj, alias, *Qs, **filters)
	
	def right_join	(self, obj, alias, *Qs, **filters):
		return self._join ("RIGHT OUTER JOIN", obj, alias, *Qs, **filters)
	
	def full_join	(self, obj, alias, *Qs, **filters):
		return self._join ("FULL OUTER JOIN", obj, alias, *Qs, **filters)
		
	def as_sql (self):
		data = utils.D (**self._data)
		sql = [
			self._template.format (
				_columns =  data.columns, 
				_values = data.values, 
				_pairs = data.pairs,
				**self._feed
			)
		]
		for join in self._joins:
			sql.append (join)
		_filters = [f for f in self._filters if f]
		_filters and sql.append ("WHERE " + " AND ".join (_filters))
		if self._group_by:
			sql.append (self._group_by)
			self._having and sql.append (self._having)
		self._order_by and sql.append (self._order_by)
		self._limit and sql.append (self._limit)
		self._offset and sql.append (self._offset)
		self._returning and sql.append (self._returning)
		r = "\n".join (sql)
		return self.maybe_union (r)
		
