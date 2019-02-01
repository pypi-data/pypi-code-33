import time
import sys
import os
from pynput.keyboard import Controller
from os import path
global_command = [0]
def WriteCommand(s,terminal=False):
    pdir=path.abspath(' ')[:-2]
    global_command[0] = s
def LaTeX(s):
    print('LaTeX')
    os.system('/usr/local/texlive/2015/bin/x86_64-linux/xelatex '+s)
    com='/usr/bin/evince '+path.splitext(s)[0]+'.pdf '
    WriteCommand(com)
def Fortran(s):
    print('Fortran')
    Cpp(s,g='gfortran')
def C(s):
    print('C')
    Cpp(s,g='g++')
def Asm(s):
    filename=s[0]
    t=path.splitext(filename)[0]
    os.system('nasm -f elf64 %s -o %s.o' % (filename,t))
    os.system('ld -s -o %s.out %s.o' % (t,t))
    WriteCommand('./%s.out' % (path.split(t)[1],),terminal=True)
def Cpp(comt,g='g++'):
    if g=='g++':print('C++')
    s=comt[0]
    if g in ['gcc','g++']:bs=' -o3 '
    else:bs=' '
    com=g+bs+s+' -o '+path.splitext(s)[0]+'.out'
    os.system(com)
    filex=path.split(path.splitext(s)[0]+'.out')[1]
    com='./'+filex
    print(com)
    WriteCommand(com,terminal=True)
def Python(c1,c2):
    print(c2)
    pdir=path.abspath(' ')
    com=c2+' '+c1
    WriteCommand(com,terminal=True)
def Make(f):
    print('make')
    WriteCommand('make',True)
def main(com):
    default='python3'
    if com[1]=='LaTeX':LaTeX(com[0])
    elif com[1] in ['python','python3' ,'pypy','pypy3','ipython','ipython3']:Python(com[0],com[1])
    elif com[1]=='Fortran':Fortran(com)
    elif com[1]=='cpp':Cpp(com)
    elif com[1]=='c':C(com)
    else:
        x=path.splitext(com[0])[1]
        if x in ['','.py']:
            s=open(com[0],'r').readline().strip()
            s=s.split()
            if len(s)>=2:s=s[-1]
            else:s=default
            if s.lower().find('py')!=-1:Python(com[0],s.lower())
            elif x=='' and path.split(com[0])[-1].lower()=='makefile':Make(com[0])
            else:Python(com[0],default)
        if x.lower() in ['.tex']:LaTeX(com[0])
        if x.lower() in ['.gf','.f','.f90']:Fortran(com)
        if x.lower() in ['.c']:C(com)
        if x.lower() in ['.cpp']:Cpp(com)
        if x.lower() in ['.asm']:Asm(com)

def run_ter(s):
    os.system(sys.argv[1])
    time.sleep(float(sys.argv[2]))
    keyboard = Controller()
    keyboard.type(s)
    keyboard.type('\n')
if __name__=='__main__':
    main([sys.argv[3],''])
    run_ter(global_command[0])