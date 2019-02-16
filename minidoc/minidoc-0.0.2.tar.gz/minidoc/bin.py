from minidoc import minidoc
from minidoc import tst
import argparse
from efdir import fs

parser = argparse.ArgumentParser()
parser.add_argument('-tst','--test_file', default="code.tst.py",help=".tst.py file name")
parser.add_argument('-codec','--codec', default="utf-8",help=".tst.py file codec")
parser.add_argument('-still','--still_frames', default="True",help="generate screen shot")
parser.add_argument('-rows','--rownums', default="30",help="screen height")
parser.add_argument('-dst','--dst_dir', default="./images",help="destination svg dir")
parser.add_argument('-title','--title', default="Usage",help="parent title")
parser.add_argument('-tbot','--title_bot', default="=",help="parent title bottom char")
parser.add_argument('-ebot','--entry_bot', default="-",help="entry title bottom char")


def boolize(s):
    s = s.lower()
    if(s=="true"):
        return(True)
    elif(s=="false"):
        return(False)
    else:
        return(False)

args = parser.parse_args()
still_frames = boolize(args.still_frames)


def main():
    kl,vl = tst.tst2kvlist(fn=args.test_file,codec=args.codec)
    minidoc.creat_svgs(kl,vl,still_frames=still_frames,rownums=int(args.rownums),dst_dir=args.dst_dir)
    rst_str = tst.creat_rst(kl,vl,title=args.title,title_bot=args.title_bot,entry_bot=args.entry_bot)
    fs.wfile(args.title+".rst",rst_str,codec=args.codec)
