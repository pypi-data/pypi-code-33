'''
Created on 19 déc. 2018

@author: jeanluc
'''
import sys, os
from collections import OrderedDict
import numpy as np
from concurrent.futures import as_completed, ProcessPoolExecutor as PoolExec

from ...nntoolbox.configparsertoolbox import defaultedConfigParser
from ...nntoolbox.progress import Progress_tqdm  #FanWait, 
from ...nntoolbox.constants import nobarverb, NO_PARALLEL_TEST, USE_NO_LIB
from ...nntoolbox.utils import doNothing, ReverseConfigString, \
    estimatedstr, leveragestr, DEMO_DEBUG_MODEL, DEMO_DEBUG_PARALLEL
from ...monal.util.toolbox import _linkstr, maxWorkers, getExtraFields
from ...monal.util.utils import appdatadir, getapplidatabase, \
    getLibExt as libExtension
from ...monal import monalconst as C
from ...monal.modelutils import loadModule
from ...monal.datareader.modeldataframe import get_modelDataframe
from ...chem_gm.components.gmmEngine import createGMModel, computeSmile
from ...chem_gm.core.gmtoolbox import getModelBase, updateConfigFromConfigstr
from ...chem_gm.core import gmprograms as gmp

modulesticker = "GM"
USE_GM_LIB_FOR_TEST = 0

#======================================================================#
# complementary data to transfer by hook
groupavailables = {
        'identifiers': 0,
        'smiles': 1,
        'inputs': 2,
        'outputs': 3,
    }
grouptypes = {
    'identifiers': 'any',
    'smiles': str,
    'inputs': 'numerical',
    'outputs': 'numerical',
    }
groupdefault = ['identifiers', 'smiles', 'outputs']

add_arg_list = [('-fh', '--fullH', int, 0, "dico", "Model gm with full Hydrogen content. Default 0")]
item = ('-C', '--configstr', str, "", "dico", "Atoms and structures connectivity string")
add_arg_list.append(item)
item = ('-c', '--central', str, "3", "dico", "Candidates for central atom")
add_arg_list.append(item)

modeconfigdict = {
    'add_section': (2, "connectivity"),
    'add_set': (("general", "fullhydrogen", "False"),
                ("model", "mergeisochiral", "False"),
                ("model", "mol1", "True"),
                ("model", "isomeric_algo", "1"),
                ("private", "compactness", "3"))}

groupdict = {
    'inputs':'inputs',
    'in': 'inputs',
    'outputs': 'outputs',
    'out': 'outputs',
    'identifiers':'identifiers',
    'id':'identifiers',
    'smiles':'smiles',  # ici
    'smi':'smiles',
    }
#======================================================================#
# start of hookable methods

# to be hooked to nn1._api_service.deepDataAnalysis
def deepDataAnalysisGM(mode, dataFrame, config=None, options=None, 
    acceptdefault=False, classif=False, doprint=doNothing):  
    """Analyse data file for gathering chemical informations for graphmachine configuration string creation.
      
    Parameters:
     - dataFrame -> modelDataFrame of training data.
     - configstr -> proposed origin configuration string.
     - classif -> classification ùodel.
     - doprint -> print function.
       
    Return the configuration string. 
    """
    configstr = options.configstr 
    configstr, _ = gmp.analyseGraphmachineData(dataFrame, config, 
        configstr, options, acceptdefault, classif, doprint)
    return configstr
    
# to be hooked to nn1._api_service.getTrainingModule
def createTrainingModuleGM(options, dataframe=None, 
        config=None, outputdir="", originbase="", unitfilename="", 
        progress=None, keeptemp=0, compiler="", verbose=0, 
        doprinttime=False, debug=0):
    """Create a module fore training from a data frame.
    This function is to be hooked in metaphor.nn1.api.getTrainingModule
    parameters:    
     - dataiterator -> data broker
     - config -> 
     - modulename -> name to be given to the training module
     - outputdir -> directory for output
     - originbase -> name of the original data base
     - unitfilename -> name of the atomic file name.
     - progress -> process follow-up procedure.
    
    Return the created module.
    """
    if config is None:
        config = defaultedConfigParser(options.cfgfile)
    if config is not None:
        updateConfigFromConfigstr(options.configstr, config)
    
    savedir = options.libfolder
    tempdir = gmp.getSourceSaveDir(keeptemp, basedir=options.savedir)
