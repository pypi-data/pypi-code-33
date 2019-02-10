#-*- coding: ISO-8859-15 -*-
# $Id: gmmEngine.py 4280 2016-10-20 15:31:56Z jeanluc $
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
'''
Created on 18 oct. 2013

@author: jeanluc

gmmEngine is a module dedicated to the gmx files, used to save the result of a 
graphmachine training on a training database.
The aim of this gmx file is to allow a property estimation on a given molecule, 
or collection de molecules, following the training on a training database.

The creation of a gmx file uses the numpy.savez procedure. See :
"https://docs.scipy.org/doc/numpy/reference/generated/numpy.savez.html"

Internally, it uses monaltoolbox.saveToFilez procedure to save the content of a 
dictionary in a file. The dictionary uses the following keys :
    'config'          : ConfigParser of model bulding and training, saved as object
    'propertyname'    : Name of the modelized property
    'paramnames'      : list of parameter names
    'outputnorm'      : Output normalization
    'paramcount'      : Number of parameters
    'baselen'         : Number og samples in training data base
    'epochs'          : Epoches of training
    'dispersion'      : Fisher dispersion matrix of the model
    'initparams'      : Initialization parameter vector
    'params'          : Trained parameter vector 
    'stddev'          : RMSE after training
    'indexes'         : List of training best results, by increasing VLOO score
    'extracount'      : Number of extra training results
    'extraweights'    : Matrix grouping the trained parameter vectors of extra trainings
    'extradispersion' : Tensor grouping the dispersion matrix of extra trainings
    'suffix'          : Suffix for saving filenames
just added
    'classif'         : classification model
    'hidden'          : number og hidden neurons
    'mol1'            : limiting number of connection to number of molecules minus 1
    'root'
    'fullhydrogen'
    'atoms'
    'grademax'
    'isomax'
    'chiralmax'
    'extras'
    'extraXXX'
    'connectivity_XX'
    'occurence_XX'
    'exoccurence_XX'
obsolete    
    'halfdispersion'  : obsolete
    'extrahalfdispersion' : obsolete
    
Useful parts of config are (from GMmodel.AdjustFromConfig):
    ("model", "classif")
    ("model", "hidden")
    ("model", "mol1")
    ("general", "root")
    ("general", "fullhydrogen")
    ("general", "atoms")
    ("general", "grademax")
    ("general", "isomax")
    ("general", "chiralmax")
    ("general", "extras")
    ("general", "extraXXX") for all XXX
    ("general", "source")
    ("general", "sourcerange")
    
    ("connectivity", all)
    ("occurence", all)
    ("exoccurence", all)

for example, the content of a config is given below:
[general]
fullhydrogen = False
simpledispersion = False
verbose = 0
sourcetype = xlsx
format = 0,1,2
cyclemax = 2
chargemin = 0
chargemax = 0
lines = 269
grademax = 4
skipline = 0
source = /docker/data/BJMA269EMOL.xlsx
delimiter = ;
isomax = 2
chiralmax = 0
sourcerange = DATA
atoms = C,O,Si
root = BJMA269EMOL

[model]
compiler = 
hidden = 5
mergeisochiral = False
mol1 = True
isomeric_algo = 1
maxneuron = 15
hiddenmax = 20
central = C,O,Si

[connectivity]
h = -1
c = 5
si = 3
o = 5

[private]
keeptemp = 
compactness = 3
moduletype = dll

[occurence]
c = 1997, 269
si = 51, 15
o = 405, 197

[exoccurence]
degree(3) = 320, 137
cycle(3) = 3
degree(4) = 235, 151
cycle(2) = 72
cycle(1) = 194
isomer(1) = 5, 2
isomer(2) = 3, 1
degree(1) = 636, 249
degree(2) = 1262, 253

[training_TS]
initialization = 150
epochs = 100
resultdirectory = /Users/jeanluc/workdir
criterion = 2
initstddev = 0.1
seed = 715857310

    
    
'''# ici aussi

from tempfile import mkdtemp
from zipfile import ZipFile, ZIP_DEFLATED
import os #, sys
import ctypes
import numpy as np
import sqlite3 as sql
import datetime
from time import time

from six import string_types
from ...monal.Property import Property
from ...monal import monalconst as C 
from .. import __version__ as chem_gm_version
from ..core import metamolecule as meta
from ..core.GMmodel import smiles2model
from ..core.gmutils import getConfigHash, key2short #, decorstring
from collections import defaultdict
from ...nntoolbox.filetoolbox import getDictFromGmx
from ...nntoolbox.utils import tableTemplate, RE_LOO
from ...nntoolbox.sqlite_numpy import getDataFromDb, getTableCountFromDb, \
    getIndexesFromDb, getFieldList
