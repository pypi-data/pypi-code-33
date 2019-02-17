"""
Quick scripts to deal with argument parsing for command-line tools.
Why not using argparse or click?
We will have a pretty basic but specific use of argparse and I prefer to debug it internally.
argparse is great, until you have a bug. I had hard time debugging some specific argparse. 
Why am I saying all that again?
Anyway.
B.G.
"""
def get_common_default_param():
	"""
	This function returns a dictionnary of common parameter that all command-line tools will need:
	For example, file name, path , ...
	B.G.
	"""
	compam = {}
	compam["file"]="WAWater.bil" # name of our test file.
	compam["path"]="./" # Default is current path
	compam["help"] = False

	return compam

def ingest_param(default_dict, params):
	"""
	Ingest the param and feed the dictionnary.
	params is sys.argv
	B.G.
	"""
	for i in range(1,len(params)):
		arg = str(params[i])
		#Checking if this is a bool activator or a argument-bearing param
		if(len(arg.split("=")) == 1):
			# Bool
			default_dict[arg.lower()] = True
		else:
			# ADD HERE ELIF FOR OTHER CASES, for example comma separated lists of basin key
			default_dict[arg.split("=")[0]] = arg.split("=")[1]

	return default_dict
