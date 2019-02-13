from data import SortData
from bubblesort import BubbleSort
from bucketsort import BucketSort

import argparse
parser=argparse.ArgumentParser(description="Sort Visulization")
parser.add_argument('-l','--length',type=int,default=64)
parser.add_argument('-i','--interval',type=int,default=1)
parser.add_argument('-t','--sort-type',type=str,default='BubbleSort', 
                                    choices=["BubbleSort", "BucketSort"])
parser.add_argument('-r','--resample', action='store_true')
parser.add_argument('-s','--sparse', action='store_true')
parser.add_argument('-rc','--record', action='store_true')
parser.add_argument('-c','--color-theme',type=str,default='blue', 
                                    choices=["blue", "green"])
args=parser.parse_args()

def main():
    MAXLENGTH=1024
    Length=args.length if args.length<MAXLENGTH else MAXLENGTH
    Interval=args.interval
    SortType=args.sort_type
    Resampling=args.resample
    Sparse=args.sparse
    Record=args.record
    ColorTheme=args.color_theme
    try:
        SortMethod=eval(SortType)
    except:
        print("Sort Type Not Found! Please Check if %s Exists or Not!"%SortType)
        exit()

    sv=SortData(Length, time_interval=Interval, sort_title=SortType, is_resampling=Resampling, is_sparse=Sparse, record=Record, color_theme=ColorTheme)
    sv.Visualize()
    sv.StartTimer()
    SortMethod(sv)
    sv.StopTimer()
    sv.SetTimeInterval(0)
    sv.Visualize()

if __name__ == "__main__":
    main()