from ...nntoolbox.configparsertoolbox import defaultedConfigParser
from ...nntoolbox.utils import saveToFilez
from ...monal.util.utils import CCharOnlys
from ...monal.model import useCodeVersionOK, expectedPpty
from ...nntoolbox.filetoolbox import decorfile 

class gmxError(Exception):
    pass

class gmxExistError(gmxError):
    pass

class gmxReadError(Exception):
    pass

_paramparams = ["extracount", "extraweights", "extrahalfdispersion", "params", 
                "dispersion", "extradispersion", "halfdispersion", 
                "propertyname", "outnorm", "baselen", "stddev"]

def getGmxInfo(filename, fieldlist=[]):
    if not len(fieldlist):
        fieldlist = _paramparams
    dico = getDictFromGmx(filename)
    lst = []
    for key in fieldlist:
        val = dico[key]
        st = "%s -> %s" %(key, repr(val))
        lst.append(st)
    return "".join(lst)
               
    

def getGmmDimension(hidden, connect, lensticker = 0, atomoccur={}, mol1=True, debug=False):
    """Calcul de la dimension du modele.
    """
    if not hidden:
        hidden = 1
        dim = 2 + lensticker
    else:
        dim = hidden * (hidden + 2 + lensticker) + 1
    # dimension de base (RN)
    
    connectedkeys = {key: hidden if value < 0 else min(value, hidden) for key, value in connect.items() if value and key in atomoccur.keys() and not key in ["C", "dgr1"]}
    for key, value in connectedkeys.items():
        # le nb d'occurence de molecule ayant la structure ou l'atome
        admitted = int(atomoccur[key].split(",")[0])
        if mol1 and admitted:
            admitted -= 1
        # admitted = min(admitted, hidden)
        # admitted is the authorized number of connection for "key"
        value = min(value, admitted)
        connectedkeys[key] = value

    dim  += sum(connectedkeys.values())#iter
    if debug:
        print()
        print(connectedkeys)
    return dim
    
def getdatafromarchive(gmxfile, keys):
    """Extract numpy data from archive file:
    gmxfile -> archive file name;
    keys -> key or key iterable for data retrieving.
    """
    try:
        with np.load(gmxfile) as source:
            if isinstance(keys, string_types):
                target = source[keys].copy()
            else:
                target = []
                for key in keys:
                    try:
                        target.append(source[key].copy())
                    except:
                        target.append(None)
    except:
        target = None
    return target

def getModuleNameComponents(source=None):
    """Depuis le fichier gmx, calcule les noms suivants:
    - resst -> le codage compact de la configuration du modele
    - reshash -> le code hash du précédent
    - ppty -> le nom de la propriété 
    - suffix -> le suffixe d'apprentissage/sauvegarde
    """
    suffix = ""
    config = None
    basename = ""
    if isinstance(source, string_types):
        with np.load(source) as sourceloc:
            return getModuleNameComponents(sourceloc)
    try:
        sourceloc = source
        ppty = str(sourceloc["propertyname"])
    except:
        sourceloc = source['root']
        ppty = str(sourceloc["propertyname"])
    if "suffix" in sourceloc.keys():
        suffix = sourceloc["suffix"]
    if "config" in  sourceloc.keys():
        try:
            config = sourceloc["config"].item()
        except:
            config = sourceloc["config"]
    elif "config" in  source.keys():
        try:
            config = source["config"].item()
        except:
            config = source["config"]
    if "basename" in sourceloc.keys():
        basename = sourceloc["basename"]
        
    if not suffix and isinstance(source, string_types):
        base = os.path.basename(source)
        base, _ = os.path.splitext(base)
        n = base.rfind("_")
        if n >= 0:
            suffix = base[n+1:]
    resst = ""
    reshash = ""
    if config is not None and not isinstance(config, np.ndarray):
        reshash, resst = getConfigHash(config, True)

#     reslong = ctypes.c_size_t(hash(resst)).value
#     reshash = str(reslong)
    
    return resst, reshash, ppty, suffix, basename
    
    #atomlist = [atom + str(config.get("co nnectivity", atom)) for atom in atomlist]
    #st = "".join([atom.capitalize() for atom in atomlist])

