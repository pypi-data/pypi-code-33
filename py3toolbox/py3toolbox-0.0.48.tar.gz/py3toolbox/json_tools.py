import json
#import .fs_tools as fs_tools

def is_json(json_text):
  try:
    json_object = json.loads(json_text)
  except ValueError:
    return False
  return True    
  

def load_json(json_file):
  with open(json_file , encoding='utf-8') as json_fh:
    config = json.load(json_fh)
  return config    


def pretty_json(json_text) :
  return (json.dumps(json.loads(json_text), sort_keys=True, indent=2))
  
  
if __name__ == "__main__": 
  pass