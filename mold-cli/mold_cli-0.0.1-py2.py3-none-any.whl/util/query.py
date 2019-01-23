''' 
defines a function name query for safly accsting collections
'''

def query(collection, key):
    try:
        return collection[key]
    except:
        return None

