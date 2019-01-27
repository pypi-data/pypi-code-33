class StatementReader:
		
	@staticmethod
	def assign(a):
		t = {}
		n = 0
		while (n + 2) < len(a):
			t[a[n]] = a[n+2]
			n += 3
		return t

class ArHelper:

		
	@staticmethod
	def same_rest(a,b):
		try:
			for i,x in enumerate(b):
				if a[i] != x: return 0
			return a[len(b):]
		except:
			return 0
	@staticmethod
	def same(a,b):
		try:
			for i,x in enumerate(b):
				if a[i] != x: return 0
			return 1
		except:
			return 0
			
	@staticmethod
	def has(a,b):
		for i,x in enumerate(a):
			if x == b[0]:
				if same(a[i:],b):
					return 1
					
	@staticmethod
	def strip_until(a,b):
		if not isinstance(b,list): b = [b]
		for i,x in enumerate(a):
			if x == b[0] and ArHelper.same(a[i:],b):
				return a[i + len(b):]
					
	@staticmethod
	def strip_property(a,prop):
		for i,x in enumerate(a):
			if x == prop:
				rv = a[i+1]
				a = a[:i] + a[i+2:]
				return (a,rv)