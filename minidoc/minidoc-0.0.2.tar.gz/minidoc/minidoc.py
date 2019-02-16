from minidoc import svg
from minidoc import tst
from efdir import fs
import shutil
import os

def creat_one_svg(k,v,i=None,**kwargs):
    if("dst_dir" in kwargs):
        dst_dir = kwargs['dst_dir']
    else:
        dst_dir = "./images"
    screen_size = svg.get_screen_size(v,**kwargs)
    kwargs['screen_size'] = screen_size
    cmds_str = svg.cmds_arr2str(v,**kwargs)
    output_path = svg.creat_svg(cmds_str,**kwargs)
    #name = tst.get_svg_name(k) + "." + str(i) + ".svg"
    name = tst.get_svg_name(k) + ".svg"
    dst = os.path.join(dst_dir,name)
    shutil.move(output_path,dst)
    return(dst)


#still_frames
#rownums
#colnums

def creat_svgs(kl,vl,**kwargs):
    if("dst_dir" in kwargs):
        dst_dir = kwargs['dst_dir']
    else:
        dst_dir = "./images"
    fs.mkdir(dst_dir)
    arr = []
    for i in range(kl.__len__()):
        k = kl[i]
        v = vl[i]
        dst = creat_one_svg(k,v,i=i,**kwargs)
        arr.append(dst)
    return(arr)


####
####





