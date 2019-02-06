# -*- coding: utf-8 -*-
"""
This is a submodule of fk_lib.
The moudle contains several functions to calculate some common index.
"""
from .fkl_string import *
from .fkl_io import *

def FKLOneHotEncode(num,max_num):
    """
    Args:
        num: An integer by input.
        max_num: Represent the maximun length of one hot code.
    Returns:
        A list that represent the one hot code.
    Raises:
        None
    """
    encoded_num=[0 for i in range(max_num)]
    encoded_num[num]=1
    return encoded_num
def FKLOneHotDecode(one_hot_code):
    """
    Args:
        one_hot_code: A list that represent the one hot code.
    Returns:
        An integer of decoded one_hot_code.
    Raises:
        None
    """
    one_hot_code=list(one_hot_code)
    num=one_hot_code.index(max(one_hot_code))
    return num
def FKLNormalization(datas,min_max_tuple=(None,None)):
    """
    Args:
        datas: A list that represent the datas.
        min_max_tuple: Respectively represent the min value and max value, if it's None,
                        then this function is automatically calculated.
    Returns:
        Return 2 dim tuple, the first element is normalized data, the second element
        is a tuple that represent the min value and max value.
    Raises:
       Exception: The min_max_tuple's type must be tuple.
    """
    if(type(min_max_tuple)!=tuple):
        raise Exception("FKLNormalization Error: The min_max_tuple's type must be tuple.")
    min_value,max_value=min_max_tuple
    if(min_value==None or max_value==None):
        min_value=min(datas)
        max_value=max(datas)
    min_max_gap=max_value-min_value
    if(min_max_gap>0):
        for i,data in enumerate(datas):
            datas[i]=(data-min_value)/min_max_gap
    return (datas,(min_value,max_value))
def FKLRevertNormalization(datas,min_max_tuple=(None,None)):
    """
    Args:
        datas: A list that represent the normalized datas.
        min_max_tuple: Respectively represent the min value and max value, can't
                        be none.
    Returns:
        Return a list that represent revert normalized datas.
    Raises:
        Exception: The min_max_tuple's type must be tuple.
        Exception: The min_value and max_value can't be None.
    """
    if(type(min_max_tuple)!=tuple):
        raise Exception("FKLRevertNormalization Error: The min_max_tuple's type must be tuple.")
    min_value,max_value=min_max_tuple
    if(min_value==None or max_value==None):
        raise Exception("FKLRevertNormalization Error: The min_value and max_value can't be None.")
    min_max_gap=max_value-min_value
    for i,data in enumerate(datas):
        datas[i]=data*min_max_gap+min_value
    return datas
def FKLCSVNormalization(csv_path,output_path,rows=[],dict_out_path=None,dict_in_path=None):
    """
    Args:
        csv_path: A str that repressent the path of the input csv.
        output_path: A str that repressent the ouput path of the normalized data.
    Returns:
        None
    Raises:
        Exception: The rows's type must be list.
        Exception: The rows's length must bigger than zero.
    """
    if(type(rows)!=list and type(rows)!=tuple):
        raise Exception("FKLCSVNormalization Error: The rows's type must be list.")
    if(len(rows)<=0):
        raise Exception("FKLCSVNormalization Error: The rows's length must bigger than zero.")
        
    datas_dict={}
    if(dict_in_path!=None and type(dict_in_path)==str):
        min_max_dict=FKLJsonData2Dict(dict_in_path)
    else:
        min_max_dict={}
        for row in rows:min_max_dict[row]=(None,None)

    fin=open(csv_path,"r")
    for data in fin:
        args=FKLSplit(data,",")
        for j,arg in enumerate(args):
            if(j not in datas_dict):
                datas_dict[j]=[]
            datas_dict[j].append(arg)      
    fin.close()
    
    for row in rows:
        if(type(row)==int):
            datas_dict[row]=list(map(lambda data:float(data),datas_dict[row]))
            datas_dict[row],min_max_dict[row]=FKLNomalization(datas_dict[row],min_max_dict[row])
        elif(type(row)==tuple or type(row)==list):
            if(len(row)!=2):
                raise Exception("FKLCSVNomalization Error: The row_interval length must be two.")
            row_begin,row_end=row
            row_datas_buf=[]
            for j in range(row_begin,row_end+1):
                datas_dict[j]=list(map(lambda data:float(data),datas_dict[j]))
                row_datas_buf=row_datas_buf+datas_dict[j]
            row_datas_buf,min_max_dict[row]=FKLNomalization(row_datas_buf,min_max_dict[row])
            for j in range(row_begin,row_end+1):
                datas_dict[j],min_max_dict[row]=FKLNomalization(datas_dict[j],min_max_dict[row])
        
    fout=open(output_path,"w")
    keys=list(datas_dict.keys())
    keys.sort()
    data_columns=len(datas_dict[0])
    for i in range(data_columns):
        output_line=[]
        for key in keys:
            output_line.append(str(datas_dict[key][i]))
        fout.write(",".join(output_line)+"\n")
    fout.close()
    return 
def FKLMean(datas):
    """
    Args:
        datas: A list that represent the datas.
    Returns:
        An integer of datas's mean value.
    Raises:
        None
    """
    return sum(datas)/len(datas)
