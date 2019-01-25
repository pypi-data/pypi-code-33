import os
import sys

#---------------------------------------------------
#
# Start of Extra Code
#
#---------------------------------------------------

# Extra import to protect dynamic library
import pytransform
from hashlib import md5

MD5SUM_PYTRANSFORM_PY = '46995aee690c412c8e65da764b892562'
MD5SUM_PYTRANSFORM_SO = 'ca202268bbd76ffe7df10c9ef1edcb6c'

# Extra import to check expired date by NTP
from ntplib import NTPClient
from time import mktime, strptime

NTP_SERVER = 'europe.pool.ntp.org'
EXPIRED_DATE = '20190202'

def check_md5sum(filename, expected):
    with open(filename, 'rb') as f:
        if not md5(f.read()).hexdigest() == expected:
            sys.exit(1)

def protect_pytransform():
    # Be sure obfuscated script is not changed
    with open(__file__, 'r') as f:
        lines = f.readlines()
        if not ((len(lines[:4]) == 3) and
                (lines[0].strip() == 'from pytransform import pyarmor_runtime') and
                (lines[1].strip() == 'pyarmor_runtime()') and
                (lines[2].startswith('__pyarmor__'))):
            sys.eixt(1)

    # Be sure `pytransform.py` is not changed
    check_md5sum(pytransform.__file__, MD5SUM_PYTRANSFORM_PY)
    # Be sure `_pytransform.so` is not changed
    check_md5sum(pytransform._pytransform._name, MD5SUM_PYTRANSFORM_SO)

def check_expired_date_by_ntp():
    c = NTPClient()
    response = c.request(NTP_SERVER, version=3)
    if response.tx_time > mktime(strptime(EXPIRED_DATE, '%Y%m%d')):
        sys.exit(1)

protect_pytransform()
check_expired_date_by_ntp()

#---------------------------------------------------
#
# End of Extra Code
#
#---------------------------------------------------

#
# Business Code
#
def hello():
    print('Hello world!')

def sum(a, b):
    return a + b

def main():
    hello()
    print('1 + 1 = %d' % sum(1, 1))

if __name__ == '__main__':
    main()
