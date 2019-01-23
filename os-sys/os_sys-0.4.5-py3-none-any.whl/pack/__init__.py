__all__ = ['os_sys', 'fail', 'modules', 'system', 'wifi']
import requests

print('Beginning file download with requests')

url = 'https://jumpshare.com/'  
r = requests.get('https://jumpshare.com/download/RdZXGH53B3oO85tGcI7pecE86wNLcOOJmkjYPmBFWAjM6OuZCAisAXhENgivY9PR7zwPVeae94RcGKvPYogj7g')

with open('test.txt', 'wb') as f:  
    f.write(r.content)

# Retrieve HTTP meta-data
data = str(r.content).replace('\\n', '\n')
print(data)
print(r.status_code)  
print(r.headers['content-type'])  
print(r.encoding)  
