def func(a):
	for b in a:
		if isinstance(b, list):
			func(b)
		else:
			print(b)