def getAvailableParamFiles(basepath, rootname, ppty="", ext=".npz"):
    if ppty:
        base = "%s_%s"%(ppty.lower(), rootname.lower())
    else:
        base = rootname.lower()
    #path = os.path.dirname(self.mainModule.__file__)
    _, _, filelst = os.walk(basepath).next()
    filelst = [filen.lower() for filen in filelst]
    filelst = [filen for filen in filelst if filen.endswith(ext)]
    filelst = [filen for filen in filelst if (filen.find(base) >= 0)]
    return filelst

def getRootName(gmxfile):
    modelname = ""
    source = np.load(gmxfile)
    if "root" in source.files:
        modelname = str(source["root"])
    source.close()
    if not modelname:
        modelname = getPythonModuleName(gmxfile)[2]
    return modelname

def createModelFromGmx(source, molname, smiles, givetime=False):
    # givetime sert au profilage
    if givetime:
        t0 = time() 
    if isinstance(source, string_types):
        dic = defaultdict(lambda: None)
        with np.load(source) as sourceloc:
            dic.update({key: value for (key, value) in sourceloc.items()})
    else:
        dic = source
    if "config" in dic.keys():
        try:
            config = dic["config"].item()
        except:
            config = dic["config"]
    else:
        config = defaultedConfigParser()
        config.add_section("general")
        config.add_section("model")
        config.add_section("connectivity")
        config.add_section("occurence")
        config.add_section("exoccurence")
        
        for section in ["model", "general", "connectivity", "occurence", "exoccurence"]:
            dico = dic[section].item() 
            for key, value in dico.items():
                config.set(section, key, str(value))
        
        
#         for key in ["classif", "hidden", "mol1"]:
#             if key in dic.keys():
#                 config.set("model", key, dic[key])
#         for key in ["root", "fullhydrogen", "atoms", "grademax", "isomax", "chiralmax"]:
#             if key in dic.keys():
#                 config.set("general", key, dic[key])
#         for key in dic.keys():
#             if key.startswith('extra'):
#                 config.set("general", key, dic[key])
#         for section in ["connectivity", "occurence", "exoccurence"]:
#             for key in dic.keys():
#                 if key.startswith(section):
#                     opt = key[len(section) + 1:]
#                     config.set(section, opt, dic[key])
    try:
        reseau = smiles2model(smiles, modelname=molname, config=config)
    except:
        try:
            hidden = config.getint("model", "hidden")
        except AttributeError:
            hidden = 0
        savingformat = C.SF_CPYTHON
        connect = defaultdict(lambda: hidden, {"chi1":0, "chi2":0, "iso1":0, 
            "iso2":0, "qp4":0, "qp3":0, "qp2":0, "qp1":0, "qm1":0, "qm2":0, 
            "qm3":0, "qm4":0})
        #fullH = config.getint("model", )
        try:
            st = config.get("general", "fullhydrogen").lower()
        except:
            st = False
        fullH = not st in ["no", "false", "0"]
        reseau = smiles2model(smiles, modelname=molname, #truename=truename, 
            hidden=hidden, connect=connect, savingformat=savingformat, 
            fullH=fullH)
    if not reseau:
        print("cannot create model %s with %s from smiles %s" % (molname, source, 
            smiles))
        return None
    if givetime:
        t1 = time() 
    reseau.loadFromDict(dic)
#     if reseau.outNormModel is None:
#         reseau.outNormModel = reseau.outputnorm
    try:
        wdir = os.path.basename(config.getdefault("general", "workingdir", ""))
    except AttributeError:
        wdir = ""
    reseau.basename = wdir
    if givetime:
        t2 = time() 
        return reseau, t1 - t0, t2 - t1
    return reseau

def getPythonModuleName(gmxfile, molname="", prefix="", suffix="auto"): 
    #config = None
    ppty = ""   
    with np.load(gmxfile) as source:
        config = source["config"].item()
        if "propertyname" in source.keys():
            ppty = str(source['propertyname'])
    module = os.path.splitext(config.getdefault("general", "module", ""))[0]
    wdir = os.path.basename(config.get("general", "workingdir")) 
    ppty = ppty if ppty else "unknown"
    package = "models.%s.%s" % (ppty, wdir)
    if suffix == "auto":
        package = "models"
        suffix = os.path.splitext(os.path.basename(gmxfile))[0]
        #if suffix.startswith(ppty):
        #    suffix = suffix[len(ppty):]
        if suffix.startswith("_"): 
            suffix = suffix[1:] 
    
    if molname:
        modelname = "%s%s_%s"%(prefix, molname, module)
    elif prefix:
        modelname = "%s_%s"%(prefix, module)
    else:
        modelname = module
    fullname = "%s.%s" %(package, modelname.lower())
    return fullname, package, modelname, suffix