#     if (options.debug & DEMO_DEBUG_MODEL) and options.keeptemp:  # 
#         tempdir = os.path.join(options.savedir, "temp", options.keeptemp)
#         if os.path.exists(tempdir):
#             shutil.rmtree(tempdir, ignore_errors=True)
    modulename = getModelBase(config, fullconfig=True)
    locmodel = "lib{0}{1}".format(modulename.lower(), libExtension())
    fullmodelname = os.path.join(savedir, locmodel)
    if options.debug & DEMO_DEBUG_MODEL:
        print('tempdir', tempdir)
        print('modulename', fullmodelname)
    modelmode = ""
    if not options.modelcreation and os.path.exists(fullmodelname):
        lib, OK = loadModule(fullmodelname, all=True)
        modelmode = "load"
        modcount = lib.modelCount
        Ok = OK and ((modcount < 0) or (modcount == dataframe.shape[0]))
        if OK:
            return lib, fullmodelname, None, modelmode
        else:   
            lib.__del__()
            lib = None
    if not originbase and config and config.has_option("general", "root"):
        originbase = config.get("general", "root")
    hidden = options.hidden
    if config:
        config.set("model", "hidden", str(hidden))
    writer = sys.stdout if verbose >= 2 else None
    if not outputdir:
        outputdir = savedir
    module, _ = gmp.createmodeltrainingbase(
        iterator=dataframe.itertuples(), 
        titlerow=dataframe.columns,
        keeptemp=keeptemp,
        tempdir=tempdir,
#         iterator=dataframe.iterData(), 
        config=config,
        hidden=hidden,
        originbase=originbase,
        outputdir=outputdir, 
        modulename=modulename,          
        savingformat=C.SF_CPYTHON,
        moduletype="dll",
        unitfilename=unitfilename,
        progress=progress,
        compiler=compiler,
        docreatefolder=False,
        writer=writer,
        configstr=options.configstr,
        doprinttime=doprinttime, 
        debug=options.debug)
    modelmode = "compile"
    if not os.path.exists(module):
        raise Exception("Error creating module %s"% module) 
    lib, OK = loadModule(module, all=True)
    return lib, module, None, modelmode

# to be hooked to nn1._api_service.computeTest
def computeTestGM(options, modeltestframe, IDlist, tablename, pptyname, 
        maxreclist, source, savedir, filename, filetype="", 
        testrange="", testformat=None, leveragethreshold=1, 
        extraselect="", orderfield="PRESS", finishTest=None, verbose=1, 
        debug=0):   
    """Calcul du resultat des tests.
    """
    maintitles = modeltestframe.gettitles()
    nametitle, smilestitle, pptyname = maintitles 
    maxreccount = len(maxreclist)
    maxrec = maxreclist[0]
#     nametitle, smilestitle, pptyname = maintitles 
    testFrameBaseCol = modeltestframe.shape[1]
    testFrame = modeltestframe._frame.copy()
    countfield, cols, richestimated, richtestresidual = getExtraFields(maxreclist, pptyname)
    targetfieldstr = testFrame.columns[-1]
    
    keyList = [_linkstr(estimatedstr, pptyname, ID) for ID in IDlist]
    levList = [_linkstr(leveragestr, pptyname, ID) for ID in IDlist]
    for key, lev in zip(keyList, levList):
        cols.append(key)
        cols.append(lev)
    fullcol = list(testFrame.columns) + cols
    newcol = OrderedDict({val: float('nan') for val in cols})
    testFrame = testFrame.assign(**newcol)
    testFrame = testFrame[fullcol]  # remise en ordre de testFrame

    testFrame = _createModelsGM(source, savedir, testFrame, 
        maintitles=maintitles, keyTitleList=keyList,
         levTitleList=levList, verbose=verbose, debug=debug)   # moduleSerie  modeluse=modeluse, 

    patternlist = finishTest(testFrame, targetfieldstr,
        keyList, levList,  maxreclist, richestimated, richtestresidual, 
        countfield, leveragethreshold)
    
    return testFrame, patternlist, testFrameBaseCol, 0

# to be hooked to nn1._api_service.computeLOOTest
def computeLOOTestGM(options, modeltestframe, tablename, pptyname, 
        datacount, source, savedir, filename, filetype="", testrange="", 
        testformat=None, leveragethreshold=1, extraselect="", 
        orderfield="PRESS", verbose=1, debug=0):   
    """Calcul du resultat des tests avec LOO.
    """
    maintitles = modeltestframe.gettitles()
    patternlist = []
    if options.mode == 'gm':
        nametitle, smilestitle, pptyname = maintitles 
    else:
        nametitle = maintitles[0]
        pptyname = maintitles[-1]
        inputtitles = maintitles[1:-1]
    reverse = orderfield in C.TCR_MAXIMIZE   
    testFrameBaseCol = modeltestframe.shape[1]
    testFrame = modeltestframe._frame.copy()
    cols = []
    richestimated = []
    countfield = []
    resKey = _linkstr(estimatedstr, pptyname)
    resLOOKey = "LOO_%s"% (_linkstr(estimatedstr, pptyname))
    cols = [resKey, resLOOKey]
    baselen = datacount
    for looindex in range(baselen):
        fieldstr = "LOO_%s_%d"% (_linkstr(estimatedstr, pptyname), 
                                 looindex)
        richestimated.append(fieldstr)
    cols.extend(richestimated)
    fullcol = list(testFrame.columns) + cols
    newcol = OrderedDict({val: float('nan') for val in cols})
    testFrame = testFrame.assign(**newcol)
    testFrame = testFrame[fullcol]  # remise en ordre de testFrame

    testFrame = _createModelsLOOGM(source, savedir, testFrame, 
        maintitles=maintitles, keyresult=resKey, keyLOOresult=resLOOKey, 
        LOOkeys= richestimated, verbose=verbose, mode=options.mode, 
        debug=debug)   # moduleSerie  modeluse=modeluse, 
 
    return testFrame, patternlist, testFrameBaseCol      
 
