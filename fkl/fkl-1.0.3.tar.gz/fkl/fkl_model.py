# -*- coding: utf-8 -*-
"""
This is a submodule of fk_lib.
The moudle contains several classes to wrapped up model.
"""
from .fkl_io import *

class FKLVirtualModel:
    """
    This class is an virtual class, it must be inheritem then can use it. this
    class was built to suit up FKLTrainer and FKLTester.
    Attributes:
        _model: A regression/classification model.
    """
    def __init__(self):
        self._model=None
    def __call__(self,x):
        return self.Predict(x)
    def Fit(self,x,y,batch_size=1,epochs=1):
        """
        Args:
            x: A list that represent features of input.
            y: A list that represent target of output.
            batch_size: An integer that represent batch size of trainning.
            epochs: An integer that represent the circles of trainning.
        Returns:
            None
        Raises:
            None
        """
        self._model.fit(x,y,batch_size,epochs)
        return 
    def Save(self,save_path):
        """
        Args:
            save_path: A str that represent target path of save.
        Returns:
            None
        Raises:
            None
        """
        self._model.save_weights(save_path)
        return 
    def Read(self,read_path):
        """
        Args:
            read_path: A str that represent the path of reading weights.
        Returns:
            None
        Raises:
            None
        """
        self._model.load_weight(read_path)
        return 
    def Predict(self,x):
        """
        Args:
            x: A list that represent features of input.
        Returns:
            Return A list that represent target of prediction.
        Raises:
            None
        """
        pred_y=self._model.predict(x)
        return pred_y
    
class FKLTrainer:
    """
    This class was built to deal with trainning model.
    Attributes:
        _fkl_model: A object of FKLModel.
        _trainer_folder_path: A str that represent the path of trainer folder.
        _weights_path: A str that represent the path of weights, the arg will be 
                       automatic generated.
        _weights_record_path: A str that represent the json path of weights record.
        _eval_function: A function that to evalue y of true and y of prediction.
        _test_x: A list that represent features of test set's input.
        _test_y: A list that represent target of test set's output.
        _step_epochs: An integer that reoresent circles in every step.
        _record_dict: A dict that record the best result after eval.
    """
    def __init__(self,fkl_model,trainer_folder_path,step_epochs=10):
        self._fkl_model=fkl_model
        self._trainer_folder_path=trainer_folder_path
        self._weights_path=self._trainer_folder_path+"/weights"
        self._CheckFolder(self._weights_path)
        self._weights_record_path=self._trainer_folder_path+"/weights_record.json"
        self._eval_function=None
        self._test_x=None
        self._test_y=None
        self._step_epochs=step_epochs
        self._record_dict={}
        self._InitRecordDict()
    def _CheckFolder(self,folder_path):
        if(FKLCheckDir(folder_path)==False):
            FKLCreateDir(folder_path)
        return
    def _Record(self,epochs_num,compare_value):
        self._record_dict[epochs_num]=compare_value
        return
    def _GetBestEpoch(self):
        values=list(self._record_dict.values())
        if(values==[]):return 0
        max_value=max(values)
        keys=list(self._record_dict.keys())
        for key in keys:
            if(self._record_dict[key]==max_value):
                select_key=key
                break
        return select_key
    def _SaveWeight(self,current_epoch_num):
        save_path=self._weights_path+"/"+str(current_epoch_num)+".hd5"
        self._fkl_model.Save(save_path)
        return 
    def _ReadWeight(self,epoch_num):
        read_path=self._weights_path+"/"+str(epoch_num)+".hd5"
        self._fkl_model.Read(read_path)
        return 
    def _SaveRecordDict(self):
        FKLDict2JsonData(self._record_dict,self._weights_record_path)
        return
    def _ReadRecordDict(self):
        record_dict=FKLJsonData2Dict(self._weights_record_path)
        keys=list(record_dict.keys())
        for key in keys:
            record_dict[int(key)]=float(record_dict[key])
            del record_dict[key]
        return record_dict
    def _InitRecordDict(self):
        try:
            record_dict_buf=self._ReadRecordDict()
            self._record_dict.update(record_dict_buf)
        except:
            pass
        return
    def _Eval(self,test_x,test_y):
        pred_y=self._fkl_model.Predict(test_x)
        return self._eval_function(pred_y,test_y)
    def _Update(self,current_epoch_num):
        if(current_epoch_num>0 and current_epoch_num%self._step_epochs==0):
            self._SaveWeight(current_epoch_num)
            self._Record(current_epoch_num,self._Eval(self._test_x,self._test_y))
            self._SaveRecordDict()
        return
    def SetTestSet(self,test_x,test_y):
        self._test_x=test_x
        self._test_y=test_y
        return
    def SetEvalFunction(self,eval_function):
        self._eval_function=eval_function
        return 
    def Train(self,train_x,train_y,batch_size=1,epochs=10):
        if(type(self._test_x)==type(None) or type(self._test_y)==type(None)):
            raise Exception("FKLTrainer Train Error: Before train, to settestset first.")
        if(self._eval_function==None):
            raise Exception("FKLTrainer Train Error: Before train, to set _eval_function first.")
        current_epoch=self._GetBestEpoch()
        if(current_epoch!=0):
            self._ReadWeight(current_epoch)
        loop_num=round(epochs/self._step_epochs)
        for i in range(loop_num):
            print("The {0}th fit loop begin.".format(i))
            self._fkl_model.Fit(train_x,train_y,batch_size,self._step_epochs)
            current_epoch+=self._step_epochs
            self._Update(current_epoch)
            print("The {0}th fit loop finish.".format(i))
        return 

class FKLTester:
    """
    This class was built to deal with testing model.
    Attributes:
        _fkl_model: A object of FKLModel.
        _test_function: A function that to test and eval the result of y of true
                        y of prediction.
        _trainer_folder_path: A str that represent the path of trainer folder.
        _weights_path: A str that represent the path of weights, the arg will be 
                       automatic generated.
        _weights_record_path: A str that represent the json path of weights record.
        _record_dict: A dict that record the best result after eval.
    """
    def __init__(self,fkl_model,trainer_folder_path):
        self._fkl_model=fkl_model
        self._test_function=None
        self._trainer_folder_path=trainer_folder_path
        self._weights_path=self._trainer_folder_path+"/weights"
        self._weights_record_path=self._trainer_folder_path+"/weights_record.json"
        self._record_dict=self._ReadRecordDict()
        self._ReadWeight(self._GetBestEpoch())
    def _ReadWeight(self,epoch_num):
        read_path=self._weights_path+"/"+str(epoch_num)+".hd5"
        self._fkl_model.Read(read_path)
        return 
    def _ReadRecordDict(self):
        try:
            record_dict=FKLJsonData2Dict(self._weights_record_path)
        except:
            raise Exception("FKLTester _ReadRecordDict Error: The weights_record.json is not exist.")
        keys=list(record_dict.keys())
        for key in keys:
            record_dict[int(key)]=float(record_dict[key])
            del record_dict[key]
        return record_dict
    def _GetBestEpoch(self):
        values=list(self._record_dict.values())
        if(values==[]):return 0
        max_value=max(values)
        keys=list(self._record_dict.keys())
        for key in keys:
            if(self._record_dict[key]==max_value):
                select_key=key
                break
        return select_key
    def SetTestFunction(self,test_function):
        self._test_function=test_function
        return 
    def Test(self,test_x,test_y):
        if(self._test_function==None):
            raise Exception("FKLTrainer Test Error: Before test, to set _test_function first.")
        pred_y=self._fkl_model.Predict(test_x)
        return self._test_function(test_x,test_y,pred_y)