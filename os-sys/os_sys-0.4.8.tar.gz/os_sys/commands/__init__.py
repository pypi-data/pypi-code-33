__all__ = ['os_sys', 'fail', 'modules', 'system', 'wifi']
import requests





 
def update(argv=None):
    from subprocess import getstatusoutput
    getstatusoutput('pip install --upgrade os_sys')

def download_zip():
    url = 'https://jumpshare.com/'  
    r = requests.get('https://github.com/Matthijs990/os_sys/archive/master.zip')
    print('downloading:')

    with open('test.zip', 'wb') as f:  
        f.write(r.content)
    from time import sleep, time
    now = time()
    def chek(now, duur):
        a = now
        b = time()
        c = b - a
        return c <= duur
    while chek(now, 10):
        print('|', end='')
        sleep(0.1)
    print(end='\n')
    print('done!')

