import sys
import re
import ast
from drugCounter import *
from drugCounter2 import *
from getAllFiles import *

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