def createPythonModule(source, molname, smiles, prefix="", suffix="auto", 
        keeptemp=0, createparamfile=False, verbose=0, compiler="", 
        forcelib=False):
    """Creation d'un module python compilé.
    """
    if isinstance(source, string_types):
        with np.load(source) as sourceloc:
            return createPythonModule(sourceloc, molname, smiles, prefix, suffix, 
                keeptemp, createparamfile, verbose, compiler, forcelib)
    reseau = createModelFromGmx(source, molname, smiles)     
    resname, reshash, _, _, basename = getModuleNameComponents(source)
    
    filename = "%s_%s"%(molname.lower(), reshash) 
    package = "models" 
    fullname = "%s.%s"%(package, filename)
    reseau.mainModel.trueName = reseau.mainModel.name
    reseau.mainModel.name = filename
    reseau.mainModel.originallink = False
    reseau.mainModel.configuration = resname
    reseau.mainModel.originbase = basename
    reseau.mainModel.date = datetime.datetime.now()
    try:
        reseau.mainModel.mark = "Model created with chem_gm %s" % chem_gm_version  #version()
    except:
        reseau.mainModel.mark = ""
    reseau.saveModel(filename="", savingformat=C.SF_CPYTHON, count=0, 
        savedir=None, tempdir=None, package=package, modeltemplate="m%d_", 
        compiler=compiler, keeptemp=keeptemp, verbose=verbose, 
        forcelib=forcelib)
    #st = "%s.%s" %(package, reseau.mainModel.name.lower())
    reseau.mainModel.name = molname
    return fullname
 
def createGMModel(source, molname, smiles, truename=""):  #savedir=None, 
    reseau = createModelFromGmx(source, molname, smiles) 
    resname, reshash, _, _, basename = getModuleNameComponents(source)
#     package = savedir 
    filename = "%s_%s"%(molname.lower(), reshash)
    reseau.mainModel.trueName = truename if truename else reseau.mainModel.name
    reseau.mainModel.name = filename
    reseau.mainModel.originallink = False
    reseau.mainModel.configuration = resname
    reseau.mainModel.originbase = basename
    reseau.mainModel.date = datetime.datetime.now()
    try:
        reseau.mainModel.mark = "Model created with chem_gm {0}".format(chem_gm_version) 
    except:
        reseau.mainModel.mark = ""
    return reseau
    
def createPythonDll(source, molname, smiles, truename="", prefix="", 
        suffix="auto", savedir=None, keeptemp=0, createparamfile=False, 
        verbose=0, compiler="", forcelib=False):
    """Creation d'une librarie compilée.
    """
    if isinstance(source, string_types):
        with np.load(source) as sourceloc:
            return createPythonDll(sourceloc, molname, smiles, truename, prefix, 
                suffix, savedir,  keeptemp, createparamfile, verbose, compiler, 
                forcelib)
#     reseau = createModelFromGmx(source, molname, smiles) 
#     resname, reshash, _, _, basename = getModuleNameComponents(source)
    package = savedir 
#     filename = "%s_%s"%(molname.lower(), reshash)
#     reseau.mainModel.trueName = truename if truename else reseau.mainModel.name
#     reseau.mainModel.name = filename
#     reseau.mainModel.originallink = False
#     reseau.mainModel.configuration = resname
#     reseau.mainModel.originbase = basename
#     reseau.mainModel.date = datetime.datetime.now()
#     try:
#         reseau.mainModel.mark = "Model created with chem_gm %s" % chem_gm.__version__  #version()
#     except:
#         reseau.mainModel.mark = ""
    reseau = createGMModel(source, molname, smiles, truename=truename)  #savedir=savedir, 
    modulename = reseau.saveModel(filename="", savingformat=C.SF_DLL, count=0, 
        savedir=savedir, tempdir=None, package=package, modeltemplate="m%d_", 
        compiler=compiler, keeptemp=keeptemp, verbose=verbose, 
        forcelib=forcelib)
    reseau.mainModel.name = molname
    return os.path.join(savedir, modulename)

def getSaveDictSingle(reseau, nameModel, index, nocheck, connection, Extra_Type, 
        nameBS, nameLOO, LOOcriterion, sqlfilenameBS, gminit={}):
    gm0 = gminit
