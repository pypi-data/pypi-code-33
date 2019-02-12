import os

from defaults import *


from utils import *

from creat_metrics import run_creat_metrics
from filter_bias import run_filter_bias

def run(args,parser):

    mode = args.mode
    
    create_dirs([args.outdir])    
        
    if mode=="CreatMetrics":
        run_creat_metrics(args)
    elif mode == "FilterBias":
        for m in args.type:
            ms = m.split("/")
            assert len(ms) == 2 and len(m) == 3, "Illegal --artifactmodes strings: %s" %m
        
        run_filter_bias(args)
        return os.EX_USAGE
    return os.EX_OK


