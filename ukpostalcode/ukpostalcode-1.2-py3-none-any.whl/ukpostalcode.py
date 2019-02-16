import re
import urllib.request, json 


__newpc = ""

def _get_from_url(url):
    res = ''
    with urllib.request.urlopen(url) as d:
        res = json.loads(d.read().decode())
    return res

def isValid(pc):
    """
    @return True or False
    isvalid Function match given postal code 'pc' using REGEX pattern
    if code is Valid return True, else return False.
    Note: isValid will try format given postal code even it contain spaces or wrong inserted.
    REGEX is NOT tested for Special postal codes used in 
    Anguilla, Bermuda, Cayman and British Virgin Insland
    """
    global __newpc
    res = False
    pattern = re.compile(r'(\b[A-Z]{1,2}[0-9][A-Z0-9]? [0-9][ABD-HJLNP-UW-Z]{2}\b)')
    if ' ' in pc:
        joinpc = pc.replace(" ", "").upper()
        try:
            if len(joinpc) == 7:
                fstchs = joinpc[:4]
                lstchs = joinpc[4:]
            if len(joinpc) == 6:
                fstchs = joinpc[:3]
                lstchs = joinpc[3:]
            if len(joinpc) == 5:
                fstchs = joinpc[:2]
                lstchs = joinpc[2:]
            
            __newpc = fstchs+" "+lstchs
            match = pattern.search(__newpc)
                
        except (AttributeError, UnboundLocalError):
            res = False

    else:
        joinpc = pc.upper()
        try:  
            if len(joinpc) == 7:
                fstchs = joinpc[:4]
                lstchs = joinpc[4:]
            if len(joinpc) == 6:
                fstchs = joinpc[:3]
                lstchs = joinpc[3:]
            if len(joinpc) == 5:
                fstchs = joinpc[:2]
                lstchs = joinpc[2:]
                
            __newpc = fstchs+" "+lstchs
            match = pattern.search(__newpc)
        except (AttributeError, UnboundLocalError):
            res = False
        
    try:
        matchpc = match.group(1)
    
        if matchpc:
            res = True
        else:
            return res
    except (AttributeError, UnboundLocalError):
        res = False

    return res

def format_postcode(pc):
    """
    @return postal code or None
    format_postcode function calls isValid() function and return changed global __newpc
    (by valid function). If postalcode is Wrong a exception in isValid is called. 
    """
    if isValid(pc):
        return __newpc
    else:
        return None

def detailed(pc):
    """
    @return json
    validate, format(if needed) and then get from http://api.getthedata.com/postcode/
    """
    d = format_postcode(pc)
    if d:
        res = _get_from_url('http://api.getthedata.com/postcode/%s'%(d.replace(' ', '+')) )
    else:
        res = None
    return res

