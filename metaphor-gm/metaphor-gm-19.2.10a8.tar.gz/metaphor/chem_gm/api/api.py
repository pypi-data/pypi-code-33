#! python
# -*- coding: UTF-8 -*-
# $Id$
#
# Copyright 2016 Jean-Luc PLOIX
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#from docutils.nodes import title
#from _modelcontainer import lst, lst2

'''
Graph machine programming interface
'''

targetstr = "measured"  
leveragestr = "leverages"
pressstr = "VLOO score"
stddevstr = "RMSE"
stddevbiaslessstr = "biasless RMSE"
trainresidualstr = "estimation_error"
testresidualstr = "estimation_error"
estimatedstr = "estimated"
meanstr = "mean"

import warnings
warnings.filterwarnings("ignore")
import os, sys
from math import sqrt, fabs
import functools as ft
import numpy as np
from pandas import DataFrame, set_option, Series
OKmatplotlib = False
# try:
#     import matplotlib
#     import matplotlib.pyplot as plt
#     from chem_gm.components.mplUtils import draw_stat, draw_stat2
#     OKmatplotlib = True
# except ImportError:
from collections import OrderedDict, defaultdict
import sqlite3 as sql

from ...nntoolbox.timetb import second2str
from ...nntoolbox.utils import unquote, DEMO_DEBUG_MODEL, DEMO_DEBUG_ANALYSIS
from ...nntoolbox.configparsertoolbox import defaultedConfigParser, \
    getDefaultedConfigParser
from ...nntoolbox.filetoolbox import backupfile, IndexFilename, \
    getReducedSelectedGmx, getDictFromGmx
from ...nntoolbox.utils import isInt, saveToFilez, RE_NONE, RE_LOO, RE_SUPER
from ...nntoolbox.modelutils import getModelDict, getSaveDictMulti
from ...nntoolbox.sqlite_numpy import createTableDb, cleanTableDb, \
    insertDataToDb, saveDataToDb, getDataFromDb, getDataFrame, createTableDb, \
    getSelectQuery, getFieldList

from ...monal.util.monaltoolbox import yesNoQuestion, valueQuestion
from ...monal import monalconst as C
from ...monal.model import ModelLib, codeVersionOK
from ...monal.driver import DriverMultiDyn
from ...monal.modelutils import ReadModule, loadModule
from ...monal.util.utils import appdatadir, CCharOnlys, defaultModuleExt
from ...monal.util.toolbox import make_dir, dataIterator, cleanDir, maxWorkers, \
    setTrainingActionParams, _linkstr
from ...monal.driver import Driver, onEndIter, onReturnResult
from ...monal.datareader.excelsource import getFrame, gettitles
from ...monal.library.libmanager import LibManager

from ..components.gmmEngine import gmxError, gmxExistError
from ..gmconstants import filedict, checkinstall
#from chem_gm.version import __version__ as GMpath
from ..api.cleancfg import defaultGMCfg, clearConnect
from ..core.gmutils import connectdef, connectdefault
from ..components.gmmEngine import computeSmile, createPythonDll, getFullModuleName # as getFullModuleName1
from ..core import gmprograms as gmp
from ..core.gmutils import gmxTmpl, key2long, cyclekey, gradekey, isokey,\
     chikey, chargekey, getConfigHash
from ..core.gmtoolbox import getModelBase
#from string import capitalize
#import chem_gm
from .. import __path__ as gm_path
GMpath = gm_path[0]
if not GMpath in sys.path:
    sys.path.append(os.path.join(GMpath, 'main'))

badlist = checkinstall("", ("atoms.cfg",))

moleculestr = "Molecule"
maintitles0 = (moleculestr, "SMILES", "property")

KEEP_TEMP = ""
USE_LIB = 0
USE_CREATED_LIB = 1

debug = 0x8000000 # 134217728

set_option('display.max_columns', None)
set_option('display.max_rows', None)
set_option('display.expand_frame_repr', False)
#set_option('display.float_format', lambda x: "%2.2f"%x)

# def float_format(verbose):
#     form = "%7.4f" if verbose >= 5 else "%5.2f"
#     return (lambda x: form % x)
#     #return (lambda x: "%7.4f" % x) if verbose >= 5 else (lambda x: "%5.2f" % x)
#     
# def roundoff_format():
#     return (lambda x: "%4.2E" % x)
# 
# def IDformat():
#     return (lambda x: "#%d" % x)

class GM_APIError(Exception):
    pass

