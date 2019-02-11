"""
================================================================================

================================================================================
Author: Van-Kha Nguyen
References: deepmg package
====================================================================================================================
"""

from deepmg import experiment
options, args = experiment.para_cmd()

#check if read parameters from configuration file
import os
if options.config_file <> '':
    if os.path.isfile(options.config_file):
        experiment.para_config_file(options)
        #print options
    else:
        print 'config file does not exist!!!'
        exit()
else:
    experiment.get_default_value(options)

#convert options which type numeric
experiment.string_to_numeric(options)
#check whether parameters all valid
experiment.validation_para(options)


# step 3: select mode of running (predict/learn/vis/config):  #####  
if __name__ == "__main__":   
    print 'the package is running!!'
    if options.type_run in ['vis','visual']: #if only visualize
        experiment.deepmg_visual(options,args)
    elif options.type_run in ['learn','config']:         #if learning

        if options.test_size in [0,1]:   #if use cross-validation
            time_text = experiment.run_kfold_deepmg(options,args)            
        else: #if set the size of test set, so use holdout validation
            time_text = experiment.run_holdout_deepmg(options,args)    
               
        if options.save_entire_w in ['y'] or options.test_exte in ['y']:        #if get weights on whole dataset  
            experiment.run_holdout_deepmg(options,args, special_usecase = 'train_test_whole',txt_time_pre=time_text)  

    elif options.type_run in ['predict']: #if predict or test from a pretrained model
        experiment.run_holdout_deepmg(options,args, special_usecase = 'predict')   
 