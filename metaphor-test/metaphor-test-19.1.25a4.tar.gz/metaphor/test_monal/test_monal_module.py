#-*- coding: ISO-8859-15 -*-

import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=DeprecationWarning)

import os, sys
from six import PY2, PY3
from metaphor.monal import driver as dr, model as ml, monalconst as C

import numpy as np
from numpy.random import randn, seed
import tempfile, shutil
 
if sys.version_info >= (3,) :
    from io import BytesIO as Buffer
    import pickle
else:
    from StringIO import StringIO as Buffer 
    import cPickle as pickle

import unittest

DO_TEST_LIBMANAGER = 1  #PY3
DO_TEST_COMPILE_LIB = 0 # mettre à 0 pour les tests in situ
KEEP_TEMP = 1
VERBOSE = 3

testFileDir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testFiles'))
WW10 = np.zeros((10,))
WW22 = np.zeros((22,))

WW10[0] = -0.082809315501
WW10[1] = 0.031850099234
WW10[2] = 0.22031874646
WW10[3] = -0.082677520564
WW10[4] = 0.12634661626
WW10[5] = 0.050722452125
WW10[6] = 0.30215815791
WW10[7] = -0.17725213005
WW10[8] = 0.00022195270492
WW10[9] = 0.097634496696

WW22[0] = 0.039843524921
WW22[1] = -0.11974612107
WW22[2] = -0.048612387027
WW22[3] = -0.19084323523
WW22[4] = -0.084070986799
WW22[5] = -0.03008236605
WW22[6] = 0.069560996908
WW22[7] = 0.11159221823
WW22[8] = 0.047867121706
WW22[9] = 0.10994423754
WW22[10] = -0.094399533507
WW22[11] = -0.021777191667
WW22[12] = 0.080970843388
WW22[13] = -0.0061677630808
WW22[14] = 0.067246044709
WW22[15] = -0.0019394849107
WW22[16] = 7.11023083E-05
WW22[17] = 0.0015981840668
WW22[18] = 0.1199492128
WW22[19] = 0.097958760835
WW22[20] = 0.027484232802
WW22[21] = 0.16873545622

FileData_L153 = os.path.join(testFileDir, 'L_153.csv')
FileData_L153_Inverse = os.path.join(testFileDir, 'L_153_Inverse.csv')
FileData_L153_1 = os.path.join(testFileDir, 'L_153_1.csv')
FileWeight10 = os.path.join(testFileDir, 'PoidsNML10.nml')
NpWeight10 = os.path.join(testFileDir, 'WW10.npy')
FileData_Static = os.path.join(testFileDir, 'Static.csv')
FileData_Static2 = os.path.join(testFileDir, 'Static2.csv')
FileNet_MGL = os.path.join(testFileDir, 'test.mgl')
FileNet_DLM = os.path.join(testFileDir, 'testModel.dlm')
FileASCIIParams = os.path.join(testFileDir, 'PoidsASCII10.txt')
FileMML = os.path.join(testFileDir, 'testCost.mml')
FileMML2 = os.path.join(testFileDir, 'testCost2.mml')
targetname = os.path.join(testFileDir, 'target.nml')
targetbinname = os.path.join(testFileDir, 'target.net')
resultcsv = os.path.join(testFileDir, 'result.csv')
FileModelC = os.path.join(testFileDir, 'CModel.nml')
FileModelC2 = os.path.join(testFileDir, 'CNModel.nml')
FileModelC3 = os.path.join(testFileDir, 'CNOModel.nml')
FileModelN = os.path.join(testFileDir, 'NModel.nml')
FileModelO = os.path.join(testFileDir, 'OModel.nml')
FileModelN2 = os.path.join(testFileDir, 'NModel_2.nml')
FileModelO2 = os.path.join(testFileDir, 'OModel_2.nml')
FileModelGM = os.path.join(testFileDir, 'ModelGM.nml')
FileModelGM1 = os.path.join(testFileDir, 'ModelGM1.nml')
FileModelGM2 = os.path.join(testFileDir, 'ModelGM2.nml')
FileModelCompact = os.path.join(testFileDir, 'Model_001.nml')
FileModelGM2load = os.path.join(testFileDir, 'Model_020.nml')
FileParamGM2load = os.path.join(testFileDir, 'Weights_020.nml')
Unit_2N = os.path.join(testFileDir, 'Unit_2N.nml')
PathGM2 = os.path.join(testFileDir, 'ReseauxGM_Lin2')
PathGM3 = os.path.join(testFileDir, 'ReseauxGM_Lin3')  
#pathMultiDyn = os.path.join(testFileDir, "libbase109_chi1_grds5_5n.so")
#pathMultiDyn = os.path.join(testFileDir, "libbasea109_chi01n.so")
#pathMultiDyn = os.path.join(testFileDir, "libbasea109_chi01n.so")
#pathMultiDyn = os.path.join(testFileDir, "libbasea109_grd12341_1n.so")
LogKdFile = os.path.join(testFileDir, "LogKd-baseA109.txt")
#PathDLM = os.path.join(testFileDir, 'DLM_target')
#PathSurdim = os.path.join(testFileDir, 'logp_2n_bin_gmm')
    #TempName3 = UniqueFileName('.NET')