#    gm1 = {} 
    internal = not isinstance(connection, sql.Connection)
    if internal:
        conn = sql.connect(connection, detect_types=sql.PARSE_DECLTYPES)
    else:
        conn = connection
    inds = getFieldList(conn, "trainingResult")
    indexname = "ID" if 'ID' in inds else "ind"
    res = getDataFromDb(conn, index=index, indexname=indexname)   # ici correction du 16/12/15 
    if internal:
        conn.close()
    try:
        gm0['epochs'] = res['epochs']
    except KeyError:
        gm0['epochs'] = res['Epochs']
    gm0['dispersion'] = res['dispersion']
    gm0['initparams'] = res['param_start']
    gm0['params'] = res['param_end']
    gm0['stddev'] = res['StdDev']
    
    try:
        try:
            presses = res["PRESS"]
        except:
            presses = reseau.presses
    except:
        presses = None
    gm0["presses"] = presses
    try:
        cond = reseau.hasResampling
    except AttributeError:
        try:
            cond = reseau.info[C.HAS_RESAMPLING]
        except AttributeError:
            cond = False
    cond = cond or nocheck
    try:
        leverages = res["leverage"]
        try:
            leverages = reseau.leverages
        except:
            leverages = None
    except:
        leverages = None
    gm0["leverages"] = leverages
#    gm0.update(gm1)
    #suffix = ""
    n = 0
    if cond:
        n = 1
        if Extra_Type == 1:  # cas Bootstrap
            gm0["BSweights"] = reseau.extraweights
            try:
                leverages = reseau.leverages
            except:
                leverages = None
            nameModel = nameBS #"%s%d%s" %(nameModel, s elf.BS_Count, s elf.extendedSuffix(s elf.startBestParamBS, s elf.BS_initcount))
             
        elif Extra_Type == 2:  # cas LOO
            try:
                nn = reseau.extraCount
                nparam = reseau.paramCount
            except:
                nn = 0
            nameModel = nameLOO  
            orderfield = C.criterFields[LOOcriterion]
            outfields = ["param_end", "leverages"]
            with sql.connect(sqlfilenameBS, detect_types=sql.PARSE_DECLTYPES) as conn:
                if not nn and nocheck:
                    nn = getTableCountFromDb(conn, tablestart="LOO")
                extraweightslist = np.zeros((n, nn, reseau.paramCount))
                leverages = np.zeros((n, nn))
                for initindex in range(nn):
                    tablename = tableTemplate[RE_LOO] % initindex
                    res = getIndexesFromDb(conn, 
                        table=tablename, outfield=outfields, 
                        orderfield=orderfield)
                    for ind, resloc in [(ind, resloc) for ind, resloc in enumerate(res) if ind < n]:
                        extraweightslist[ind][initindex] = resloc[0]  
                        leverages[ind][initindex] = resloc[1]  
                                     
            if np.any(extraweightslist):                               
                gm0["LOOweights"] = extraweightslist[:n,:,:]                            
            else:
                gm0["LOOweights"] = extraweightslist
     
    if leverages is not None:
        if n == 1:
            gm0["LOOleverages"] = leverages[0]
        else:
            nmin = min(n, extraweightslist.shape[0])
            gm0["LOOleverages"] = leverages[:nmin,:]
    gm0["paramcount"] = reseau.paramCount
    gm0["suffix"] = str(index)

    return gm0, nameModel
      