def analyseTrainingDatafile(filename, filetype="" , datarange="", skipline=0, 
        delimiter=';', dataformat=[0, 1, 2], maxlength=50000, titlesfirst=True,
        fullH=False, debug=0):
    """Analyse data source content.
    
    - filename -> data file name.
    
    - filetype -> "", "csv", "xls", "xlsx". If filetype=="", filetype will be assigned filename extension.
    
    - datarange -> Name of the data range for xls and xlsx type files only.
    
    - skipline -> number of beginning skipped lines or csv type files only.
    
    - delimiter -> suggested data delimiter character for csv type files only.
    
    - datafmt -> list of data column indexes. Default [0,1,2]
    
    - maxlength -> max number of analysed lines. Default 50000.
    
    - titlesfirst -> boolean: include titles as first line. Default True
    
    return a tuple of 14 elements:
    
    - atoms -> List of atoms present in the base
    
    - grademax -> maximum grade in the base.
    
    - isomax -> maximum isomeric index in the base.
    
    - chiralmax -> maximum chiral index in the base.
    
    - occurs -> dictionary of the atom and structure elements oocurrences.
    
    - occurmols -> dictionary of the molecules occurrences for atom and structure elements.
    
    - cycles -> dictionary of the cycle structure occurrences.
    
    - delimiter -> delimiter. meaningful only for csv type files.
    
    - baselen -> base length
    
    - names -> name list (index 0 of datafmt)
    
    - smilist -> smiles list (index 1 of datafmt)
    
    - pptylist -> property value list (index 2 of datafmt)
    
    - reslist -> list of occurences in each molecule as dictionary
    
    - reslimit -> limited base bool.
    """
    #global pptyname
    if not filetype:
        filetype = os.path.splitext(filename) [1][1:]
    logstream = sys.stdout if debug & DEMO_DEBUG_ANALYSIS else None
    res = gmp.analysebase(None, filename=filename, filetype=filetype, 
            datarange=datarange, skipline=skipline, delimiter=delimiter, 
            datafmt=dataformat, logstream=logstream, cyclemax=None, 
            targetfilename="", maxlength=maxlength, titlesfirst=titlesfirst,
            fullH=fullH)
    atoms, grademax, isomax, chiralmax, occurs, occurmols, cycles, delimiter, \
        baselen, names, smilist, pptylist, _, titles, reslimit, \
        chargelist, _ = res  #reslist errorlist
    cyclemax = 0
    for key, val in cycles.items():
        if val:
            cyclemax = max(cyclemax, int(key))
    #chargeminmax = 0, 0
    chmax = chmin = 0
    for value in chargelist:
        if value[:2] == 'qp':
            chmax = max(chmax, int(value[2:]))
        elif value[:2] == 'qm':
            chmin = min(chmin, -int(value[2:]))
    chargeminmax = chmin, chmax
    try:
        pptyname = titles[-1]
    except:
        pptyname = ""
    config = defaultGMCfg(["training", ""])
    dict3 = {
        "source": filename,
        "sourcetype": filetype,
        "sourcerange": datarange,
        "grademax": grademax,
        "isomax": isomax,
        "chiralmax": chiralmax,
        "cyclemax": cyclemax,
        "chargemin": chargeminmax[0],
        "chargemax": chargeminmax[1],
        "skipline": skipline,
        "delimiter": delimiter,
        "lines": baselen,
        "format": ",".join([str(val) for val in dataformat]),
        "atoms": ",".join(atoms),
        'fullhydrogen': fullH,
        }
    if reslimit:
        dict3["limited"] = str(reslimit)
    config.updatesection("general", **dict3)
    
    dict1 = {}
    dict2 = {}
    for key, value in occurs.items():
        st = "%s, %s" %(value, occurmols[key])
        if key in atoms: 
            dict1[key] = st
        else: # key in occurmols
            dict2[key2long(key)] = st
    #for key, value in cycles.iteritems():
    for key, value in cycles.items():
        dict2[cyclekey(key+1, True)] = value  #cycles[key]
    originname = CCharOnlys(os.path.splitext(os.path.basename(filename))[0], 
        extended=True)
    config.updatesection("occurence", **dict1)
    config.updatesection( "exoccurence", **dict2)
    config.set("general", "root", originname)
    iter1 = dataIterator(titles, names, smilist, pptylist) # pptylist ajoute le 14/10/17
    #iter1 = list(iter1)
    return config, iter1, pptylist, pptyname, baselen, titles  # ici reslist est abandonné

