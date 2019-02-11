'''to read results:
Author: Nguyen Thanh Hai
Date: 18/01/2018

## FUNCTION: This module aims to collect the complete results of the experiments including all folds (training and testing by ACC, AUC, MCC)
    a file contains names of file to extract results of folds shoud be already available (parameters: -b)

## USAGE: copy these commands as an example
cd ~/deepMG_tf/
python ./utils/read_results/filtered_metrics.py -a ~/deepMG_tf/results/  -c ~/deepMG_tf/results/ -d mc_1704
'''
import numpy as np
import os
import pandas as pd
from optparse import OptionParser
from time import gmtime, strftime
#read para from cmd
time_text = str(strftime("%Y%m%d_%H%M%S", gmtime()))

parser = OptionParser()
parser.add_option("-a", "--folder_parent_results", type="string", default='~/deepMG_tf/results/', help="locate the parent folder where contains results") 
parser.add_option("-b", "--file_listname", type="string", default='res_filtered', help="locate the file contains desired information to explore all folds") 
parser.add_option("-c", "--folder_file_listname", type="string", default='~/deepMG_tf/', help="locate folder containing the file of list") 
parser.add_option("-d", "--output", type="string", default=str('filtered') + str(time_text), help="naming the output file") 
parser.add_option("-e", "--extension", type="string", default='txt', help="extension for input") 

(options, args) = parser.parse_args()

#function to read the last line of the file
def readfile_tosave(namefile, file_to_save):
    fileHandle = open (namefile,"r" )
    lineList = fileHandle.readlines()
    fileHandle.close()
    #print namefile
    f=open(file_to_save,'a')
    index_fold = 1
    for i in range(0,len(lineList)):
        if lineList[i].find('t_acc')>-1:            
            f1 = lineList[i+1].find('--')
            f2 = lineList[i+1].find('--',f1+1)
            f3 = lineList[i+1].find('--',f2+1)
            f4 = lineList[i+1].find('--',f3+1)
            f5 = lineList[i+1].find('--',f4+1)
            #print f1,f2,f3, lineList[i+1][0:f1], lineList[i+1][f1+2:f2], lineList[i+1][f2+2:f3],lineList[i+1][f3+2:f4]
            #print lineList[i+1][0:f1], lineList[i+1][f1+2:f2], lineList[i+1][f2+2:f3],lineList[i+1][f3+2:f4]
            
            #title_cols = np.array([[index_fold,float(lineList[i+1][0:f1]),float(lineList[i+1][f1+2:f2]),
            #    float(lineList[i+1][f2+2:f3]),float(lineList[i+1][f3+2:f4]),float(lineList[i+1][f4+2:f5]),namefile]])
            
            title_cols = np.array([[index_fold,(lineList[i+1][0:f1]),(lineList[i+1][f1+2:f2]),
                (lineList[i+1][f2+2:f3]),(lineList[i+1][f3+2:f4]),(lineList[i+1][f4+2:f5]),namefile]])
            
            np.savetxt(f,title_cols, fmt="%s",delimiter="\t")  
            # np.savetxt(f,np.c_[ (
                    
            #         index_fold,
            #         float(lineList[i+1][0:f1]) , #train_acc_all
            #         float(lineList[i+1][f1+2:f2]) , #val_acc_all
            #         float(lineList[i+1][f2+2:f3]) , #train_auc_all
            #         float(lineList[i+1][f3+2:f4]) , #val_auc_all
            #         float(lineList[i+1][f4+2:f5]) ,#val_mmc_all
            #         'hdhdhdh'
            #     )] , fmt="%s",delimiter="\t")
            index_fold = index_fold + 1 
        
    
    f.close()

   

#read file containing file name
if options.folder_file_listname=='~/deepMG_tf/':
    if options.extension == 'txt':
        file_general = open ( str(options.file_listname) +'.txt',"r" )  
    elif options.extension == 'csv':
        file_general = pd.read_csv(str(options.file_listname)  + '.csv', header = None)
        #file_general = file_general.values
        file_general = file_general.iloc[:,0] 
    else:
        print 'extension is not supported'
        
else:
    #file_general = open ( str(options.folder_file_listname) + str(options.file_listname) +'.txt',"r" )  
    if options.extension == 'txt':
        file_general = open ( str(options.folder_file_listname) +'.txt',"r" )  
    elif options.extension == 'csv':
        file_general = pd.read_csv(str(options.folder_file_listname) + '.csv', header = None)
        #file_general = file_general.values
        file_general = file_general.iloc[:,0] 
    else:
        print 'extension is not supported'

if options.extension == 'txt':   
    list_filenames = file_general.readlines()
elif options.extension == 'csv':
    list_filenames = file_general
else:
    print 'extension is not supported'
    exit()

#print list_filenames

num_files = len(list_filenames)

os.system('cd ' + str(options.folder_parent_results))
temp_res = []
print 'reading....'
#read the last line of each file
f=open(options.output,'w')   
title_cols = np.array([['id_fold','train_acc',"val_acc","train_auc",'val_auc','val_mcc',"file"]])
np.savetxt(f,title_cols, fmt="%s",delimiter="\t")  
f.close() 

for i in range(0,num_files):    
    print 'file ' + str(i+1) + ' ' + str(list_filenames [i])
    if options.extension == 'txt':  
        list_filenames[i] = list_filenames[i].strip('\n')   
    else:
        list_filenames[i] = str(list_filenames[i])
    print list_filenames[i]
    
    readfile_tosave(namefile = list_filenames[i], file_to_save=options.output)
   
