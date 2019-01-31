
from iwiki import *

import requests

def search_existance(word, lang='en'):
    try:
        r = requests.get(f"https://{lang}.wikipedia.org/wiki/{word}")
    except Exception as e:
        return None
    else:
        if r.status_code == 200: return True
        elif r.status_code == 404: return False
        else:
            print(f"\n\n r.status_code : {r.status_code}")
            return None
