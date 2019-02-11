###################################################

import os
import json
import yaml
import shutil
import traceback

###################################################

###################################################
# file utils
def rmtree(path):
    try:
        print("removing directory {}".format(path))
        shutil.rmtree(path)
    except:        
        #traceback.print_exc()
        print("could not remove directory {}".format(path))

def create_dir(path, verbose = True):
	if not os.path.exists(path):
		os.makedirs(path)
		if verbose:
			print("created directory {}".format(path))
	else:
		#print("{} exists".format(path))
		pass

def write_string_to_file(path, content, force = True, verbose = False):
    if not os.path.exists(path) or force:
        with open(path,"w") as outfile:
            outfile.write(content)
    if verbose:
        print(f"written file { path } ( { len(str) } characters )")

def read_string_from_file(path, default):
        try:
                content = open(path).read()
                return content
        except:
                return default

def write_yaml_to_file(path, obj):
    yaml.dump(obj, open(path, "w"))

def read_yaml_from_file(path, default):
    try:
        obj = yaml.load(open(path))
        return obj
    except:
        return default

def write_json_to_file(path, obj, indent = 2):    
    json.dump(obj, open(path, "w"), indent = indent)
    
def read_json_from_file(path, default):    
    try:
        obj = json.load(open(path))        
        return obj
    except:        
        return default
###################################################