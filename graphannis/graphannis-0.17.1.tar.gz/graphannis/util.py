import networkx as nx
import sys, re

def salt_uri_from_match(match):
    if isinstance(match, str):
        elements = re.split('::', match, 3)
        if len(elements) == 3:
            return elements[2]
        elif len(elements) == 2:
            return elements[1]
        else:
            return elements[0]
    elif isinstance(match, list):
        result = []
        for m in match:
            result.append(salt_uri_from_match(m))
        return result
    else:
        return None
