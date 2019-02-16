import os
import termtosvg.main as term
import tempfile
import elist.elist as elel
from efdir import fs
#efdir >0.0.14
import pty
import time
from multiprocessing import Process
import estring.estring as eses
#estring > 0.6

def get_last_svg(output_path):
    svgs = fs.walkf(output_path)
    svgs.sort()
    if(svgs.__len__()>1):
        return(svgs[-2])
    else:
        print("something wrong~!")
        return(svgs[-1])

def write2slave(s,slave_fd,**kwargs):
    if("codec" in kwargs):
        codec = kwargs['codec']
    else:
        codec = 'utf-8'
    if("input_speed" in kwargs):
        input_speed = kwargs['input_speed']
    else:
        input_speed = 7
    delay = 1 / input_speed
    for c in s:
        os.write(slave_fd,c.encode(codec))
        time.sleep(delay)
    os.close(slave_fd)


def creat_svg(cmds_str,**kwargs):
    if('bin_path' in kwargs):
        bin_path = kwargs['bin_path']
    else:
        bin_path = '/usr/local/bin/termtosvg'
    if('py' in kwargs):
        py = kwargs['py']
    else:
        py = "python3"
    if('codec' in kwargs):
        codec = kwargs['codec']
    else:
        codec = 'utf-8'
    if('still_frames' in kwargs):
        still_frames = kwargs['still_frames']
    else:
        still_frames = False
    if('screen_size' in kwargs):
        screen_size = kwargs['screen_size']
    else:
        screen_size = "160x50"
    if(still_frames):
        output_path = tempfile.mkdtemp(prefix='termtosvg_')
        input_fileno,slave_fd = eses.str2io(cmds_str,codec=codec)
    else:
        _, output_path = tempfile.mkstemp(prefix='termtosvg_',suffix='.svg')
        input_fileno,slave_fd = pty.openpty()
    if(still_frames):
        print("----")
        print(screen_size)
        print("----")
        term.main([bin_path, output_path,'-c', py, '-s','-g',screen_size],input_fileno,None)
        output_path = get_last_svg(output_path)
        os.close(slave_fd)
        os.close(input_fileno)
    else:
        p_slave = Process(target=write2slave, args=(cmds_str,slave_fd,))
        p_slave.start()
        term.main([bin_path, output_path,'-c', py,'-g',screen_size],input_fileno,None)
        os.close(input_fileno)
        p_slave.join()
    print("final file at "+output_path)
    return(output_path)


def get_screen_size(arr,**kwargs):
    if("rownums" in kwargs):
        rownums = kwargs['rownums']
    else:
        rownums = 30
    if("colnums" in kwargs):
        colnums = kwargs['colnums']
    else:
        colnums = elel.max_length(arr) + 5 
    return(str(colnums)+"x"+str(rownums))

def cmds_arr2str(arr,**kwargs):
    '''
    '''
    if('still_frames' in kwargs):
        still_frames = kwargs['still_frames']
    else:
        still_frames = True
    s = elel.join(arr,"\r")
    s = "\r" + s + "\r"  + "exit()" + "\r"
    return(s)



