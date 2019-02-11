'''to read results:
Date: 18/01/2018

## FUNCTION: This module aims to collect the results to a txt file
then just copy the content of res_full.txt to excel file for computations.

## USAGE: copy these commands

cd ~/deepMG_tf/
python ./utils/read_results/read_res.py -d ibal_2907 -a ~/deepMG_tf/results/  -c ~/deepMG_tf/results/ -e "'*ok*'"
'''
import numpy as np
import os
from optparse import OptionParser

from time import gmtime, strftime
time_text = str(strftime("%Y%m%d_%H%M%S", gmtime()))
#read para from cmd
parser = OptionParser()
parser.add_option("-a", "--folder_parent_results", type="string", default='~/deepMG_tf/results/', help="locate the parent folder where contains results") 
parser.add_option("-b", "--file_listname", type="string", default='res', help="naming the file containing list of files") 
parser.add_option("-c", "--folder_file_listname", type="string", default='~/deepMG_tf/', help="locate folder containing the file of list") 
parser.add_option("-d", "--file_results", type="string", default='i' + time_text, help="locate folder containing the file of list") 
parser.add_option("-e", "--find_patter", type="string", default='*ok*.txt', help="determine the pattern for searching") 
parser.add_option("-l", "--line_file", type="int", default=-1, help="determine the line to get results, if -1 get the last line") 

(options, args) = parser.parse_args()

#function to read the last line of the file
def readfile_tosave(namefile):
    fileHandle = open (namefile,"r" )
    lineList = fileHandle.readlines()
    fileHandle.close()
    
    # if lineList[len(lineList)-2].find("tr_ac_a") <= -1: 
    #     #take a look at "header" at the second-last row, if it does not exist 'tr_ac_a'
    #     #if did not compute std all folds,runs
        
    #     train_acc_all =[] #stores the train accuracies of all folds, all runs
    #     train_auc_all =[] #stores the train auc of all folds, all runs
    #     val_acc_all =[] #stores the validation accuracies of all folds, all runs
    #     val_auc_all =[] #stores the validation auc of all folds, all runs

    #     f=open(namefile,'a')
    #     f.write("\n") #create a new line
    #     title_cols = np.array([['tr_ac_a','sd_ac',"va_ac_a","sd_ac",'tr_au_a','sd_au',"va_au_a","sd_au"]])
    #     np.savetxt(f,title_cols, fmt="%s",delimiter="\t")   

    #     for i in range(0,len(lineList)):
    #         if lineList[i].find('t_acc')>-1:            
    #             f1 = lineList[i+1].find('--')
    #             f2 = lineList[i+1].find('--',f1+1)
    #             f3 = lineList[i+1].find('--',f2+1)
    #             f4 = lineList[i+1].find('--',f3+1)
    #             #print f1,f2,f3, lineList[i+1][0:f1], lineList[i+1][f1+2:f2], lineList[i+1][f2+2:f3],lineList[i+1][f3+2:f4]
    #             #print lineList[i+1][0:f1], lineList[i+1][f1+2:f2], lineList[i+1][f2+2:f3],lineList[i+1][f3+2:f4]
    #             train_acc_all.append(float(lineList[i+1][0:f1]))
    #             val_acc_all.append(float(lineList[i+1][f1+2:f2]))
    #             train_auc_all.append(float(lineList[i+1][f2+2:f3]))
    #             val_auc_all.append(float(lineList[i+1][f3+2:f4]))
        
    #     np.savetxt(f,np.c_[ (
    #             np.mean(train_acc_all, axis=0),
    #             np.std(train_acc_all, axis=0),
    #             np.mean(val_acc_all, axis=0),
    #             np.std(val_acc_all, axis=0),
    #             #len(train_acc_all), #in order to check #folds * #run
    #             #len(val_acc_all),
    #             np.mean(train_auc_all, axis=0),
    #             np.std(train_auc_all, axis=0),
    #             np.mean(val_auc_all, axis=0),
    #             np.std(val_auc_all, axis=0)
    #             #len(train_auc_all),
    #             #len(val_auc_all)
    #             )] , fmt="%s",delimiter="\t")
    #     f.close()

    #     fileHandle = open (namefile,"r" ) #open again after updating
    #     lineList = fileHandle.readlines()
    #     fileHandle.close()
    # else:
    #     print 'result is already available'
    if options.line_file == -1:
        str_save = lineList[len(lineList)-3] + '\t'+ lineList[len(lineList)-1]        
    else:
        str_save = lineList[(options.line_file-1)]
    str_save = str_save.replace("\n","")
    str_save = str_save.replace('\t\t',"\t")
    return str_save

#save file name that finished the experient (contain "ok" in the file name)
#print 'find '+ str(options.folder_parent_results)+' -name "*ok*.txt" > ' + str(options.folder_file_listname) + str(options.file_listname) + '.txt'
#os.system('find  '+ str(options.folder_parent_results)+' -name "*ok*.txt" > ' + str(options.folder_file_listname) + str(options.file_listname) + '.txt')
print 'find '+ str(options.folder_parent_results)+' -name '+ str(options.find_patter)+' > ' + str(options.folder_file_listname) + str(options.file_listname) + '.txt'
os.system('find  '+ str(options.folder_parent_results)+' -name '+ str(options.find_patter)+' > ' + str(options.folder_file_listname) + str(options.file_listname) + '.txt')


#read file containing file name
if options.folder_file_listname=='~/deepMG_tf/':
    file_general = open ( str(options.file_listname) +'.txt',"r" )  
else:
    file_general = open ( str(options.folder_file_listname) + str(options.file_listname) +'.txt',"r" )  
list_filenames = file_general.readlines()

num_files = len(list_filenames)

os.system('cd ' + str(options.folder_parent_results))
temp_res = []
print 'reading....'
#read the last line of each file
for i in range(0,num_files):
    
    print 'file ' + str(i+1) + ' ' + str(list_filenames [i])
    list_filenames[i] = list_filenames[i].strip('\n')
    str_results = str(readfile_tosave(list_filenames[i]))
    str_results = str_results.strip('\t')
    temp_res.append([list_filenames[i],str(str_results)])
#save results of all experiment to file
print temp_res
print 'files read: ' + str (num_files)
f=open( str(options.file_results)+".txt",'w')
np.savetxt(f,temp_res,delimiter='\t', fmt='%s')
f.close()