# to be hooked to nn1._api_service.computeBSTest
def computeBSTestGM(options, modeltestframe, tablename, pptyname,
                    bscount, source, savedir, 
        filename, filetype="", testrange="", testformat=None, 
        leveragethreshold=1, extraselect="", 
        orderfield="PRESS", verbose=1, debug=0):  
        raise NotImplementedError

# end of hookable methods
#======================================================================#
def _createModelsGM(source, savedir, testFrame, maintitles=[], 
    modeluse=USE_GM_LIB_FOR_TEST, writer=None, maxworkers=-2, keyTitleList=[], 
    levTitleList=[], verbose=1, debug=0):  
    """Creation des models unitaires (*.so ou ) depuis les noms et smiles 
    contenus dans la base testFrame.
    """
    nametitle, smilestitle, pptyname = maintitles 

    if isinstance(source, str):
        source = np.load(source)
    mess = 'compute modules'
    length = testFrame.shape[0]
    t_create = 0
    t_compute = 0
    t_load = 0
    printtime = False
    
    smilesSerie = testFrame[smilestitle]
    max_workers = maxWorkers(maxworkers)
    with Progress_tqdm(length, desc=mess, nobar=verbose<nobarverb) as update:
        if (max_workers > 1) and not NO_PARALLEL_TEST and not (debug & DEMO_DEBUG_PARALLEL):  # parallel
            with PoolExec(max_workers=max_workers) as executor:
                futures = [executor.submit(computesmile_transfer, 
                    smiles, source, molecule, savedir, writer, False) 
                    for molecule, smiles in smilesSerie.iteritems()]        
                for indloc, future in enumerate(as_completed(futures)):
                    #if update:
                    update(indloc+1)
                    outputs, leverages, molecule = future.result()
                    for keytitle, levtitle, output, leverage in zip(keyTitleList, levTitleList, outputs, leverages):                                                            
                        testFrame.at[molecule, keytitle] = float(output)
                        testFrame.at[molecule, levtitle] = float(leverage)                                                           
        else:
            printtime = True
            for ind, (molecule, smiles) in enumerate(smilesSerie.iteritems()):     
                #if update:
                update(ind+1)
                
                outputs, leverages, molecule = computesmile_transfer(
                    smiles, source, molecule, savedir, writer, False)
                
                for keytitle, levtitle, output, leverage in zip(keyTitleList, levTitleList, outputs, leverages): 
                    testFrame.at[molecule, keytitle] = float(output)
                    testFrame.at[molecule, levtitle] = float(leverage)
        update.flush()
    if printtime:
        print("model creation time", t_create)
        print("model loading time", t_load)
        print("model transfer time", t_compute)  
                             
    return testFrame  #, series

def _createModelsLOOGM(source, savedir, testFrame, maintitles=[],
    keyresult="", keyLOOresult="", LOOkeys = [], writer=None, 
    maxworkers=-2, verbose=1, mode="nn", debug=0):  #modeluse=USE_LIB, 
    """Creation des models unitaires (*.so ou ) depuis les noms et smiles 
    contenus dans la base testFrame.
    """
    nametitle, smilestitle, pptyname = maintitles 
    smilesSerie = testFrame[smilestitle]
    inputtitles = []

    if isinstance(source, str):
        source = np.load(source)
    mess = 'compute modules'
    t_create = 0
    t_compute = 0
    t_load = 0
    printtime = False
    
    max_workers = maxWorkers(maxworkers)
    
    # A revoir dans le cas de mode = "nn"
    
    with Progress_tqdm(len(testFrame.index), desc=mess, nobar=verbose<nobarverb) as update:
        if  (max_workers > 1) and not NO_PARALLEL_TEST and not (debug & DEMO_DEBUG_PARALLEL):  # parallel
            with PoolExec(max_workers=max_workers) as executor:
                futures = [executor.submit(computesmile_transferLOO, 
                    index, smiles, source, molecule, savedir, writer, False) 
                    for index, (molecule, smiles) in enumerate(smilesSerie.items())]
                for indloc, future in enumerate(as_completed(futures)):
                    #if update:
                    update(indloc+1)
                    indLOO, output, outputs, molecule = future.result()
                    #LOOPred = float(outputs[indLOO])
                    testFrame.at[molecule, keyresult] = float(output)