def setTrainingModelParams(config, **kwd):
    """Introducing the connectivity parameters along with the hidden, mol1, 
    classif & central values in the configuration object.
    
    Allowed parameters in the kwd dictionary are:
    
    model parameters:
    
        - hidden -> number of hidden nodes
        
        - mol1 -> limit the connectivity to molecular occurrence minus 1.
        
        - classif -> classification model
        
        - central -> suggested central atom list.
        
        - fullhydrogen -> 
    
    connectivity parameters:
    
        - degrees -> maximum grades
        
        - isomers -> maximum isomeric index
        
        - chirals -> maximum chiral index
        
        - isomers -> 
        
        - isomer(1) -> 
        
        - isomer(2) -> 
        
        - chirals -> 
        
        - chiral(1) -> 
        
        - chiral(2) -> 
        
        - degree(1..grademax) -> 
        
        - cycle(1..cyclemax) -> 
    """
    assert(isinstance(config, defaultedConfigParser))
    has_H = 'H' in kwd
    has_H = has_H and kwd['H']
    connect = connectdefault(has_H).copy()
    modeldict = {}
    grademax = config.getintdefault("general", "grademax", 6)
    cyclemax = config.getintdefault("general", "cyclemax", 12)
    chargemin = config.getintdefault("general", "chargemin", -4)
    chargemax = config.getintdefault("general", "chargemax", 4)
    for key in kwd:
        if key in ("hidden", "mol1", "central", "classif"):
            modeldict[key] = kwd[key]
        elif key == "cycles":
            for ind in range(1, cyclemax):
                connect[cyclekey(ind, 1)] = kwd[key]
        elif key in ("degrees", "grades", "grds"):
            for ind in range(1, grademax+1):
                connect[gradekey(ind, 1)] = kwd[key]
        elif key in ["qp", "qm"]:
            for ind in range(1, chargemax+1):
                connect[chargekey(ind, 1)] = kwd[key]
                connect[chargekey(-ind, 1)] = kwd[key]
#         elif key == "qm":
#             for ind in range(1, chargemin-1, -1):
#                 connect[chargekey(ind, 1)] = kwd[key]
#                 connect[chargekey(-ind, 1)] = kwd[key]
        elif key == "isomers":
            connect[isokey(1, 1)] = kwd[key]
            connect[isokey(2, 1)] = kwd[key]
        elif key == "chirals":
            connect[chikey(1, 1)] = kwd[key]
            connect[chikey(2, 1)] = kwd[key]
        else:
            connect[key] = kwd[key]
        
    atoms = config.getdefault("general", "atoms", [])
    atoms0 = atoms.split(",")
    if len(atoms):
        atoms = [val.title() for val in atoms0]
        if "central" in kwd:
            central = kwd["central"]
            if not central:  # or not isinstance(central, int) or not len(central):
                central = atoms
            elif isInt(central):  #isinstance(central, int):
                central = atoms[:int(central)]
            elif isinstance(central, str):
                lst = [val.capitalize() for val in central.split(",")]
                if all([val in atoms for val in lst]):
                    central = lst
                else:
                    central = atoms
            else:
                central = atoms
            modeldict["central"] = ",".join(central)
    if "hidden" in kwd:
        hidden = kwd["hidden"]
        if hidden:
            for val in atoms0:
                if val:
                    if connect[val] == -1:
                        connect[val] = hidden
                    if val in kwd:
                        connect[val] = min(connect[val], kwd[val])
            for val in config.options("exoccurence"):
                if connect[val] == -1:
                    connect[val] = hidden
    connect = clearConnect(connect, atoms)
    config.updatesection("connectivity", **connect)
    config.updatesection("model", **modeldict)
    return config