class NotYetImplemented(Exception):
    
    pass

def newModel(ne=1, ns=1, nc=3, activ='TANH', APolyType=0,
             ILayer=0, INeuron=0, NState=0, modelname="model_0", classif=False):
    return ml.Network(modelname=modelname, inputs=ne, outputs=ns, hidden=nc, 
                 activfunc=activ, polytype=APolyType, classif=classif, 
                 nosynapse=0)

def newDriver(ne=1, ns=1, nc=3, activ='TANH', APolyType=0,
             ILayer=0, INeuron=0, NState=0, modelname="model_0", classif=False):
    return dr.Driver(modelname=modelname, inputs=ne, outputs=ns, hidden=nc, 
                 activfunc=activ, polytype=APolyType, classif=classif,
                 nosynapse=0)
    
# class MonalBase0(unittest.TestCase):
#     def setUp(self):
#         self.TEST_FOLDER = tempfile.mkdtemp()
#  
#     def tearDown(self):
#         if os.path.exists(self.TEST_FOLDER):
#             shutil.rmtree(self.TEST_FOLDER)

class TestMonalBase(unittest.TestCase):
    # les premières lettres 'T' des procedures doivent etre remplacées par des
    # 't' minuscules pour activer les tests
    def setUp(self):
        self.TEST_FOLDER = tempfile.mkdtemp()
 
    def tearDown(self):
        if os.path.exists(self.TEST_FOLDER): # and not KEEP_TEMP:
            shutil.rmtree(self.TEST_FOLDER)
            try:
                os.rmdir(self.TEST_FOLDER)
            except: pass
    
    def testComments(self):
        model = newModel() 
        test1str = 'Premiere ligne de commentaire'
        test2str = 'Deuxieme ligne de commentaire'
        model.addComment(test1str)
        model.addComment(test2str)
        st = model.getComment(1)
        self.assertEqual(st, test2str)
        st = model.getComment(0)
        self.assertEqual(st, test1str)
        
    def testClassification(self):
        model = newModel(classif=True) 
        val = model.outputNodes[0].activation
        self.assertEqual(val, 'sig')

    def testAddSuppSynapse(self):
        model = newModel() 
#         n1 = model.layerLength(1)
#         self.assertEqual(n1, 3)
        d1 = model.dimension
        model.weights = [(ind + 1)*1.1 for ind in range(d1)]
#         for ind in range(d1):
#             model.weights[ind] = (ind + 1)*1.1
        self.assertEqual(d1, 10)
        res = model.deleteLink(4, 1, adjustweights=True)
        self.assertEqual(res, 5)
#         n2 = model.layerLength(1)
#         self.assertEqual(n2, 3)
        d2 = model.getTrueDimension()
        self.assertEqual(d2, 9)
        model.createLink(4, 1, linkid=res)
        d3 = model.getTrueDimension()
        self.assertEqual(d3, d1)
