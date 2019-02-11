import sys
from topgen import *
from getAllFiles import *

print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))
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