#                     testFrame.set_value(molecule, keyresult, float(output))
                    mean = 0.0
                    for key, value in zip(LOOkeys, outputs):
                        val = float(value)
                        mean += val
                        testFrame.at[molecule, key] = val
#                         testFrame.set_value(molecule, key, val)
                    mean = mean / len(LOOkeys)
                    testFrame.at[molecule, keyLOOresult] = mean
#                     testFrame.set_value(molecule, keyLOOresult, mean)
        else:
            printtime = True
            for ind, (molecule, smiles) in enumerate(smilesSerie.items()):
                #if update:
                update(ind+1)
                
                indLOO, output, outputs, molecule = computesmile_transferLOO(
                    ind, smiles, source, molecule, savedir, writer, False)
                
                #LOOPred = float(outputs[indLOO])
                testFrame.at[molecule, keyresult] = float(output)
#                 testFrame.set_value(molecule, keyresult, float(output))
                mean = 0.0
                for key, value in zip(LOOkeys, outputs):
                    val = float(value)
                    mean += val
                    testFrame.at[molecule, key] = val
#                     testFrame.set_value(molecule, key, val)
                mean = mean / len(LOOkeys)
                testFrame.at[molecule, keyLOOresult] = mean
#                 testFrame.set_value(molecule, keyLOOresult, mean)
        update.flush()
    if printtime:
        print("model creation time", t_create)
        print("model loading time", t_load)
        print("model transfer time", t_compute)  
                             
    return testFrame  #, series

def computesmile_transfer(smile, source, molecule, savedir, writer, givetime): 
    drivermodel, _, molecule, _ = computeSmile(smile, source=source, 
        molecule=molecule, modeldir=savedir, modeluse=USE_NO_LIB, moduletype='', 
        writer=writer, givetime=givetime)
    outputs, leverages = drivermodel.transferEx()  #original=True
    return outputs, leverages, molecule

def computesmile_transferLOO(index, smile, source, molecule, savedir, writer, givetime): 
    drivermodel, _, molecule, _ = computeSmile(smile, source=source, 
        molecule=molecule, modeldir=savedir, modeluse=USE_NO_LIB, moduletype='', 
        writer=writer, givetime=givetime)
    output, outputs = drivermodel.transferExtra()  #original=True
    return index, output, outputs, molecule

def compute_transferBS(index, smile, source, molecule, savedir, writer, givetime): 
    drivermodel, _, molecule, _ = computeSmile(smile, source=source, 
        molecule=molecule, modeldir=savedir, modeluse=USE_NO_LIB, moduletype='', 
        writer=writer, givetime=givetime)
    drivermodel.confidenceLevel = 0.95
    output, output95p, output95m, outputs = drivermodel.transferExtraCI()  #original=True
    return index, output, output95p, output95m, outputs, molecule

def singleCoreUsageActionGM(xml, source, ni, nh, no, idName, grouplist, datalist):
    if 'inputs' in grouplist:
        inputs = np.asarray([float(val) for val in datalist[grouplist.index('inputs')]])
    if 'targets' in grouplist:
        target = float(datalist[grouplist.index('targets')][0])
    smile = datalist[grouplist.index('smiles')][0]
     
    model = createGMModel(source, id, smile, truename="")  #savedir=None, 
    if not idName:
        idName = model.modelName
    outs, levs, stds, students = model.transferEx(inputs, 
        withCI=True) 
    return model, target, idName, outs, levs, stds, students

def multiCoreUsageActionGM(xml, source, dataFrame, options, ni):
    modelNames = []
    outslist = []
    levslist = []
    icslist = []
    stdslist = []
    studentslist = []
    count = 0
    with Progress_tqdm(dataFrame.shape[0], desc="computing model", 
                       nobar=options.verbose<nobarverb) as update:
        for ID, row in dataFrame.iterrows():
            count += 1
            update(count)
            if ni:
                inputs = row[:ni]
            smile = row[ni]
            target = row[ni+1:]
            model = createGMModel(source, ID, smile, truename="")  
            modelNames.append(model.modelName)
            res = model.transferEx(inputs, withCI=True)  
            outs, levs, stds, students = res
            ics = [np.sqrt(lev)*studentvar*stddev for lev, stddev, studentvar in zip(levs, stds, students)]
            outslist.append(outs)
            levslist.append(levs)
            stdslist.append(stds)
            studentslist.append(students)
            icslist.append(ics)
        update.flush()

if __name__ == '__main__':
    pass