
def lFormat(string, nCol=60):
    return ''.join([x+'\n' if (i+1)%nCol == 0 else x for i,x in enumerate(string) ])

        