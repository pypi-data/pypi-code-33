
def to_octal(string, prefix = "\\"):
    """Returns the octal representation of a string"""
    octal = ""
    
    for b in bytearray(string):
        octal = octal + "{}{:o}".format(prefix, b)
        
    return octal