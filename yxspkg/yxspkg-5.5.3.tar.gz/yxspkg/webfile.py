import sys
sys.path.pop(0)
from webfile.webfile import *

def main():
    x=getip()
    print('本机ip：{ip}'.format(ip=x))
    website()
if __name__ == '__main__': 
    main()
