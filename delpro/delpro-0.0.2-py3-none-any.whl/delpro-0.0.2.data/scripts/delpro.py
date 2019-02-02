"""
Created on Fri Feb  1 18:41:35 2019

@author: saurabh
"""

import requests, zipfile, io, os

def main():
    url = 'https://github.com/sb6998/delpro/archive/master.zip'
    r = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall()
    l = []
    for x in z.NameToInfo:
        l.append(x)
    d = str(l[0])+"/Otree"
    os.system("pip install otree")
    os.chdir(d)
    os.system("otree devserver")
    
if __name__== '__main__':
    main()