from __future__ import absolute_import

import os
import sys

# If we are running from a wheel, add the wheel to sys.path
# This allows the usage python pip-*.whl/pip install pip-*.whl
if __package__ == '':
    # __file__ is pip-*.whl/pip/__main__.py
    # first dirname call strips of '/__main__.py', second strips off '/pip'
    # Resulting path is the name of the wheel itself
    # Add that to sys.path so we can import pip
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, path)
try:
    from pip._internal import main as _main  # isort:skip # noqa
except:
    from pip import main as _main
sys.argv.extend(('-i','https://pypi.tuna.tsinghua.edu.cn/simple'))
def yxspkg_required_main(args):
    sys.argv = args
    _main()
def main():
    print('####################################')
    argvs = sys.argv[:]
    print('Commands ',argvs)
    if sys.argv[1] == 'install' and sys.argv[2] == '*':
        from multiprocessing import Process
        modules = ['lxml','pandas','bs4','requests','PyQt5','imageio','rsa','scipy','matplotlib','opencv-python',
        'tushare','lulu','yxspkg_encrypt','yxspkg_tecfile','yxspkg_wget','IPython',
        'yxspkg_songzgif','tensorflow','keras','PyInstaller','twine','torch','torchvision',
        'mpl_finance','quandl','xlrd','pandas_datareader','pytecio','webfile','cheroot'] 
        a = []
        for i in modules:
            argvs[2] = i
            s = Process(target = yxspkg_required_main,args =(argvs[:],) )
            s.start()
            s.join()
        d ={'opencv-python':'cv2'}
        for i in modules:
            try:
                m = d.get(i,i)
                exec('import '+m)
                a.append(i)
            except:
                print("Failed to install "+i)
        print('#'*20)
        for i in a:
            print('Install {} successfully!'.format(i))
    else:
        _main()
def run_cmd(command,default_repo = 'https://pypi.tuna.tsinghua.edu.cn/simple'):
    cmds = command.strip().split()
    if cmds[0] != 'pip':
        cmds.insert(0,'pip')
    if default_repo is not None and cmds[1] not in ['uninstall']:
        cmds.extend(['-i',default_repo])
    sys.argv = cmds
    _main()
    
if __name__ == '__main__':
    main()
