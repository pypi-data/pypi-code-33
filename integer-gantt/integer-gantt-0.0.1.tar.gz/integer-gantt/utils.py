import json

def load(fname):
    """Load a json list from file.
    
    Arguments:
        fname {str} -- Path to the json file
    """
    with open(fname) as jfile:
        data = json.load(jfile)

    return(data)
