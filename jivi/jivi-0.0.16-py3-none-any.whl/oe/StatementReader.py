class StatementReader:
		
	@staticmethod
	def assign(a):
		t = {}
		n = 0
		while (n + 2) < len(a):
			t[a[n]] = a[n+2]
			n += 3
		return t