def FKLVariance(datas):
    """
    Args:
        datas: A list that represent the datas.
    Returns:
        An integer of datas's mean value.
    Raises:
        None
    """
    var_buf=0
    mean=FKLMean(datas)
    datas_len=0
    for data in datas:
        var_buf+=(data-mean)**2
        datas_len+=1
    return var_buf/datas_len
def FKLConfusionMatrix(labels,pred_datas,true_datas):
    """
    Args:
        labels: A list that represent the total label of datas.
        pred_datas: A list that represent the data of prediction.
        true_datas: A list that represent the true datas.
    Returns:
        Return a dict that represent the confusion matrix by compare true data
        between data of prediction.
    Raises:
        Exception: FKLConfusionMatrix Error: The pred_datas and true_datas must be list.
        Exception: FKLConfusionMatrix Error: The pred_datas_len and true_datas_len must be equal.
    """
    if(type(true_datas)!=list or type(true_datas)!=list):
        raise Exception("FKLConfusionMatrix Error: The pred_datas and true_datas must be list.")
    pred_datas_len=len(pred_datas)
    true_datas_len=len(true_datas)
    if(pred_datas_len!=true_datas_len):
        raise Exception("FKLConfusionMatrix Error: The pred_datas_len and true_datas_len must be equal.")

    datas_len=true_datas_len
      
    confusion_matrix_dict={}
    for label in labels:
        if(label in confusion_matrix_dict):continue
        confusion_matrix_dict[label]={}
        for label_temp in labels:
            confusion_matrix_dict[label][label_temp]=0
            
    for i in range(datas_len):
        confusion_matrix_dict[pred_datas[i]][true_datas[i]]+=1
    return confusion_matrix_dict
def FKLConfusionMatrix2Csv(confusion_matrix_dict,save_path):
    """
    Args:
        confusion_matrix_dict: A dict that represent the confusion matrix.
        save_path: A str that repressent the output path of confusion matrix.
    Returns:
        None
    Raises:
        None
    """
    labels=list(confusion_matrix_dict.keys())
    fout=open(save_path,"w")
    labels_temp=list(map(lambda label:str(label),labels))
    fout.write(","+",".join(labels_temp)+"\n")
    for label in labels:
        fout.write(str(label))
        for label_temp in labels:
            fout.write(","+str(confusion_matrix_dict[label][label_temp]))
        fout.write("\n")
    fout.close()
    return
def FKLPrecision(confusion_matrix_dict):
    """
    Args:
        confusion_matrix_dict: A dict that represent the confusion matrix.
    Returns:
        Return a dict that repressent the dict of precision.
    Raises:
        None
    """
    labels=list(confusion_matrix_dict.keys())
    true_count_dict={}
    tot_count_dict={}
    precision_dict={}
    for label in labels:
        precision_dict[label]=0
        tot_count_dict[label]=0
        true_count_dict[label]=0
        
    for label in labels:
        for label_temp in labels:
            tot_count_dict[label]+=confusion_matrix_dict[label][label_temp]
            if(label==label_temp):
                true_count_dict[label]+=confusion_matrix_dict[label][label_temp]
    for label in labels:
        if(tot_count_dict[label]==0):
            precision=0
        else:
            precision=true_count_dict[label]/tot_count_dict[label]
        precision_dict[label]=precision
    return precision_dict
def FKLRecall(confusion_matrix_dict):
    """
    Args:
        confusion_matrix_dict: A dict that represent the confusion matrix.
    Returns:
        Return a dict that repressent the dict of recall.
    Raises:
        None
    """
    labels=list(confusion_matrix_dict.keys())
    true_count_dict={}
    tot_count_dict={}
    recall_dict={}
    for label in labels:
        recall_dict[label]=0
        tot_count_dict[label]=0
        true_count_dict[label]=0
        
    for label in labels:
        for label_temp in labels:
            tot_count_dict[label_temp]+=confusion_matrix_dict[label][label_temp]
            if(label==label_temp):
                true_count_dict[label]+=confusion_matrix_dict[label][label_temp]
    for label in labels:
        if(tot_count_dict[label]==0):
            recall=0
        else:
            recall=true_count_dict[label]/tot_count_dict[label]
        recall_dict[label]=recall
    return recall_dict
def FKLAccuracy(confusion_matrix_dict):
    """
    Args:
        confusion_matrix_dict: A dict that represent the confusion matrix.
    Returns:
        Return a float of accuracy.
    Raises:
        None
    """
    labels=list(confusion_matrix_dict.keys())
    true_count=0
    tot_count=0
    for label in labels:
        for label_temp in labels:
            if(label==label_temp):
                true_count+=confusion_matrix_dict[label][label_temp]
            tot_count+=confusion_matrix_dict[label][label_temp]
    accuracy=true_count/tot_count
    return accuracy
def FKLDecimal2Bin(decimal_num):
    """
    Args:
        decimal_num: A decimal integer.
    Returns:
        Return an integer that represent the binary num.
    Raises:
        None
    """
    return int(bin(decimal_num)[2:])
def FKLBin2Decimal(bin_num):
    """
    Args:
        decimal_num: An in teger that represent the binary num.
    Returns:
        Return a decimal integer.
    Raises:
        None
    """
    return int(str(bin_num),2)