# def getSaveDictMulti(indexlist, connection, gminit={}, extrasize=-1): 
#     if indexlist is None:
#         index0 = -1
#     else:
#         index0 = int(indexlist[0]) 
#     gm0 = gminit  
#     if isinstance(connection, sql.Connection):
#         conn = connection
#         internal = False
#     else:
#         conn = sql.connect(connection, detect_types=sql.PARSE_DECLTYPES)
#         internal = True
#     inds = getFieldList(conn, "trainingResult")
#     indexname = "ID" if 'ID' in inds else "ind"
#     res = getDataFromDb(conn, index=index0, indexname=indexname , fieldlist="*")  # ici aussi correction du 16/12/15  
#     try: gm0['epochs'] = res['Epochs']
#     except KeyError: gm0['epochs'] = res['epoch']
#     gm0['dispersion'] = res['dispersion']
#     gm0['initparams'] = res['param_start']
#     gm0['params'] = res['param_end']
#     gm0['stddev'] = res['StdDev']
#     gm0["indexes"] = indexlist
#     paramsize = res['param_end'].shape[0]
#     internalextra = extrasize < 0
#     if internalextra:
#         internalextra = True
#         extrasize = len(indexlist)
#     if extrasize > 1:
#         gm0["extracount"] = extrasize
#         extraweights = np.zeros((extrasize, paramsize))
#         extradispersion = np.zeros((extrasize, paramsize, paramsize))
#         #extrahalfdispersion = np.zeros((extrasize, paramsize, paramsize))
#         if internalextra:
#             for ind, index in enumerate(indexlist):
#                 res = getDataFromDb(conn, index=index, indexname=indexname, fieldlist=['param_end', 'dispersion', 'ID'])    
#                 extraweights[ind] = res["param_end"]
#                 extradispersion[ind] = res["dispersion"]
#             gm0["extraweights"] = extraweights 
#             gm0["extradispersion"] = extradispersion
#         else:
#             nn = getTableCountFromDb(conn, tablestart="trainingResults")
#             nl = getTableCountFromDb(conn, tablestart="LOO")
#             nb = getTableCountFromDb(conn, tablestart="BS")
#             if nn:
#                 for ind in range(extrasize):
#                     tablename = C.tableTemplate[''] % ind
#                     res = getDataFromDb(conn, table=tablename, orderfield="PRESS", maxrec=1, fieldlist=['param_end'])
#                     extraweights[ind] = res["param_end"]
#             elif nl:
#                 for ind in range(extrasize):
#                     tablename = C.tableTemplate['loo'] % ind
#                     res = getDataFromDb(conn, table=tablename, orderfield="PRESS", maxrec=1, fieldlist=['param_end'])
#                     extraweights[ind] = res["param_end"]
#             elif nb:
#                 for ind in range(extrasize):
#                     tablename = C.tableTemplate['bs'] % ind
#                     res = getDataFromDb(conn, table=tablename, orderfield="PRESS", maxrec=1, fieldlist=['param_end'])
#                     extraweights[ind] = res["param_end"]
#             gm0["extraweights"] = extraweights 
#             #gm0["extradispersion"] = extradispersion
#     gm0["suffix"] = "multi%d"%len(indexlist)
#     if internal:
#         conn.close()
#    
#     return gm0

def computeSmile(smile, source=None, molecule= "", modeldir="", extras=None, 
                 createparamfile=False, modeluse=True, moduletype='so',
                 keeptemp="", compiler=None, writer=None, givetime=False):

    truename = molecule 
    modelname = CCharOnlys(molecule, extended=True)
    modname, outputname, extension = getmodelname(smile, modelname, 
        source, root = "")
    modelname = modelname + extension
    
    path = modeldir  
    lst = modname.split('.')
    for val in lst[:-1]:
        path = os.path.join(path, val)
    finalpath = lst[-1]
    if not moduletype:
        if isinstance(source, string_types):
            with np.load(source) as sourceloc:
                return createModelFromGmx(sourceloc, modelname, smile, givetime=givetime), outputname, molecule, True  
        else:
            return createModelFromGmx(source, modelname, smile, givetime=givetime), outputname, molecule, True
    if (moduletype in ["so", "dylib"]) and not finalpath.startswith("lib"):
        finalpath = "lib%s"% finalpath            
    if not finalpath.endswith(".%s"% moduletype):
        finalpath = "%s.%s"% (finalpath, moduletype)
    finalpath = os.path.join(path, finalpath)
        
    cond = modeluse or not os.path.exists(finalpath) or \
        not expectedPpty(finalpath, "smiles", smile) or \
        not useCodeVersionOK(finalpath)
    
    if cond:
        try:
            modname = createPythonDll(source, modelname, smile, 
                truename=truename, savedir=path, keeptemp=keeptemp, #"$$$", #
                createparamfile=createparamfile, compiler=compiler)
        except Exception as err:
            if writer:
                writer(str(err) + "\n")            
    return finalpath, outputname, molecule, cond

def getmodelname(smile, molecule, source, root="models"):
    tokens = meta.MetaMolecule(smile)
    tcentral = tokens.getCentralAtom(smile)
    modelname = CCharOnlys(molecule, extended=True)
    if tcentral:
        extension ="_C%s"% tcentral.numero
    else: 
        extension = ""
    modelname = modelname + extension
    _, hashname, outputname, _, _ = getModuleNameComponents(source)
    if root:
        modname = "%s.%s_%s"%(root, modelname.lower(), hashname)
    else:
        modname = "%s_%s"%(modelname.lower(), hashname)
    return modname, outputname, extension
    
class GmmError(Exception):
    pass

