import codecs
import sys, os
def getversionMercurial():
    __subversion__='0'
    try:
        import os
        try:
            p=__path__[0]
        except:
            p=os.path.curdir
        filename=p+os.sep+"/CHANGELOG.txt"
        if(os.path.exists(filename)):
            f=codecs.open(filename,mode='r',encoding='utf8',errors='ignore')
            l=f.readline()
            s=l.split()
            return s[0]
        else:
            return __subversion__
    except:
        return __subversion__

def getMonthYear():
    try:
        import calendar
        import time
        month= calendar.month_name[time.localtime().tm_mon]
        year=time.localtime().tm_year
        return month+str(year)
    except:
        return ''

__version__ = '3.'
#__subversion__='0'
__subversion__=getversionMercurial()#+getMonthYear()
__author__='CEA - IRAMIS - LIONS'
__author_email__='olivier.tache@cea.fr'
__url__='http://iramis.cea.fr/nimbe/lions/'

UI_PATH=os.path.dirname(os.path.abspath(__file__))+os.sep+'guisaxs'+os.sep+'ui'  +os.sep  
ICON_PATH=os.path.dirname(os.path.abspath(__file__))+os.sep+'guisaxs'+os.sep+'images'+os.sep 

