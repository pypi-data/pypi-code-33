# Name: Tiffany Nguyen
# Date: 2.12.19
# File: Proteomics.py (kfwx)

# Note: Using Python 2.7

# 1) Place the raw data files (.txt) to be analyzed in a folder with this Python script.
# 2) Open the command line
# 3) Navigate to the folder 
#	  e.g. if folder path is users/data_analysis, then type the command "cd users/data_analysis" without quotations
# 4) Type command "python Proteomics.py" without quotations to run

import matplotlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('seaborn-darkgrid')
import seaborn as sns
import scipy.stats as stats
import glob
import os
import datetime

def main():
	#get_input()
	print('-----------------------------------------------')
	print("Loading...")

	# Retrieves all .txt files in the current working directory
	root = os.getcwd()
	path = root + '/*.txt'
	files = glob.glob(path)   

	file_num = 1

	if (os.path.isdir(root + '/output') == False):
			os.makedirs('output')

	# Loops through every .txt file found
	for name in files:
		print('Analyzing file ' + str(file_num) + '...')

		# Stores file name
		filename = name.split('/')[-1]

		# Removes file type from filename
		shortened_filename = filename.split('.')[0]

		output_dir = root +'/output/' + shortened_filename

		if (os.path.isdir(output_dir) == False):
			os.chdir(root + '/output')
			os.makedirs(shortened_filename)
			os.chdir(root)

		# Creates .xlsx file to output analyzed data to
		writer = pd.ExcelWriter(shortened_filename + '.xlsx')

		# ----DATA READ-IN----

		#print(filename) #debug

		# Reads in the data from the csv and stores it as a dataframe
		raw = pd.read_csv(filename, sep='\t', header=0, engine='python')

        os.chdir(output_dir)
        raw.to_excel(writer, ('Raw Data'))

        high = raw[raw['Protein FDR Confidence: Combined'] == 'High']

        high.to_excel(writer, ('High Confidence Data'))

        print('Raw', len(raw.index))
        print('High', len(high.index))

        # Saves excel file and moves on to next file to be analyzed if there is one
        writer.save()
        file_num += 1
        os.chdir(root)

	print('Analysis complete')
	print('-----------------------------------------------')

main()