def createTrainingModule(dataiterator, config, modulename="", outputdir="", 
        tempdir="", originbase="", unitfilename="", progress=None, keeptemp=0,
        compiler="", verbose=0, doprinttime=False, debug=0):
    """Create a module fore training from a data broker.
    
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
    if not originbase and config and config.has_option("general", "root"):
        originbase = config.get("general", "root")
    hidden = config.get("model", "hidden")
    writer = sys.stdout if verbose >= 2 else None
    module, _ = gmp.createmodeltrainingbase(
        keeptemp=keeptemp,
        tempdir=tempdir,
        iterator=dataiterator, 
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
        doprinttime=doprinttime, 
        debug=debug)
    if not os.path.exists(module):
        raise Exception("Error creating module %s"% module) 
    return module

def loadTrainingModule(moduleName, workingdir=""):
    """Loading a training module.
    
    parameters:
    
        - moduleName -> 
        
        - workingdir -> 
    
    Return the loaded object.
    """
    return gmp.loadbase(moduleName, workingdir=workingdir)

def loadUsageModule(gmxfile, moleculename, smiles, savedir="default", 
    mustcreatelib=False):
    """Create a molecule model for usage if necessary, and load it
    parameters:
    
    - gmxfile -> file created by a training process
    
    - moleculename -> (str, unicode)Name of the molecule
    
    - smiles -> (str, unicode) smiles code of the molecule
    
    - savedir -> Directory for saving the library file. If set "default" then a user specific directory is used.
    
    - mustcreatelib -> 
    
    Return the newly loaded module.
    """
    modname = getFullModelName(gmxfile, moleculename)
    if savedir == "default":
        savedir = appdatadir("models", APPNAME="graphmachine", docreate=1)
    path = savedir
    lst = modname.split('.')
    for val in lst[:-1]:
        path = os.path.join(path, val)
    finalpath = lst[-1]
    ext = defaultModuleExt()
    #if (self.moduletype in ["so", "dylib"]) and not finalpath.startswith("lib"):
    if not finalpath.startswith("lib"):
        finalpath = "lib" + finalpath            
    finalpath = os.path.join(path, finalpath)
    if not finalpath.endswith(".%s"% ext):
        finalpath = "%s.%s"% (finalpath, ext)
        
    cond = mustcreatelib or not os.path.exists(finalpath) or not codeVersionOK(finalpath)
    
    if cond:
        modname = createPythonDll(gmxfile, moleculename, smiles, 
            savedir=savedir, keeptemp=KEEP_TEMP)
    return ModelLib(modname, source=gmxfile)

def trainModule(module, targets=None, propertyname="", config=None, initparams=None, 
        outputnorm=None, workingdir="", trainstyle=0, onReturnResult=None, 
        onEndIter=None, saveResult=None, savetemplate=gmxTmpl):
    """Launching a training session

    Parameters:
    
        - module -> 
        
        - targets -> 
         
        - propertyname -> 
         
        - config -> 
         
        - initparams=None -> 
     
        - outputnorm=None -> 
         
        - workingdir="" -> Working directory.
        
        - trainstyle -> training style (monalconsy CS_xxx constants))
        
        return 3-tuple:
        
        - module -> In memory training module
        
        - nfails -> number of failures.
    """
    if isinstance(module, str):
        module = gmp.loadbase(module, workingdir)
    if propertyname:
        module.propertyName = propertyname
    if not targets is None:
        module.targets = np.asarray(targets)
    root = config.getdefault("general", "root", "")
    trainsection = _linkstr("training", propertyname) if propertyname else "training"
    initcount = config.getintdefault(trainsection, "initialization", 1)
    epochs = config.getintdefault(trainsection, "epochs", 100)
    seed = config.getdefault(trainsection, "seed", "None")
    if seed == "None":
        seed = None
    else:
        seed = int(seed)
    resultdir = config.getdefault(trainsection, "resultdirectory", "")
    resultdir = os.path.join(resultdir, root)
    criterion = config.getintdefault(trainsection, "criterion", C.TCR_NOSORT)
    weightsstddev = config.getfloatdefault(trainsection, "initstddev", 0.3) 
    if resultdir:
        make_dir(resultdir)
    
    nfail = module.multitrain(
            initcount=initcount, 
            epochs=epochs,
            initweights=initparams,
            weightsstddev=weightsstddev,
            seed=seed,
            onEndIter=onEndIter,
            onReturnResult=onReturnResult,
            trainstyle=trainstyle)
    
    return module, nfail  #savelist, bests, 

# def getGmxFileAndSave(dbConnect, gm0, config, indexlist, options, full=False, extrasize=-1, dosave=True):
#     gmdict = getSaveDictMulti(indexlist, dbConnect, gminit=gm0, extrasize=extrasize)
#     #config = gm0['config']
#     config = getDefaultedConfigParser(config)
#     root = config.getdefault("general", "root", "root")   
#     gmxfilename = getGmxFileName(options, dosave)    
#     if dosave:
#         saveToFilez(gmxfilename, gmdict) 
#     if full:
#         return gmxfilename, gmdict
#     return gmxfilename

# def getBaseDict(config, model=None, propertyName=None, parameterNames=None, 
#         outputnorm=None, paramCount=None, modelCount=None):
# #     gm0 = {}
# #     sectionlst = ["model", "general", "connectivity", "occurence", "exoccurence"]
# #     for section in [val for val in sectionlst if config.has_section(val)]:
# #         gm0[section] = config.getSectionDict(section)
#     return getModelDict(config=config, model=model, propertyName=propertyName,
#         parameterNames=parameterNames, outputnorm=outputnorm,
#         paramCount=paramCount, dataCount=modelCount)
# #     return gm0

def SaveGmxFile(dbConnect, config, model, savedir, indexlist):
    gm0 = getModelDict(config, model)
    gmdict = getSaveDictMulti(indexlist, dbConnect, gminit=gm0)
    modname = getModelBase(config, fullconfig=True)
    gmxfile = os.path.join(savedir, "%s.gmx" % modname)
    saveToFilez(gmxfile, gmdict) 
    return gmdict, gmxfile

def resamplingTrainModule(module, inittype=C.INIT_START_PARAM, initlist=[], 
        initcount=1, count=0, epochs=0, BStype=RE_NONE, weightsstddev=0.1,
        computeDispersion=False, selected_LOO=None, LOOcriterion=-1,
        callBack=None, onReturnResult=None):
    """Launching a special training session. Special may mean Leave-One-out or Bootstrap.
    Parameters:
    
        - module -> In memory training module.
        
        - inittype ->  . Default INIT_START_PARAM
        
            Available:
            
            - INIT_START_PARAM -> Initialization with the parameters of the starting train process
            
            - INIT_END_PARAM -> Initialization with the parameters at the end of the training process
            
            - INIT_RANDOM -> Random initialization.
        
        - initlist -> Rekated to super training.ƒ
            Initialization parameters list. Each item of this list is 
            a tuple of at least 4 elements. Element 2 is used with 
            INIT_END_PARAM inittype, and element 3 is used with INIT_START_PARAM 
            inittype. Default []
        
        - inicount -> Number of initialization for Leave-One-out. Default 1
        
        - count -> Number of Bootstrap resampling. Meaningless for Leave-One-out. Default 0
        
        - epochs -> Training epochs. Default 0
         
        - BStype -> Resampling type. Default RE_NONE
        
            Available:
            - RE_NONE -> no resampling
            
            - RE_BS_STD -> standard Bootstrap.
            
            - RE_BS_RESIDU -> residual Bootstrap.
            
            - RE_LOO -> Leave-One-Out.

        - computeDispersion -> Compute leverages and dispersion matrix. Default False
         
        - selected_LOO -> Debug. With serial training only. List of selected initialization in training base list. Default None
        
        - LOOcriterion -> selection criterion for LOO result. Default CRITER_PRESS
        
            Available: 
            
            - CRITER_STDDEV -> minimum standard deviation 
            
            - CRITER_PRESS -> minimum PRESS
            
            - CRITER_LEV -> minimum pseudo-leverage
        
        - callBack -> Follow up callback function. Default None
    
    return
    
        - loccount -> Number of local training performed.
        
    Constants are defined in module monal.monalconst
    """

    assert(isinstance(module, DriverMultiDyn))
    if BStype == RE_LOO:
        res = module.trainLOO(inittype=inittype, initlist=initlist, 
            initcount=initcount, weightsstddev=weightsstddev, epochs=epochs, 
            selected_LOO=selected_LOO, LOOcriterion=LOOcriterion, 
            callback=callBack, onReturnResult=onReturnResult, trainstyle=0)
    elif BStype == RE_SUPER:
        res = module.trainSuper(inittype=inittype, initlist=initlist, 
            initcount=initcount, weightsstddev=weightsstddev, BScount=count, 
            epochs=epochs, selected_LOO=selected_LOO, callback=callBack, 
            onReturnResult=onReturnResult, trainstyle=0)
    else:
        res = module.trainBS(inittype=inittype, initlist=initlist, 
            initcount=initcount, weightsstddev=weightsstddev, BScount=count, 
            epochs=epochs, BStype=BStype, selected_LOO=selected_LOO, 
            LOOcriterion=LOOcriterion, callback=callBack, 
            onReturnResult=onReturnResult, trainstyle=0)
    # mettre trainstyle=0
    return res
  
#----------- PRIMITIVES INTEGREES ----------------------------------------------

def createModule(filename, datadic=None, libdic=None, modeldic=None, 
        configfile="", doprinttime=False, fullH=False):
    """Creating a training module.
    
    This integrated procedure include successively the following procedures
    properly connected:
    
    - analyseTrainingDatafile
    
    - setTrainingModelParams
    
    - createTrainingModule
    
    - loadTrainingModule
    
    Parameters:
    
        - filename -> Data file including molecules names, smiles and property values
        
        - datadic -> dictionary descriving data. Default None
        
        - libdic -> dictionary descriving module creation. Default None
        
        - modeldic -> dictionary descriving model construction. Default None
        
        - configfile -> filename for saving configuration. Default ""
    
    return  a 5-tuple:
    
        - model -> in memory training model created from the data base
        
        - config -> configuration object
        
        - modulename -> module name
        
        - pptylist -> property value list
        
        - propertyname -> property name
    """
#     if (datadic is None) or not len(datadic):
#         res = analys eTrainingDatafile(filename=filename, datarange=datarange)
#     else:
    datadic.update({'fullH': fullH})
    res = analyseTrainingDatafile(filename, **datadic) #, fullH=fullH)
    config, iterator, pptylist, propertyname, baselen, titles = res
    config = setTrainingModelParams(config, **modeldic)
    if configfile:
        with open(configfile, "w") as ff: 
            config.write(ff)
    libdic.update({'debug': debug})
    modulename = createTrainingModule(iterator, config, **libdic)  #, debug=debug)
    reseau = loadTrainingModule(modulename)
    return reseau, config, modulename, pptylist, propertyname

def createModuleAndTrain(filename, datadic=None, libdic=None, modeldic=None, 
                         traindic=None, configfile="", progress=None, fullH=False):
    """Creating a training module and launching the training.
    
    This integrated procedure include successively the following procedures
    properly connected:
        
    - analyseTrainingDatafile
    
    - setTrainingModelParams
    
    - createTrainingModule
    
    - loadTrainingModule
    
    - trainModule

    Parameters:
    
        - filename -> Data file including molecules names, smiles and property values
        
        - datadic -> dictionary descriving data
        
        - libdic -> dictionary descriving module creation
        
        - modeldic -> dictionary descriving model construction
        
        - traindic -> dictionary descriving training action
        
        - configfile -> filename for saving configuration.
    """
    reseau, config, _, pptylist, propertyname = createModule(
        filename, datadic, libdic, modeldic)  #modulename
    config = setTrainingActionParams(config, propertyname, **traindic)
    if configfile:
        with open(configfile, "w") as ff: 
            config.write(ff)
    initparams = traindic["initparams"] if "initparams" in traindic else None
    outputnorm = traindic["outputnorm"] if "outputnorm" in traindic else None
    debugfile = traindic["debugfile"] if "debugfile" in traindic else None
    workingdir = traindic["workingdir"] if "workingdir" in traindic else ""
    module, nfail = trainModule(reseau, pptylist, propertyname, config, 
        initparams=initparams, outputnorm=outputnorm, workingdir=workingdir,
        debugfile=debugfile, onEndIter=ft.partial(onEndIter, progress=progress))
    return module  #, savelist, bests    

#----------- UTILITAIRES -------------------------------------------------------

def getFullModelName(gmxfile, moleculename):
    """Retrieve the full module name from the modlecule name and the gmx file.
    """
    moleculename = CCharOnlys(moleculename, extended=True)
    _, hashname, _, _, _ = getFullModuleName(gmxfile)  
    return "%s.%s_%s"%("models", moleculename.lower(), hashname)

# def loadModule(modulefile, pptyname="", targets=None, all=False):
#     OK = True
#     libmgr = LibManager(modulefile)
#     if not libmgr.hasLib():
#         return None
#     try:
#         modtype = libmgr.moduleType
#         if all:
#             OK = libmgr.codeVersionOK()
#     except Exception as ex:
#         modtype = 0
#     libmgr.__del__()
#     
#     #import monal.driver as mdriver
#     if modtype == 2:
#         model = DriverMultiDyn(modulefile)
#         if targets is not None:
#             model.targets = targets
#     elif modtype == 1:
#         model = ModelLib(modulefile)
#     else:
#         return None
#     if pptyname:
#         model.propertyName = str(pptyname)
#     if all:
#         return model, OK
#     return model
# 
# def ReadModule(modulefile, pptyname, targets=None, dodelete=False):
#     if isinstance(modulefile, str):
#         res = loadModule(modulefile, pptyname, targets, all=True)
#         if res is None:
#             return None, None, False
#         model, OKversion = res
#     else:
#         model = modulefile
#         OKversion = True
#     dic = None
#     if model is not None:
#         dic = model.dict()
#     if dodelete:
#         del model
#         return dic, OKversion
#     return model, dic, OKversion

def ReadAndCheckModule(modulefile, pptyname=None, targets=None, hidden=0, 
        modelcount=-1, verbose=3, debug=0):
    modulefile = unquote(modulefile)
#     try:
#         if ((modulefile.startswith("'") and modulefile.endswith("'")) or 
#             (modulefile.startswith('"') and modulefile.endswith('"'))):
#             modulefile = modulefile[1:-1]
#     except: pass
    if not isinstance(modulefile, str):
        return [ReadAndCheckModule(mod, pptyname, targets, hidden, modelcount, verbose) for mod in modulefile]
            
    result = 0
    model, dic, OKversion = ReadModule(modulefile, pptyname, targets)
    if not OKversion:
        result |= 1
    
    if (model is None):
        res = False
        st = "Loading %s failed\n"% modulefile
    else:
        res = model.propertyName == pptyname
        if modelcount >= 0:
            res = res and model.modelCount == modelcount
        res = res and model.hidden == hidden
        st = ""
        if verbose >= 2:
            if not OKversion:
                st = "%s is outdated\n"% modulefile
            if verbose >=4:
                st = "%s%s\n" % (st, model.repr('short'))
            else:
                st = "%s%s\n" % (st, model.repr('veryshort'))
        if debug & DEMO_DEBUG_MODEL:  
            lst = ["parameters from module"]
            lst2 = ["{0}\t{1}".format(ind, val) for ind, val in enumerate(list(model.parameterNames))]
            lst.extend(lst2) 
            st = st + "\n\t".join(lst) + "\n"
            #wlist = model.    
        del model
    if not res:
        result |= 2
    return result, st, dic

# def TransferModule(modulefile, pptyname, targets, weight=None, style=0):
#     model = loadModule(modulefile, pptyname, targets)
#     res = TransferModel(model, weight, style)
#     del model
#     return res
    
def TransferModel(model, weights=None, style=0):
    res = None
    if weights is None:
        n = model.paramCount
        weights = [0.01 for _ in range(n)]
    if weights.ndim == 1:
        if style == 2:
            res = model.getPRESS(weights, full=True) #, trainstyle=trainstyle
        elif style == 1:
            res = model.getCost(weights, trainstyle=0)
        else:
            res = model.getresiduals(weights, style=0)
    elif weights.ndim == 2:
        res = [TransferModel(model, weight, style) for weight in weights]            
    return res

def TransferJacobian(modulefile, pptyname, targets, weight=None):
    model = loadModule(modulefile, pptyname, targets)
    res = None
    if weight is None:
        n = model.paramCount
        weight = [0.01 for _ in range(n)]
    res = model.getjacobian(weight, style=1)
    #del model
    return res
        
# to-do : fonction get_result_from_smiles  averc parallelism
def get_results_from_smiles(modellist, inputs=None, level=0, 
                            modelindex=-1, parallel=True, progress=None):
    """Create graphmachine models and obtain their results.
    
    parameters:
     - modellist -> list of triplets (sourcefile, model name, smiles code) to perocess.
     - inputs -> None, vector or dictionary
         - None : no input values (default).
         - vector : vector of the input values, in the order of the inputs.
         - dictionary: input value for each input name.
     - level -> level of the required transfer.    
     - modelindex -> Index of the model used in the extra model list. For -1 value, the mean model is used.
     - parallel -> if True, the computation will be processed in parallel mode
    
    return depending on level value :
        - 0 -> return a list of the best approximation of the required result
        - 1 -> return a list of the absolute minimum value, best value, absolute maximum value
        - 2 -> return a list of the list of (minimum, value, maximum) for each extra model
    """
    maxworkers = -2
    max_workers = maxWorkers(maxworkers)
    if parallel and max_workers > 1:
        result = [None for _ in modellist]
        with cf.ProcessPoolExecutor(max_workers=max_workers) as executor: 
            futures = [executor.submit(_usageJob, ind, 
                sublist, inputs, level, modelindex) 
                for ind, sublist in enumerate(modellist)]
            for indloc, future in enumerate(cf.as_completed(futures)):
                try:
                    ind, modname, res = future.result()
                except:
                    res = (0,0,0)
                    modname = ""
                    ind =indloc
                result[ind] = modname, res 
                if progress:
                    progress(indloc)           
    else:
        result = []
        for ind, sublist in enumerate(modellist):
            indloc, modname, res = __usageJob(ind, sublist, 
                                             inputs, level, modelindex)
            result.append((modname, res))
            if progress:
                progress(indloc)           
    return result

#----------- DEMO --------------------------------------------------------------

def _drawResult(modulename, pptyname, dataframe, datarange="", testframe=None, 
        testrange="", resindex=0, propertyname="", fontsize=16):
    """Presentation des resultats de dataframe et testframe sur une figure 
    matplotlib avec 4 graphes.
    """
    if not OKmatplotlib:
        raise Exception("_drawResult cannot be used without matplotlib")
    plt.close('all')
    richestimatedstr = _linkstr(estimatedstr, pptyname)
    mini = min(dataframe[targetstr])
    maxi = max(dataframe[targetstr])
    delta = maxi - mini
    maxi = maxi + 0.05 * delta
    mini = mini - 0.05 * delta
    
    if testframe is not None:
        figtitle = "%s | %s | %s #%s - %s"% (modulename, datarange, testrange, 
            resindex, propertyname)
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, 
            num=figtitle, figsize=(15, 12))
    else:
        figtitle = "%s | %s #%s - %s"% (modulename, datarange, resindex, propertyname)
        fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, num=figtitle)
    
    target = DataFrame([dataframe[targetstr], dataframe[_linkstr(richestimatedstr, resindex)]]) 
    ax1.scatter(target.ix[0], target.ix[1])
    ax1.plot([mini, maxi], [mini, maxi])
    ax1.set_ylabel(richestimatedstr, fontsize=fontsize) 
    ax1.set_xlabel(targetstr, fontsize=fontsize)
    ax1.set_title(datarange, fontsize=fontsize+2)
    
    draw_stat(ax1, target, 'StdDev')
    draw_stat(ax1, target, 'R2', (0.05, 0.9))

    target = DataFrame([dataframe[targetstr], dataframe[_linkstr("VLOO", resindex)]])
    ax2.scatter(target.ix[0], target.ix[1])
    ax2.plot([mini, maxi], [mini, maxi])
    ax2.set_xlabel(targetstr, fontsize=fontsize)
    ax2.set_ylabel("VLOO", fontsize=fontsize)
    ax2.set_title(datarange, fontsize=fontsize+2)
    
    draw_stat(ax2, target, 'StdDev')
    draw_stat(ax2, target, 'R2', (0.05, 0.9))
    
    if testframe is not None:
        target = DataFrame([testframe[propertyname], testframe[richestimatedstr]])
        ax3.scatter(target.ix[0].as_matrix().flat, target.ix[1].as_matrix().flat)
        ax3.plot([mini, maxi], [mini, maxi])
        ax3.set_xlabel(targetstr, fontsize=fontsize)
        ax3.set_ylabel("%s mean"% richestimatedstr, fontsize=fontsize) 
        ax3.set_title(testrange, fontsize=fontsize+2)
            
        draw_stat(ax3, target, 'StdDev')
        draw_stat(ax3, target, 'R2', (0.05, 0.9))
    
        keyList = [key for key in testframe.keys() if key.startswith( estimatedstr + "_")]
        target = DataFrame([testframe[propertyname], testframe[keyList[0]]])
        ax4.scatter(target.ix[0], target.ix[1])
        # ajouter ici le IC ???
        ax4.plot([mini, maxi], [mini, maxi])
        ax4.set_xlabel(targetstr, fontsize=fontsize)
        ax4.set_ylabel("%s best"% richestimatedstr, fontsize=fontsize) 
        ax4.set_title(testrange, fontsize=fontsize+2)
    
        draw_stat(ax4, target, 'StdDev')
        draw_stat(ax4, target, 'R2', (0.05, 0.9))

    plt.tight_layout()
    plt.show()
    
    return fig

        
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    modulefile = '/Users/jeanluc/docker/alpine_based_gm/workdir/libbjma271emos_si3_grds5_5n.soç'
    modulefile = '/Users/jeanluc/Public/Drop Box/libb200_11rt_br1_h_grd23455_5n_ce5.so'
    result, st, dico = ReadAndCheckModule(modulefile, pptyname="TS", hidden=5, verbose=4,  debug=DEMO_DEBUG_MODEL)
    print(st)
    print("OK")
    
    print("done")