#         revoir createLink
#         for ind in range(d3):
#             self.assertEqual(model.weights[ind], (ind + 1)*1.1)

    def TestAddSuppNeuron(self):
        model = newModel() 
        raise NotYetImplemented
    
    def TestAddSuppLayer(self):
        model = newModel() 
        raise NotYetImplemented
        pass
    
    def TestFusion(self):
        raise NotYetImplemented

    def TestBoucle(self):
        raise NotYetImplemented
    
    def TestBoucleES(self):
        raise NotYetImplemented
    
    def TestNormalization(self):
        raise NotYetImplemented
        
class TestMonal(unittest.TestCase):
    
    def setUp(self):
        self.TEST_FOLDER = tempfile.mkdtemp()
 
    def tearDown(self):
        if os.path.exists(self.TEST_FOLDER) and not KEEP_TEMP:
            shutil.rmtree(self.TEST_FOLDER)
            try:
                os.rmdir(self.TEST_FOLDER)
            except: pass


    def testMultidyn(self):#1
        if KEEP_TEMP:
            self.TEST_FOLDER_2 = tempfile.mkdtemp()
        else:
            self.TEST_FOLDER_2 = self.TEST_FOLDER
        driver = newDriver(ne=5, nc=4)
        modulename = driver.saveModel(filename="", savingformat=C.SF_DLLTRAIN, #SF_DLLTRAIN
            count=0, savedir=self.TEST_FOLDER_2, tempdir=self.TEST_FOLDER_2, package="", 
            modeltemplate="m%d_", keeptemp=KEEP_TEMP, verbose=VERBOSE, compiler="", 
            forcelib=False, appliname="nn1")
        modulename = os.path.join(self.TEST_FOLDER_2, modulename)
        if DO_TEST_LIBMANAGER:
            model = dr.DriverMultiDyn(modulename)  #pathMultiDyn)
            self.assertEqual(model.name, "")
#            model.targets = LogKdFile
            self.assertEqual(model.paramCount, 29) #66)
            self.assertEqual(model.propertyName, "unknown") #"LogKdd-baseA109.txt")
            self.assertEqual(model.modelCount, 0)# 109)
            self.assertEqual(model.hidden, 4)
            self.assertEqual(model.base, "")#"Base109")
#             self.assertEqual(model.biasbased[0], 30)
#             self.assertEqual(model.biasbased[1], 36)
#             self.assertEqual(model.outlinks[0], 60)
#             self.assertEqual(model.outlinks[1], 61)
            self.assertAlmostEqual(model.outputnorm[0], 1.0, 6)#3.5837352, 6)
            self.assertAlmostEqual(model.outputnorm[1], 0.0, 6)#17.5587156, 6)
        else:
            pass
         
    def testMultiDynPickle(self):#2
        if KEEP_TEMP:
            self.TEST_FOLDER_2 = tempfile.mkdtemp()
        else:
            self.TEST_FOLDER_2 = self.TEST_FOLDER
        driver = newDriver(ne=5, nc=4)
        modulename = driver.saveModel(filename="", savingformat=C.SF_DLLTRAIN, # SF_DLLTRAIN
            count=0, savedir=self.TEST_FOLDER_2, tempdir=self.TEST_FOLDER_2, package="", 
            modeltemplate="m%d_", keeptemp=KEEP_TEMP, verbose=VERBOSE, compiler="", 
            forcelib=False, appliname="metaphor")
        modulename = os.path.join(self.TEST_FOLDER_2, modulename)
        if DO_TEST_LIBMANAGER:
            model = dr.DriverMultiDyn(modulename)#pathMultiDyn)
            self.assertEqual(model.name, "")
#            model.targets = LogKdFile
            memprop = model.propertyName
            stream = Buffer()
            pickle.dump(model, stream)
            stream.flush()
            #stream.seek(0)
            stream2 = Buffer(stream.getvalue())
            #stream.close()
            model2 = pickle.load(stream2)
            self.assertEqual(memprop, model2.propertyName)
            #model2.targets = LogKdFile
            self.assertEqual(model.propertyName, model2.propertyName)
            self.assertEqual(model.hidden, model2.hidden)
            self.assertEqual(model.paramCount, model2.paramCount)
            self.assertEqual(model.modelCount, model2.modelCount)
            self.assertEqual(model.base, model2.base)
            self.assertEqual(model.mark, model2.mark)
            self.assertEqual(model.monalVersion, model2.monalVersion)
