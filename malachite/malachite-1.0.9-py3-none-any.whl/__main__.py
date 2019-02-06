#!/usr/bin/python

import os
import sys
import re
import ast
# from cmndline import *
# from cmndPhase2 import *
import getAllFiles

def cmndPhase2(path_in, categor, name, path_out):
	# path_in = str(sys.argv[1])

	list_of_files = getFiles(path_in)
	if '.DS_Store' in list_of_files:
	    list_of_files.remove('.DS_Store')

	numof = len(list_of_files)

	# CATEGORY
	category = ast.literal_eval(categor)

	# OUTPUT PATH NAME
	name = str(name)

	# OUTPUT PATH
	path_out = str(path_out)

	toppDict = {"GeneOntologyMolecularFunction": "GO: Molecular Function", "GeneOntologyBiologicalProcess": "GO: Biological Process", "GeneOntologyCellularComponent":"GO: Cellular Component", "HumanPheno":"Human Phenotype","MousePheno":"Mouse Phenotype","Domain":"Domain", "Pathway":"Pathway","Pubmed":"Pubmed","Interaction":"Interaction","Cytoband":"Cytoband","TFBS":"Transcription Factor Binding Site","GeneFamily":"Gene Family","Coexpression":"Coexpression","CoexpressionAtlas":"Coexpression Atlas","Computational":"Computational","MicroRNA":"MicroRNA","Drug":"Drug","Disease":"Disease"}

	print("currently running part (1/2), please wait.")
	dcount(path_in, numof, list_of_files, name, path_out, category, toppDict)
	print("currently running part (2/2), please wait.")
	dcount2(path_in, numof, list_of_files, name, path_out, category, toppDict)
	print("done.")

def cmndline(path_in, input_type, category, output_name):
	# path_in = sys.argv[1]

	list_of_files = getFiles(path_in)
	if '.DS_Store' in list_of_files:
	    list_of_files.remove('.DS_Store')

	numof = len(list_of_files)

	# input_type = sys.argv[2]
	# category = sys.argv[3]
	pval_method = 'HYPER_PMF'
	# output_name = str(sys.argv[4])

	topgen(path_in, numof, list_of_files, input_type, category, pval_method, output_name)


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
