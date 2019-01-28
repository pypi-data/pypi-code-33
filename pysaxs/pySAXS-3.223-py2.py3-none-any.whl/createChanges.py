import os
import codecs
import pySAXS
import sys
filename="CHANGELOG.txt"
#get the changelog from mercurial command 
p=pySAXS.__path__[0]
p0=os.getcwd()
p=os.getcwd()+os.sep+".hg"
os.chdir(p)

l=os.popen('hg log').readlines()

#transform the output in a python list
d1={}
l2=[]
#--list of dictionnary
for st in l:
    if st=='\n':
        l2.append(d1)
        d1={}
    else:
        st=st.strip('\n')
        st=st.strip()
        pos=st.index(':')
        d1[st[:pos]]=st[pos+1:].strip()

#write to file
f=open(p0+os.sep+filename,mode='w')
for d in l2:
    version=d['changeset']
    pos=version.index(':')
    version=version[:pos]
    st=version+'\t'+\
        d['date']+'\t'+\
        d['user']+'\t'+\
        d['summary']+'\n'
    if sys.version_info.major>=3:
        f.write(st)
    else:    
        f.write(st.decode(encoding='utf8',errors='ignore'))
    print(st)
f.close()