#             self.assertEqual(model.outputnorm[0], model2.outputnorm[0])
#             self.assertEqual(model.outputnorm[1], model2.outputnorm[1])
    #         for val1, val2 in zip(model.targets, model2.targets):
    #             self.assertEqual(val1, val2)
    #             print val1
        else:
            pass
    
    def testModelName(self):#3
        model = newModel() 
        self.assertEqual(model.name, "model_0")
        model = newModel(modelname = "model_1") 
        self.assertEqual(model.name, "model_1")
        model.name = "mymodel"
        self.assertEqual(model.name, "mymodel")
    
    def testInOutNames(self):#4
        model = newModel(ne=3, ns=3) 
        self.assertEqual(model.inputNames[0], "IN_0")
        self.assertEqual(model.inputNames[1], "IN_1")
        self.assertEqual(model.inputNames[2], "IN_2")
        self.assertEqual(model.outputNames[0], "OUT_0")
        self.assertEqual(model.outputNames[1], "OUT_1")
        self.assertEqual(model.outputNames[2], "OUT_2")
        model.inputNames[1] = "titi"
        self.assertEqual(model.inputNames[1], "titi")
        model.outputNames[1] = "toto"
        self.assertEqual(model.outputNames[1], "toto")
    
    def testHiddenNames(self):#5
        model = newModel()
        hb = model.getNode(0)
        self.assertEqual(hb.name, 'bias')
        h00 = model.getNode(2)
        self.assertEqual(h00.name, 'H0_0')
        h0 = model.getNode((1, 0))
        self.assertEqual(h0.name, 'H0_0')
        h1 = model.getNode((1, 1))
        self.assertEqual(h1.name, 'H0_1')
        h000 = model.getNode('H0_0')
        self.assertEqual(h000.name, 'H0_0')        
        self.assertEqual(h0, h00)
        self.assertEqual(h0, h000)
    
    def testModelCreation(self):#6
        model = newModel() 
        self.assertEqual(model.name, "model_0")
        self.assertEqual(model.inputCount, 1)
        self.assertEqual(model.outputCount, 1)
        self.assertEqual(model.hiddenCount, 3)
        self.assertEqual(model.paramCount, 10)
        model = newModel(ne=5) 
        self.assertEqual(model.inputCount, 5)
        self.assertEqual(model.paramCount, 22)
        
    def testModelTransfer0(self):#7
        model = newModel(ne=3)
        ww = [0.01*i for i in range(16)]
        model.setWeights(ww)
        res = model.transfer([0,0,0])
        self.assertAlmostEqual(res, 0.1375714806, 10)
        seed(1947)
        ww = randn(16,)
        model.setWeights(ww)
        res = model.transfer()
        self.assertAlmostEqual(res,  0.2942158063, 10)
        
    def testModelTransfer(self):#8
        model = newModel()
        model.setWeights(WW10)
        res = model.transfer([0.0])
        self.assertAlmostEqual(res, 0.3291215143, 10)
        seed(1947)
        ww = randn(10,)
        model.setWeights(ww)
        res = model.transfer()
        self.assertAlmostEqual(res, 0.7444300349977917, 10)
        
    def testModelPrime(self):#9
        model = newModel(ne=3)
        ww = [0.01*i for i in range(16)]
        model.setWeights(ww)
        res = model.transfer([0,0,0], style=C.TFR_GRADIENT)
        self.assertAlmostEqual(res[0], 0.1375714806, 10)
        self.assertAlmostEqual(res[1][0], 0.13) #, 10)
        self.assertAlmostEqual(res[1][1], 0)  #, 10)
        self.assertAlmostEqual(res[1][-2], 0.039978680311, 10)
        self.assertAlmostEqual(res[1][-1], 0.079829769111, 10)
        self.assertAlmostEqual(res[2][0], 0.021702779243, 10)
        self.assertAlmostEqual(res[2][1], 0.025890982442, 10)
        self.assertAlmostEqual(res[2][2], 0.030079185641, 10)
        pass
        
    def testLoadWeights(self):#10
        model = newModel()  #
        res = model.loadParameters(FileWeight10)
        self.assertEqual(None, res, "load parameters NML")
        self.assertAlmostEqual(model.weights[0], -0.0299450274, 10)
        #np.save(NpWeight10, model._weights)
        
        model.initWeights()
        res = model.loadParameters(FileASCIIParams)
        self.assertEqual(None, res, "load parameters, ASCII")
        self.assertAlmostEqual(model.weights[0], 1.01, 10)
        
        model.initWeights()        
        res = model.loadParameters(NpWeight10)
        self.assertEqual(None, res, "load parameters Numpy")
        self.assertAlmostEqual(model.weights[0], -0.0299450274, 10)
        
    def testBoxLucasNoLoad(self):#11
        path = os.path.join(testFileDir, 'KINETIC_BOX_LUCAS.NML');
        datafile = os.path.join(testFileDir, 'BOXLUCAS.CSV');
        model = dr.Driver(path)
        self.assertTrue(model)
        self.assertFalse(model.loadParameters(datafile))
        
    def testSaveModelXML(self):#12
        driver = newDriver(5)
        driver.loadTrainingData(FileData_L153)
        test = list(driver.trainingData)[0]
        target = [ 28., 11., 18., 79., 17., 32.]
        for tt, tg in zip(test, target):
            self.assertEqual(tt, tg)
        tes = list(driver.trainingData)[-1]
        taget = [ 34., 31., 14., 78., 28., 23.]
        for tt, tg in zip(test, target):
            self.assertEqual(tt, tg)
        
