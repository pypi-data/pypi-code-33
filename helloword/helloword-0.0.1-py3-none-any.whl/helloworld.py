def say_hello(name=None):
	if name is None:
		return "Hello, World!"
	else: 
		return f"Hello, {name}!"

print(say_hello(name='Sara'))

