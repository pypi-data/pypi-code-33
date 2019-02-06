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
