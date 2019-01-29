def add(a, b):
	return a+b

def subtract(a, b):
	return a-b

def multiply(a, b):
	return a*b

def divide(a, b):
	return a/b



def simple_calc(a, b, mode):
	mapper = {
		'add' : add(a,b),
		'sub' : subtract(a,b),
		'mult' : multiply(a,b),
		'div' : divide(a,b)
	}
	mode = mapper[mode]
	return mode


