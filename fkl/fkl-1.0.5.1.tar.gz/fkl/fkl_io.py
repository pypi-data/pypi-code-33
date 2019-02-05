# -*- coding: utf-8 -*-
"""
This is a submodule of fk_lib.
The moudle contains several functions and classes to process file I/O.
"""
import json
from .fkl_string import *
import os

class FKLSelectReader:
    """
    This class was built to deal with csv of big data.
    Attributes:
        _file_path: A str of file path.
        _offset_json_path: A str of offset json path.
        _offset_dict: A dict of offset.
        _offset_dict_len: An integer that represent length of offset dict.
        _offset_msg_cache: A cache to speed ​​up the calculation.
    """
    def __init__(self):
        self._file_path=None
        self._offset_json_path=None
        self._offset_dict=None
        self._offset_dict_len=0
        self._offset_msg_cache=(0,0)
    def __call__(self,file_path,offset_json_path=None,select_num=0):
        if(select_num<0):raise Exception("FKLSelectRead Error: The select_num must bigger than zero.")
        selected_data=None
        fin=open(file_path,"r")
        if(offset_json_path==None):
            for i,data in enumerate(fin):
                if(i!=select_num):
                    continue
                else:
                    selected_data=data
                    break
        elif(type(offset_json_path)==str):
            if(self._offset_json_path!=offset_json_path):
                self._offset_json_path=offset_json_path
                self._offset_dict=FKLJsonData2Dict(offset_json_path)
                self._offset_dict_len=len(self._offset_dict)
            if(self._offset_dict_len>select_num):
                seek_count=self._CalSeekOffset(select_num)
                fin.seek(seek_count)
                selected_data=fin.readline()
        else:
            fin.close()
            raise Exception("FKLSelectRead Error: The offset_path must be str.")
        if(selected_data==None):
            fin.close()
            raise Exception("FKLSelectRead Error: The file not enough lines for read.")
        else:
            fin.close()
            return selected_data
    def _CalSeekOffset(self,select_num):
        lines_buf,offset_buf=self._offset_msg_cache
        if(abs(0-select_num)<abs(lines_buf-select_num)):
            offset_buf=sum([int(self._offset_dict[str(i)])for i in range(select_num+1)])
        else:
            if(select_num<lines_buf):
                for i in range(lines_buf,select_num,-1):
                    offset_buf-=int(self._offset_dict[str(i)])
            else:
                for i in range(lines_buf+1,select_num+1,1):
                    offset_buf+=int(self._offset_dict[str(i)])
        self._offset_msg_cache=(select_num,offset_buf)
        return offset_buf
    def GetLinesLen(self):
        return self._offset_dict_len
    
class FKLCSVData:
    """
    This class that represent line data of csv.
    Attributes:
        _data: A list that represent line data of csv.
        _max_index: An integer that represent the maximun number of arguments.
        _headers_dict: A dict that represent headers of arguments.
    """
    def __init__(self,data,data_len,headers_dict={}):
        self._data=data
        self._max_index=data_len-1
        self._headers_dict=headers_dict
    def __call__(self):
        return self._data
    def __getitem__(self,key):
        if(type(key)==int):
            arg=self._GetByIndex(key)
        elif(type(key)==str):
            arg=self._GetByHeader(key)
        else:
            raise Exception("FKLCSVData __getitem__ Error: The key's type must be int or str.")
        return arg
    def _GetByIndex(self,index):
        if(index>self._max_index or index<0):
            raise Exception("FKLCSVData _GetByIndex Error: The index out of range.")
        return self._data[index]
    def _GetByHeader(self,header):
        index=self._headers_dict.get(header,None)
        if(index==None):
            raise Exception("FKLCSVData _GetByHeader Error: The header is not exist.")
        return self._GetByIndex(index)

class FKLIterater:
    def __init__(self,datas,datas_len):
        self._datas=datas
        self._datas_len=datas_len
        self._current_index=0
    def __next__(self):
        if(self._current_index==self._datas_len):
            raise StopIteration
        returrn_data=self._datas[self._current_index]
        self._current_index+=1
        return returrn_data
        
