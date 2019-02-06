#!/usr/bin/python

import os
import sys

from cmndline import *
from cmndPhase2 import *


def main():
# pwd = os.getcwd()
	inputFiles = sys.argv[1]
	inputType = str(sys.argv[2])
	categories = sys.argv[3]
	indiv_output = sys.argv[4]
	name_for_output = sys.argv[5]
	concat_output = sys.argv[6]
	print("INPUT FILES: "+inputFiles)
	print("INPUT TYPE: "+inputType)
	print("CATEGORIES: "+categories)
	print("INITIAL TOPPGENE OUTPUT PATH: "+indiv_output)
	print("NAME FOR OUTPUT: "+name_for_output)
	print("CONCATENATED RESULTS OUTPUT PATH: "+concat_output)

	cmndline(inputFiles, inputType, categories, indiv_output)
	cmndPhase2(indiv_output, categories, name_for_output, concat_output)


# ./malachite.py "/Users/Gershkowitz/Desktop/malachite/Phase1/LuSc-nuResults/" "ENTREZ" "['Drug','Disease','TFBS']" "Phase1/Phase1output/LuSc/" "LuSc" "/Users/Gershkowitz/Desktop/malachite-final/Phase2/Results/LuSc_Output/"

# os.system("python "+ pwd + "/Phase1/cmndline.py"  +" \""+inputFiles+"\" " +" \""+inputType+"\" "+" \""+categories+"\" "+" \""+indiv_output+"\"")

# os.system("python "+ pwd + "/Phase2/cmndPhase2.py"  +" \""+indiv_output+"\" " +" \""+categories+"\" " +" \""+name_for_output+"\" "+" \""+concat_output+"\"")

if __name__ == "__main__":
    main()