class GmmEngine(object):
    '''
    Exploitation des formats gmm
    '''

    def __init__(self, gmmfile, mode="r"):
        '''
        Constructor
        '''
        self._gmfile = gmmfile
        self._mode = mode
        self._tempdir = ""
        self.gmmzip = None
        self.config = None
        
    def createModel(self, molname, smiles):
        st = self.weightFile
        reseau = smiles2model(smiles, modelname=molname, config=self.config)
        reseau.loadParameters(st) 
        wdir = os.path.basename(self.config.get("general", "workingdir"))
        reseau.basename = wdir
        return reseau
    
    def createPythonModule(self, molname, smiles, keeptemp=0, verbose=0, 
            forcelib=False):
        reseau = self.createModel(molname, smiles)
        ppty = reseau.propertyName
        ppty = ppty if ppty else "unknown"
        wdir = reseau.basename
        package = "models.%s.%s" % (ppty, wdir) 
        reseau.saveModel( filename="", savingformat=C.SF_CPYTHON, count=0, 
            savedir=None, tempdir=None, package=package, modeltemplate="m%d_", 
            keeptemp=keeptemp, verbose=verbose, forcelib=forcelib)
        return "%s.%s" %(package, reseau.name.lower())
    
    def readConfig(self):
        self.config = defaultedConfigParser(self.configFile)
    
    @property
    def filename(self):
        return self._gmfile
    
    @Property
    def curdir(self):
        return self._tempdir
    
    @Property
    def configFile(self):
        return os.path.join(self._tempdir, "config.cfg")
    
    @Property
    def weightFile(self):
        st = os.path.join(self._tempdir, "weight.npz")
        if os.path.exists(st):
            return st
        st = os.path.join(self._tempdir, "weight_0.npz")
        if os.path.exists(st):
            return st
        raise GmmError("cannot find weight file in %s"% self._gmfile)
    
    @Property
    def weightFileList(self):
        st = os.path.join(self._tempdir, "weight_0.npz")
        if not os.path.exists(st):
            return [self.weightFile]
        lst = []
        ind = 0
        while os.path.exists(st):
            lst.append(st)
            ind += 1
            st = os.path.join(self._tempdir, "weight_%d.npz"% ind)
        return lst
    
    def fullFile(self, filename=""):
        #filename = filename if filename else self.filename
        return os.path.join(self._tempdir, filename)
    
    def add(self, filename="", archname=""):
        if self._mode == "r":
            raise RuntimeError('"write" mode needed for GmmEngine.')
        if os.path.exists(filename):
            self._gmfile = filename
        if os.path.exists(self.filename):
            if archname:
                return self.gmmzip.write(self.filename, archname)
            return self.gmmzip.write(self.filename)
    
    def __enter__(self):
        self._tempdir = mkdtemp()
        self.gmmzip = ZipFile(self.filename, self._mode, ZIP_DEFLATED)
        if self._mode == "r":
            self.gmmzip.extractall(self._tempdir)
            self.readConfig()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._mode == "w":
            for _, _, files in os.walk(self._tempdir):
                for fil in files:
                    fullfil = os.path.join(self._tempdir, fil)
                    self.gmmzip.write(fullfil)
            self.gmmzip.close() 
        for _, _, files in os.walk(self._tempdir):
            for fil in files:
                fullfil = os.path.join(self._tempdir, fil)
                os.remove(fullfil)
        os.rmdir(self._tempdir)
        if exc_type:
            #stderr.write(exc_val + "\n")
            #stderr.write(exc_tb)
            return False
        return True
#===============================================================================

def getFullModuleName(gmxfile=None):
    """Depuis le fichier gmx, calcule les noms suivants:
    - resst -> le codage compact de la configuration du modele
    - reshash -> le code hash du prÈcÈdent
    - ppty -> le nom de la propriÈtÈ 
    - suffix -> le suffixe d'apprentissage/sauvegarde
    """
    suffix = ""
    if isinstance(gmxfile, string_types):
        source = np.load(gmxfile)
        #with np.load(gmxfile) as source:
        config = source["config"].item()
        ppty = str(source["propertyname"])
        if "suffix" in source.files:
            suffix = source["suffix"]
        source.close()
    else:
        source = gmxfile
        config = source["config"].item()
        ppty = str(source["propertyname"])
        if "suffix" in source.keys():
            suffix = source["suffix"]
        
    if not suffix and isinstance(gmxfile, string_types):
        base = os.path.basename(gmxfile)
        base, _ = os.path.splitext(base)
        n = base.rfind("_")
        if n >= 0:
            suffix = base[n+1:]
    atomlist = config.options("occurence")
    connectivities = config.options("connectivity")
    
    lst = []
    for item in connectivities:
        if item in atomlist:
            Item = item.capitalize()
        else:
            Item = key2short(item)
        valst = config.get("connectivity", item)
        if valst == "-1":
            lst.append(Item)
        elif valst != "0":
            lst.append(Item + valst)
    central = config.get("model", "central") 
    central = "|".join(central.split(","))
    lst.append("_%s"% central)
    classif = config.get("model", "classif")
    lst.append("_%s"%classif[0])
    hidden = config.get("model", "hidden")
    lst.append("_%sN"% hidden)
    resst = "_".join(lst)
    
    reslong = ctypes.c_size_t(hash(resst)).value
    
    reshash = str(reslong)
    return resst, reshash, ppty, suffix
    
    #atomlist = [atom + str(config.get("connectivity", atom)) for atom in atomlist]
    #st = "".join([atom.capitalize() for atom in atomlist])