class FKLCSVReader:
    """
    This class was built to deal with general csv.
    Attributes:
        _headers_dict: A dict that represent headers of line datas.
        _datas: A list that represent line datas of csv.
        _max_index: An integer that represent the maximun number of line datas.
    """
    def __init__(self,csv_datas_path,json_headers_path=None):
        self._headers_dict=self._ReadHeaders(json_headers_path)
        self._datas,self._first_header_dict=self._ReadDatas(csv_datas_path,self._headers_dict)
        self._max_index=len(self._datas)-1
    def __getitem__(self,key):
        if(type(key)==int):
            data=self._GetByIndex(key)
        elif(type(key)==str):
            data=self._GetByFirstHeader(key)
        else:
            raise Exception("FKLCSVReader __getitem__ Error: The key's type must be int or str.")
        return data
    def __iter__(self):
        return FKLIterater(self._datas,self._max_index+1)
    def _ReadHeaders(self,headers_json_path):
        if(headers_json_path==None):return {}
        self._headers_dict=FKLJsonData2Dict(headers_json_path)
        keys=list(self._headers_dict.keys())
        for key in keys:
            self._headers_dict[key]=int(self._headers_dict[key])
        return self._headers_dict
    def _ReadDatas(self,csv_path,headers_dict={}):
        fin=open(csv_path,"r")
        datas=fin.readlines()
        fin.close()
        datas=list(map(lambda data:FKLSplit(data,","),datas))
        datas_len=list(map(lambda data:len(data),datas))
        data_len=datas_len[0]
        if(data_len!=max(datas_len) or data_len!=min(datas_len)):
            raise Exception("FKLCSVReader _ReadDatas Error: The datas_length must be equal.")
        
        first_header_dict={}
        for i,data in enumerate(datas):
            first_header_dict[data[0]]=i
            datas[i]=FKLCSVData(data,data_len,headers_dict)
        return datas,first_header_dict
    def _GetByIndex(self,index):
        if(index>self._max_index or index<0):
            raise Exception("FKLCSVReader _GetByIndex Error: The index out of range.")
        return self._datas[index]
    def _GetByFirstHeader(self,first_header):
        index=self._first_header_dict.get(first_header,None)
        if(index==None):
            raise Exception("FKLCSVReader _GetByFirstHeader Error: The header is not exist.")
        return self._GetByIndex(index)
    def Len(self):
        return self._max_index+1
    
def FKLComputeLinesOffset(csv_file_path):
    """
    Args:
        csv_file_path: A str of csv file path.
    Returns:
        Return a dict that represent offset of every line data.
    Raises:
        None
    """
    offset_dict={}
    offset=0
    fin=open(csv_file_path,"r")
    for i,data in enumerate(fin):
        offset_dict[i]=offset
        offset=len(data.encode('utf-8'))
        print("Compute Finish......"+str(i))
    fin.close()
    return offset_dict
def FKLDict2JsonData(data_dict,output_path):
    with open(output_path,"w") as fout:
        json.dump(data_dict,fout,ensure_ascii=False)  
    return 
def FKLJsonData2Dict(json_path):
    with open(json_path,"r") as json_fin:
        data_dict=json.load(json_fin)
    return data_dict
def FKLFileSort(input_path,offset_path,output_path,sort_arg):
    arg_dict={}
    fin=open(input_path,"r")
    for i,data in enumerate(fin):
        arg_dict[sort_arg(data)]=i
    fin.close()
    
    select_reader=FKLSelectReader()
    dates=list(arg_dict.keys())
    dates.sort()
    fout=open(output_path,"w")
    for i,date in enumerate(dates):
        data=select_reader(input_path,offset_path,arg_dict[date])
        fout.write(data)
        print("Sorted Finish......"+str(i))
    fout.close()
    return 
def FKLReSplitCSVFile(file_path,output_folder,batch_size):
    """
    Args:
        file_path: A str of file path.
        output_folder: A str of output folder path.
        batch_size: An integer that represent the number of each csv.
    Returns:
        None
    Raises:
        None
    """
    fin=open(file_path,"r")
    file_count=0
    fout=open(output_folder+"/"+str(file_count)+".csv","w")
    for i,data_line in enumerate(fin):
        fout.write(data_line)
        if((i+1)%batch_size==0):
            print("ReSplit Finish......"+str(file_count))
            file_count+=1
            fout.close()
            fout=open(output_folder+"/"+str(file_count)+".csv","w")
    print("ReSplit Finish......"+str(file_count))
    fout.close()
    return 
def FKLCheckDir(folder_path):
    """
    Args:
        folder_path: A str of folder path.
    Returns:
        Return a bool of does folder path exist. 
    Raises:
        None
    """
    return os.path.isdir(folder_path)
def FKLCreateDir(path):
    """
    Args:
        path: A str of target path.
    Returns:
        None
    Raises:
        None
    """
    os.mkdir(path)
    return 
def FKLListDir(folder_path):
    """
    Args:
        folder_path: A str of folder path.
    Returns:
        A list that represent strings of files's name.
    Raises:
        None
    """
    return os.listdir(folder_path)
def FKLImport(import_path):
    """
    Args:
        import_path: A str of import path.
    Returns:
        None
    Raises:
        None
    """
    __import__(import_path)
    return 