#        self.assertEqual(, )
        filename = "toto.nml"
        fullfilename = os.path.join(self.TEST_FOLDER, filename)
        driver.saveModel(filename=filename, savingformat=C.SF_XML, savedir=self.TEST_FOLDER)
        assert os.path.exists(fullfilename)
        driver2 = dr.Driver(fullfilename)
        self.assertEqual(driver.inputCount, driver2.inputCount, "Input counts should be equal")
        self.assertEqual(driver.outputCount, driver2.outputCount, "Output counts should be equal")
        self.assertEqual(driver.mainModel.hiddenCount, driver2.mainModel.hiddenCount, "Hidden counts should be equal")

        #for val in driver.trainingData:
        #    print val
        
    def testSaveModelAsCode(self):#13
        driver = newDriver(5)
        driver.saveModel(savingformat=C.SF_CCODE, savedir=self.TEST_FOLDER)
        fullfilename = os.path.join(self.TEST_FOLDER, driver.name)
        #assert os.path.exists(fullfilename + ".c")
        assert os.path.exists(fullfilename + "_.h")
        assert os.path.exists(fullfilename + "_.c")
        assert os.path.exists(fullfilename + "usebase.h")
        assert os.path.exists(fullfilename + "usebase.c")

    def testSaveModelAsDll(self):#14
        #shutil.rmtree(self.TEST_FOLDER)
        self.TEST_FOLDER = tempfile.mkdtemp(prefix='toto')
        driver = newDriver(5)
        driver.setWeights(WW22)
        ni = driver.inputCount
        assert ni == 5
        inputs = randn(ni,)
        res1 = driver.transfer(inputs)
        tempdir = self.TEST_FOLDER
        modulename = driver.saveModel(savingformat=C.SF_DLL, 
            savedir=self.TEST_FOLDER, 
            keeptemp = KEEP_TEMP,
            tempdir=tempdir,
            forcelib=DO_TEST_COMPILE_LIB,
            verbose=VERBOSE)
        fullfilename = os.path.join(self.TEST_FOLDER, modulename)
        assert os.path.exists(fullfilename)
        driver2 = ml.ModelLib(fullfilename)
        assert driver2
        assert driver2.transfer(inputs=inputs) == 0.0
        res2 = driver2.transfer(WW22, inputs) 
        driver2.params = WW22
        res3 = driver2.transfer(inputs=inputs)
        assert res1 == res2 == res3
        driver2.outputnorm = (2, 1.55)
        assert driver2.outputnorm[0] == 2.0
        assert driver2.outputnorm[1] == 1.55
        res4 = driver2.transfer(inputs=inputs)
        assert res4 == 2 * res1 + 1.55
        driver2.__del__()

def run():
    unittest.main() 

#================================================
if __name__ == "__main__":

    run()