# def getDictFromGmx(gmxfile):
#     if not os.path.exists(gmxfile):
#         raise gmxExistError("Cannot read gmx file %s"%gmxfile)
#     try:
#         dic0 = {}  #defaultdict(lambda: None)
#         with np.load(gmxfile) as sourceloc:
#             dic0.update({key: value for (key, value) in sourceloc.items()})
#         for key, value in dic0.items():
#             try:
#                 dic0[key] = value.item()
#             except: pass
#             
#         if not 'config' in dic0.keys(): 
#             config = defaultedConfigParser()  #SafeConfigParser
#             config.add_section("general")
#             config.add_section("model")
#             config.add_section("connectivity")
#             config.add_section("occurence")
#             config.add_section("exoccurence")
#             for section in ["general", "model", "connectivity", "occurence", 
#                             "exoccurence"]:
#                 if section in dic0.keys():
#                     sectiondic = dic0[section]
#                     for key, value in sectiondic.items():
#                         config.set(section, key, str(value))                
#             dic0['config'] = config        
#         return dic0
#     except:
#         raise
#         raise gmxReadError("Cannot analyse gmx file %s"%gmxfile)
#     
# def getGmxFileName(options, dosave=True):
#     decor = ['confstr']
#     for val in options.decor:
#         if not val in ['hash', 'levthresh', 'selectedcountex']:
#             decor.append(val)
#     for val in ['selectedcount', 'hidden']:
#         if not val in decor:
#             decor.append(val) 
#     indextemplate="(%d)" if dosave else ""
#     return decorfile(os.path.join(options.savedir, options.root), options, ".gmx", 
#         decor, indextemplate=indextemplate,  maxreconly=True)     

# def getReducedSelectedGmx(origin, newlen=1, originstr=""):
#     """Creation d'un fichier gmx avec reduction de la dimension des extra
#     """
#     if isinstance(origin, string_types):
#         originstr = origin
#         dico = getDictFromGmx(origin)
#     else:
#         dico = origin.copy()
#     curlen = int(dico['extracount'])
#     newfilename = ""
#     mess = ""
#     if newlen < curlen:
#         dico['extracount'] = newlen
#         try:
#             dico['extradispersion'] = dico['extradispersion'][:newlen]
#         except: pass
#         dico['indexes'] = dico['indexes'][:newlen]
#         dico['extraweights'] = dico['extraweights'][:newlen]
#         target = "_%dS"% curlen
#         newtarget = "_%dS"% newlen
#         try:
#             n = originstr.index(target)
#             base = originstr[:n]
#             follow = originstr[n+len(target):]
#             newfilename = "%s%s%s"% (base, newtarget, follow)
#         except ValueError:
#             base, ext = os.path.splitext(originstr)
#             newfilename = "%s%s%s"% (base, newtarget, ext)
# 
#         saveToFilez(newfilename, dico)
#     else:
#         mess = "Current gmx record len too small: %d should be smaller than %d\n"% (newlen, curlen)
#     return newfilename, mess
#         

if __name__ == "__main__":
    filename = "BJMA269EMOL_Si3_250T_150E_10S_5N.gmx"
    ppath = os.path.expanduser("~/workdir/BJMA269EMOL_321")
    filename = os.path.join(ppath, filename)
    print(getGmxInfo(filename, ["extradispersion"]))
#     filename = os.path.expanduser("~/workdir/BJMA269EMOL/BJMA269EMOL_Si3_150T_100E_70S_5N.gmx")
#     print "file :", filename
#     print "file exists :", os.path.exists(filename)
#     newfilename,mess = getReducedSelectedGmx(filename, 70)
#     print newfilename
#     
#     dic = getDictFromGmx(newfilename)
#         
#     for key in dic:
#         print key
#         if key in ['extraweights', 'extradispersion', 'indexes']:
#             print "len(%s)"%key, len(dic[key])
#         else:
#             print dic[key]
#         
#     
#     print 
    print("Done")
