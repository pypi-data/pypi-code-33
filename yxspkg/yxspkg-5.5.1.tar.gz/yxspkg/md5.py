import hashlib,sys
def main(filename = None):
    if filename is None:
        filename = sys.argv[1]
    fp = open(filename,'rb')
    md5 = hashlib.md5()
    md5.update(b'tr')
    md5.update(b'kk')
    md5.update(b'k')
    print(md5.hexdigest())
if __name__=='__main__':
    main()