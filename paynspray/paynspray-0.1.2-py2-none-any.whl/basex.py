import base64, re

def encode_base64(string, delim = ''):
    return re.sub(r'\s+', delim, (base64.b64encode(str(string)) + "\n"))
    
def decode_base64(string):
    return base64.b64decode(str(string))
    
def encode_base64url(string, delim = ''):
    return re.sub('=', '', encode_base64(string, delim).replace('+/', '-_'))
    
def decode_base64url(string):
    return decode_base64(re.sub(r'[^a-zA-Z0-9_\-]', '', string).replace('-_', '+/'))