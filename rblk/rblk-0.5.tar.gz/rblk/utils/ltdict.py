import copy
from operator import itemgetter

    # '''
        # is_ltdict(obj)
        # json2ltdict(obj,**kwargs)
        # to_json(ltd,**kwargs)
        # list2ltdict(array,**kwargs)
        # tuple2ltdict(fixed_array,**kwargs)
        # set2ltdict(this_set,**kwargs)
        # to_list(ltd,**kwargs)
        # to_tuple(ltd,**kwargs)
        # to_set(ltd,**kwargs)
        # extend(ltd1,ltd2,**kwargs)
        # prepend_extend(ltd1,ltd2,**kwargs)
        # concat(ltd1,ltd2,**kwargs)
        # first_continuous_indexes_slice(ltd,value,**kwargs)
        # last_continuous_indexes_slice(ltd,value,**kwargs)
        # all_continuous_indexes_slices_array(ltd,value,**kwargs)
        # indexes_array(ltd,value,**kwargs)
        # first_index(ltd,value,**kwargs)
        # last_index(ltd,value,**kwargs)
        # append(ltd,value,**kwargs)
        # prepend(ltd,value,**kwargs)
        # clear(ltd,**kwargs)
        # copy(ltd,**kwargs)
        # deepcopy(ltd,**kwargs)
        # insert(ltd,index,value,**kwargs)
        # insert_ltdict(ltd1,index,ltd2,**kwargs)
        # include(ltd,value,**kwargs)
        # count(ltd,value,**kwargs)
        # pop(ltd,index,**kwargs)
        # pop_range(ltd,start,end,**kwargs)
        # pop_seqs(ltd,seqs_set,**kwargs)
        # remove_first(ltd,value,**kwargs)
        # remove_last(ltd,value,**kwargs)
        # remove_all(ltd,value,**kwargs)
        # reverse(ltd,**kwargs)
        # sort(ltd,**kwargs)
        # naturalize_intkeydict(ikd)
    # '''
#ListTupleDict

def is_ltdict(obj):
    '''
        ltd = {0:1,1:2,2:3}
        is_ltdict(ltd) == True
        ltd = {0:1,2:2,3:3}
        is_ltdict(ltd) == False
        ltd = {0:1,'1':2,2:3}
        is_ltdict(ltd) == False
    '''
    if(isinstance(obj,dict)):
        pass
    else:
        return(False)
    index_set = set({})
    if(obj == {}):
        return(True)
    else:
        for key in obj:
            if(isinstance(key,int)):
                if(key >= 0):
                    index_set.add(key)
                else:
                    return(False)
            else:
                return(False)
        for i in range(0,obj.__len__()):
            if(i in index_set):
                pass
            else:
                return(False)
        return(True)

def json2ltdict(obj,**kwargs):
    '''not recursive;
       by default deepcopy=1: will not affect the origianl object;
       return a ltd;
       by default check=0: will not check if the obj is a json_ltdict, return None if the obj is not a json_ltdict
       json_dict = {'0':'a','1':'b','2':'c'}
       json2ltdict(json_dict) == {0:'a',1:'b',2:'c'}
    '''
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = 1
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_json_ltdict(obj)):
            pass
        else:
            return(None)
    else:
        pass
    ltd = {}
    if(deepcopy):
        new = copy.deepcopy(obj)
    else:
        new = obj
    for key in new:
        ltd[int(key)] = new[key]
    return(ltd)


def to_json(ltd,**kwargs):
    '''not recursive;
       by default deepcopy=1: will not affect the origianl object;
       return a ltd;
       by default check=0: will not check if the obj is a ltd, return None if the obj is not a ltd
       ltd = {0:'a',1:'b',2:'c'}
       to_json(ltd) == {'1': 'b', '2': 'c', '0': 'a'}
    '''
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = 1
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd)):
            pass
        else:
            return(None)
    else:
        pass
    j = {}
    if(deepcopy):
        new = copy.deepcopy(ltd)
    else:
        new = ltd
    for key in new:
        j[str(key)] = new[key]
    return(j)


def list2ltdict(array,**kwargs):
    '''not recursive;
       by default deepcopy=1: will not affect the origianl object;
       return a ltd;
       by default check=0: will not check if the array is a list, return None if the array is not a list
       array = ['a','b','c']
       list2ltdict(array) == {0: 'a', 1: 'b', 2: 'c'}
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(isinstance(array,list)):
            pass
        else:
            return(None)
    else:
        pass
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = 1
    ltd = {}
    len = array.__len__()
    if(deepcopy):
        new = copy.deepcopy(array)
    else:
        new = array
    for i in range(0,len):
        ltd[i] = new[i]
    return(ltd)

def tuple2ltdict(fixed_array,**kwargs):
    '''not recursive;
       by default deepcopy=1: will not affect the origianl object;
       return a ltd;
       by default check=0: will not check if the array is a tuple, return None if the array is not a tuple
       t = ('a','b','c')
       tuple2ltdict(t) == {0: 'a', 1: 'b', 2: 'c'}
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(isinstance(fixed_array,tuple)):
            pass
        else:
            return(None)
    else:
        pass
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = 1
    ltd = {}
    len = fixed_array.__len__()
    if(deepcopy):
        new = copy.deepcopy(fixed_array)
    else:
        new = fixed_array
    for i in range(0,len):
        ltd[i] = new[i]
    return(ltd)


def set2ltdict(this_set,**kwargs):
    '''not recursive;
       by default deepcopy=1: will not affect the origianl object;
       return a ltd;
       by default check=0: will not check if the array is a set, return None if the array is not a set
       s = {'a','b','c'}
       set2ltdict(s) == 
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(isinstance(this_set,set)):
            pass
        else:
            return(None)
    else:
        pass
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = 1
    ltd = {}
    if(deepcopy):
        new = copy.deepcopy(this_set)
    else:
        new = this_set
    i = 0
    for each in this_set:
        ltd[i] = each
        i = i + 1
    return(ltd)

def to_list(ltd,**kwargs):
    '''not recursive;
       by default deepcopy=1: will not affect the origianl object;
       return a ltd;
       by default check=0: will not check if it is a ltd, return None if it is not a ltd
       ltd = {0: 'a', 1: 'b', 2: 'c'}
       to_list(ltd) == ['a', 'b', 'c']
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd)):
            pass
        else:
            return(None)
    else:
        pass
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = 1
    l = []
    len = ltd.__len__()
    if(deepcopy):
        new = copy.deepcopy(ltd)
    else:
        new = ltd
    for i in range(0,len):
        l.append(new[i])
    return(l)

def to_tuple(ltd,**kwargs):
    '''not recursive;
       by default deepcopy=1: will not affect the origianl object;
       return a ltd;
       by default check=0: will not check if it is a ltd, return None if it is not a ltd
       ltd = {0: 'a', 1: 'b', 2: 'c'}
       to_tuple(ltd) == ('a', 'b', 'c')
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd)):
            pass
        else:
            return(None)
    else:
        pass
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = 1
    l = []
    len = ltd.__len__()
    if(deepcopy):
        new = copy.deepcopy(ltd)
    else:
        new = ltd
    for i in range(0,len):
        l.append(new[i])
    return(tuple(l))


def to_set(ltd,**kwargs):
    '''not recursive;
       by default deepcopy=1: will not affect the origianl object;
       return a ltd;
       by default check=0: will not check if it is a ltd, return None if it is not a ltd
       ltd = {0: 'a', 1: 'b', 2: 'c'}
       to_set(ltd) == {'b', 'c', 'a'} 
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd)):
            pass
        else:
            return(None)
    else:
        pass
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = 1
    s = set({})
    len = ltd.__len__()
    if(deepcopy):
        new = copy.deepcopy(ltd)
    else:
        new = ltd
    for i in range(0,len):
        s.add(new[i])
    return(s)



def extend(ltd1,ltd2,**kwargs):
    '''not recursive;
       by default deepcopy_1=0 and deepcopy_2=0: a shallow copy ltd2 is is excuted;
       return a ltd;
       by default check=0: will not check if both are ltds, return None if either is not a ltd
       ltd1 = {0: 'a', 1: 'b', 2: 'c'}
       ltd2 = {0: 'd', 1: 'e', 2: 'f'}
       extend(ltd1,ltd2) == {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f'}
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd1) & is_ltdict(ltd2)):
            pass
        else:
            return(None)
    else:
        pass
    if('deepcopy_1' in kwargs):
        deepcopy_1 = kwargs['deepcopy_1']
    else:
        deepcopy_1 = 0
    if('deepcopy_2' in kwargs):
        deepcopy_2 = kwargs['deepcopy_2']
    else:
        deepcopy_2 = 0
    if(deepcopy_1):
        new_1 = copy.deepcopy(ltd1)
    else:
        new_1 = ltd1
    if(deepcopy_2):
        new_2 = copy.deepcopy(ltd2)
    else:
        new_2 = copy.copy(ltd2)
    len_1 = new_1.__len__()
    len_2 = new_2.__len__()
    for i in range(0,len_2):
        new_1[i + len_1] = new_2[i]
    return(new_1)


def prepend_extend(ltd1,ltd2,**kwargs):
    '''not recursive;
       by default deepcopy_1=0 and deepcopy_2=0: a shallow copy ltd2 is is excuted;
       return a ltd;
       by default check=0: will not check if both are ltds, return None if either is not a ltd
       ltd1 = {0: 'a', 1: 'b', 2: 'c'}
       ltd2 = {0: 'd', 1: 'e', 2: 'f'}
       prepend_extend(ltd1,ltd2) == {0: 'd', 1: 'e', 2: 'f', 3: 'a', 4: 'b', 5: 'c'}
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd1) & is_ltdict(ltd2)):
            pass
        else:
            return(None)
    else:
        pass
    if('deepcopy_1' in kwargs):
        deepcopy_1 = kwargs['deepcopy_1']
    else:
        deepcopy_1 = 0
    if('deepcopy_2' in kwargs):
        deepcopy_2 = kwargs['deepcopy_2']
    else:
        deepcopy_2 = 0
    if(deepcopy_1):
        new_1 = copy.deepcopy(ltd1)
    else:
        new_1 = ltd1
    if(deepcopy_2):
        new_2 = copy.deepcopy(ltd2)
    else:
        new_2 = copy.copy(ltd2)
    len_1 = new_1.__len__()
    len_2 = new_2.__len__()
    swap = {}
    for i in range(0,len_1):
        swap[len_2 + i] = new_1[i]
    for i in range(0,len_2):
        new_1[i] = new_2[i]
    for i in range(len_2,len_2+len_1):
        new_1[i] = swap[i]
    return(new_1)


def concat(ltd1,ltd2,**kwargs):
    '''not recursive;
       by default deepcopy_1=1 and deepcopy_2=1;
       return a ltd;
       by default check=0: will not check if both are ltds, return None if either is not a ltd
       ltd1 = {0: 'a', 1: 'b', 2: 'c'}
       ltd2 = {0: 'd', 1: 'e', 2: 'f'}
       concat(ltd1,ltd2) == {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f'}
       ltd1 == {0: 'a', 1: 'b', 2: 'c'}
       ltd2 == {0: 'd', 1: 'e', 2: 'f'}
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd1) & is_ltdict(ltd2)):
            pass
        else:
            return(None)
    else:
        pass
    if('deepcopy_1' in kwargs):
        deepcopy_1 = kwargs['deepcopy_1']
    else:
        deepcopy_1 = 1
    if('deepcopy_2' in kwargs):
        deepcopy_2 = kwargs['deepcopy_2']
    else:
        deepcopy_2 = 1
    if(deepcopy_1):
        new_1 = copy.deepcopy(ltd1)
    else:
        new_1 = ltd1
    if(deepcopy_2):
        new_2 = copy.deepcopy(ltd2)
    else:
        new_2 = ltd2
    len_1 = new_1.__len__()
    len_2 = new_2.__len__()
    new = {}
    for i in range(0,len_1):
        new[i] = new_1[i]
    for i in range(len_1,len_1+len_2):
        new[i] = new_2[i-len_1]
    return(new)
def first_continuous_indexes_slice(ltd,value,**kwargs):
    '''
       select all the first continuous indexes whose value equals the given value;
       return a list ;       
       by default check=0: will not check if it is a ltd, return None if it is not a ltd
       by default start=0
       ltd = {0:'a',1:'b',2:'c',3:'c',4:'d',5:'c',6:'e',7:'f',8:'c',9:'c'}
       first_continuous_indexes_slice(ltd,'c') == [2, 3]
    '''
    if('start' in kwargs):
        start = kwargs['start']
    else:
        start = 0
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd)):
            pass
        else:
            return(None)
    else:
        pass
    rslt = []
    begin = 0
    for i in range(start,ltd.__len__()):
        if(ltd[i] == value):
            rslt.append(i)
            begin = i+1
            break
        else:
            pass
    for i in range(begin,ltd.__len__()):
        if(ltd[i] == value):
            rslt.append(i)
        else:
            break
    return(rslt)
def last_continuous_indexes_slice(ltd,value,**kwargs):
    '''
       select all the last continuous indexes whose value equals the given value;
       return a list ;       
       by default check=0: will not check if it is a ltd, return None if it is not a ltd
       by default start= ltd.__len__() -1  
       ltd = {0:'a',1:'b',2:'c',3:'c',4:'d',5:'c',6:'e',7:'f',8:'c',9:'c'}
       last_continuous_indexes_slice(ltd,'c') == [8, 9]
    '''
    if('start' in kwargs):
        start = kwargs['start']
    else:
        start = -1
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd)):
            pass
        else:
            return(None)
    else:
        pass
    if(start==-1):
        start = ltd.__len__()-1
    rslt = []
    begin = 0
    for i in range(start,-1,-1):
        if(ltd[i] == value):
            rslt.append(i)
            begin = i-1
            break
        else:
            pass
    for i in range(begin,-1,-1):
        if(ltd[i] == value):
            rslt.append(i)
        else:
            break
    rslt.reverse()
    return(rslt)
def all_continuous_indexes_slices_array(ltd,value,**kwargs):    
    '''
        select all the continuous indexes whose value equals the given value;
        return a list ;       
        by default check=0: will not check if it is a ltd, return None if it is not a ltd
        ltd = {0:'a',1:'b',2:'c',3:'c',4:'d',5:'c',6:'e',7:'f',8:'c',9:'c'}
        all_continuous_indexes_slices_array(ltd,'c') == [[2, 3], [5], [8, 9]]
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd)):
            pass
        else:
            return(None)
    else:
        pass
    len = ltd.__len__()
    sarray = []
    start = 0
    while(start < len):
        rslt = first_continuous_indexes_slice(ltd,value,start=start,check=0)
        sarray.append(rslt)
        start = rslt[-1] +1
    return(sarray)

def indexes_array(ltd,value,**kwargs):
    '''
        select all the indexes whose value equals the given value;
        return a list ;       
        by default check=0: will not check if it is a ltd, return None if it is not a ltd
        ltd = {0:'a',1:'b',2:'c',3:'c',4:'d',5:'c',6:'e',7:'f',8:'c',9:'c'}
        indexes_array(ltd,'c') == [2, 3, 5, 8, 9]
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd)):
            pass
        else:
            return(None)
    else:
        pass
    rslt = []
    for i in range(0,ltd.__len__()):
        if(ltd[i] == value):
            rslt.append(i)
        else:
            pass
    return(rslt)


def first_index(ltd,value,**kwargs):
    '''
        select all the first index whose value equals the given value;
        return a list ;       
        by default check=0: will not check if it is a ltd, return None if it is not a ltd
        ltd = {0:'a',1:'b',2:'c',3:'c',4:'d',5:'c',6:'e',7:'f',8:'c',9:'c'}
        first_index(ltd,'c') == 2
    '''
    if('start' in kwargs):
        start = kwargs['start']
    else:
        start = 0
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd)):
            pass
        else:
            return(None)
    else:
        pass
    for i in range(start,ltd.__len__()):
        if(ltd[i] == value):
            return(i)
        else:
            pass
    return(None)
def last_index(ltd,value,**kwargs):
    '''
        select all the last index whose value equals the given value;
        return a list ;
        by default check=0: will not check if it is a ltd, return None if it is not a ltd
        ltd = {0:'a',1:'b',2:'c',3:'c',4:'d',5:'c',6:'e',7:'f',8:'c',9:'c'}
        last_index(ltd,'c') == 9
    '''
    if('start' in kwargs):
        start = kwargs['start']
    else:
        start = -1
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd)):
            pass
        else:
            return(None)
    else:
        pass
    if(start == -1):
        start = ltd.__len__() - 1
    for i in range(start,-1,-1):
        if(ltd[i] == value):
            return(i)
        else:
            pass
    return(None)
def append(ltd,value,**kwargs):
    '''
        by default it will change the original ltd: deepcopy = 0;
        by default check=0: will not check if it is a ltd, return None if it is not a ltd
        ltd = {0: 'a', 1: 'b', 2: 'c'}
        append(ltd,'d') == {0: 'a', 1: 'b', 2: 'c', 3: 'd'}
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd)):
            pass
        else:
            return(None)
    else:
        pass
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = 0
    if(deepcopy):
        new = copy.deepcopy(ltd)
    else:
        new = ltd
    len = ltd.__len__()
    new[len] = value
    return(new)
def prepend(ltd,value,**kwargs):
    '''
        by default it will change the original ltd: deepcopy = 0;
        by default check=0: will not check if it is a ltd, return None if it is not a ltd
        ltd = {0: 'a', 1: 'b', 2: 'c'}
        prepend(ltd,'d') == {0: 'd', 1: 'a', 2: 'b', 3: 'c'}
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd)):
            pass
        else:
            return(None)
    else:
        pass
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = 0
    if(deepcopy):
        new = copy.deepcopy(ltd)
    else:
        new = ltd
    len = ltd.__len__()
    swap = {}
    for i in range(0,len):
        swap[i + 1] = new[i]
    for i in range(1,len+1):
        new[i] = swap[i]
    new[0] = value
    return(new)
def clear(ltd,**kwargs):
    '''
        by default it will change the original ltd: deepcopy = 0;
        by default check=0: will not check if it is a ltd, return None if it is not a ltd
        ltd = {0: 'a', 1: 'b', 2: 'c'}
        clear(ltd) == {}
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd)):
            pass
        else:
            return(None)
    else:
        pass
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = 0
    if(deepcopy):
        new = {}
    else:
        new = ltd
        new.clear()
    return(new)
def insert(ltd,index,value,**kwargs):
    '''
        by default it will change the original ltd: deepcopy = 0;
        by default check=0: will not check if it is a ltd, return None if it is not a ltd
        ltd = {0: 'a', 1: 'b', 2: 'c'}
        insert(ltd,1,'d') == {0: 'a', 1: 'd', 2: 'b', 3: 'c'}
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd)):
            pass
        else:
            return(None)
    else:
        pass
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = 0
    if(deepcopy):
        new = copy.deepcopy(ltd)
    else:
        new = ltd
    len = ltd.__len__()
    swap = {}
    for i in range(0,index):
        swap[i] = new[i]
    swap[index] = value
    for i in range(index + 1,len+1):
        swap[i] = new[i-1]
    for i in range(0,len+1):
        new[i] = swap[i]
    return(new)
def insert_ltdict(ltd1,index,ltd2,**kwargs):
    '''
        by default it will change the original ltd1: deepcopy_1 = 0;
                   and will do a shallow copy of ltd2: deepcopy_2 = 0;
        by default check=0: will not check if it is a ltd, return None if it is not a ltd
        ltd1 = {0: 'a', 1: 'b', 2: 'c'}
        ltd2 = {0: 'd', 1: 'e', 2: 'f'}
        insert_ltdict(ltd1,1,ltd2) == {0: 'a', 1: 'd', 2: 'e', 3: 'f', 4: 'b', 5: 'c'}
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd1) & is_ltdict(ltd2)):
            pass
        else:
            return(None)
    else:
        pass
    if('deepcopy_1' in kwargs):
        deepcopy_1 = kwargs['deepcopy_1']
    else:
        deepcopy_1 = 0
    if('deepcopy_2' in kwargs):
        deepcopy_2 = kwargs['deepcopy_2']
    else:
        deepcopy_2 = 0
    if(deepcopy_1):
        new_1 = copy.deepcopy(ltd1)
    else:
        new_1 = ltd1
    if(deepcopy_2):
        new_2 = copy.deepcopy(ltd2)
    else:
        new_2 = copy.copy(ltd2)
    len_1 = new_1.__len__()
    len_2 = new_2.__len__()
    if(index >= len_1):
        return(new_1)
    else:
        pass
    swap = {}
    for i in range(0,index):
        swap[i] = new_1[i]
    for i in range(index,index + len_2):
        swap[i] = new_2[i-index]
    for i in range(index + len_2,len_1+len_2):
        swap[i] = new_1[i-len_2]
    for i in range(0,len_1+len_2):
        new_1[i] = swap[i]
    return(new_1)
def include(ltd,value,**kwargs):
    '''
        by default check=0: will not check if it is a ltd, return None if it is not a ltd
        ltd = {0: 'a', 1: 'b', 2: 'c'}
        include(ltd,'c') == True
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd)):
            pass
        else:
            return(None)
    else:
        pass
    for i in range(0,ltd.__len__()):
        if(ltd[i] == value):
            return(True)
    return(False)
def count(ltd,value,**kwargs):
    '''
        by default check=0: will not check if it is a ltd, return None if it is not a ltd
        ltd = {0:'a',1:'b',2:'c',3:'c',4:'d',5:'c',6:'e',7:'f',8:'c',9:'c'}
        count(ltd,'c') == 5
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd)):
            pass
        else:
            return(None)
    else:
        pass
    num = 0
    for i in range(0,ltd.__len__()):
        if(ltd[i] == value):
            num = num + 1
    return(num)
def pop(ltd,index,**kwargs):
    '''
        by default it will change the original ltd: deepcopy = 0;
        by default check=0: will not check if it is a ltd, return None if it is not a ltd
        ltd = {0: 'a', 1: 'b', 2: 'c'}
        pop(ltd,1) == 'b'
        ltd == {0: 'a', 1: 'c'}
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd)):
            pass
        else:
            return(None)
    else:
        pass
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = 0
    if(deepcopy):
        new = copy.deepcopy(ltd)
    else:
        new = ltd
    len = ltd.__len__()
    if(index < 0):
        index = len + index
    else:
        pass
    if(index in range(0,len)):
        rslt = new[index]
    else:
        rslt = None
        return(rslt)
    for i in range(index,len-1):
        new[i] = new[i+1]
    del new[len-1]
    return(rslt)
def pop_range(ltd,start,end,**kwargs):
    '''
        by default it will change the original ltd: deepcopy = 0;
        by default check=0: will not check if it is a ltd, return None if it is not a ltd
        ltd = {0:'a',1:'b',2:'c',3:'c',4:'d',5:'c',6:'e',7:'f',8:'c',9:'c'}
        pop_range(ltd,1,7) == {0: 'b', 1: 'c', 2: 'c', 3: 'd', 4: 'c', 5: 'e', 6: 'f'}
        ltd == {0: 'a', 1: 'c', 2: 'c'}
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd)):
            pass
        else:
            return(None)
    else:
        pass
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = 0
    if(deepcopy):
        new = copy.deepcopy(ltd)
    else:
        new = ltd
    len = ltd.__len__()
    if(start < 0):
        start = 0
    elif(start >= len):
        start = len
    else:
        pass
    if(end<start):
        end = start
    elif(end >= len-1):
        end = len-1 
    elif(end < 0):
        end = 0
    else:
        pass
    rslt = {}
    seq = 0
    for i in range(start,end+1):
        rslt[seq] = new[i]
        seq = seq + 1
    swap = {}
    range_len = end-start+1
    for i in range(0,start):
        swap[i] = new[i]
    for i in range(start,end+1):
        s = i+range_len
        if(s in new):
            swap[i] = new[s]
    for i in range(end+1,len):
        s = i+range_len
        if(s in new):
            swap[i] = new[s]
    for i in range(0,swap.__len__()):
        new[i] = swap[i]
    for i in range(swap.__len__(),len):
        del new[i]
    return(rslt)
def pop_seqs(ltd,seqs_set,**kwargs):
    '''
        by default it will change the original ltd: deepcopy = 0;
        by default check=0: will not check if it is a ltd, return None if it is not a ltd
        ltd = {0:'a',1:'b',2:'c',3:'c',4:'d',5:'c',6:'e',7:'f',8:'c',9:'c'}
        seqs_set = {2,5,8}
        pop_seqs(ltd,seqs_set) == {0: 'c', 1: 'c', 2: 'c'}
        ltd == {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'c'}
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd)):
            pass
        else:
            return(None)
    else:
        pass
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = 0
    if(deepcopy):
        new = copy.deepcopy(ltd)
    else:
        new = ltd
    len = new.__len__()
    rslt = {}
    if(isinstance(seqs_set,list)):
        pass
    elif(isinstance(seqs_set,set)):
        real_seqs = list(seqs_set)
    elif(is_ltdict(seqs_set)):
        real_seqs = to_list(seqs_set)
    else:
        print("Error: <seqs_set> Invalid")
        return(None)
    len = real_seqs.__len__()
    i = 0
    while((len > 0)&(i<len)):
        if(real_seqs[i] in new):
            pass
        else:
            real_seqs.pop(i)
        i = i + 1
        len = real_seqs.__len__()
    real_seqs.sort()
    j = 0
    for i in range(0,real_seqs.__len__()):
        seq = real_seqs[i]
        rslt[j] = new[seq]
        j = j + 1
    step = 0
    for i in range(0,real_seqs.__len__()):
        seq = real_seqs[i] - step 
        pop(new,seq)
        step = step +1
    return(rslt)
def remove_first(ltd,value,**kwargs):
    '''
        by default it will change the original ltd: deepcopy = 0;
        by default check=0: will not check if it is a ltd, return None if it is not a ltd
        ltd = {0:'a',1:'b',2:'c',3:'c',4:'d',5:'c',6:'e',7:'f',8:'c',9:'c'}
        remove_first(ltd,'c') == {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'c', 5: 'e', 6: 'f', 7: 'c', 8: 'c'}
        ltd == {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'c', 5: 'e', 6: 'f', 7: 'c', 8: 'c'}
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd)):
            pass
        else:
            return(None)
    else:
        pass
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = 0
    if(deepcopy):
        new = copy.deepcopy(ltd)
    else:
        new = ltd
    len = new.__len__()
    start = len
    for i in range(0,len):
        if(new[i]==value):
            start = i
            break
    for i in range(start,len-1):
        new[i] = new [i+1]
    del new[len-1]
    return(new)
def remove_last(ltd,value,**kwargs):
    '''
        by default it will change the original ltd: deepcopy = 0;
        by default check=0: will not check if it is a ltd, return None if it is not a ltd
        ltd = {0:'a',1:'b',2:'c',3:'c',4:'d',5:'c',6:'e',7:'f',8:'c',9:'c'}
        remove_last(ltd,'c') == {0: 'a', 1: 'b', 2: 'c', 3: 'c', 4: 'd', 5: 'c', 6: 'e', 7: 'f', 8: 'c'}
        ltd == {0: 'a', 1: 'b', 2: 'c', 3: 'c', 4: 'd', 5: 'c', 6: 'e', 7: 'f', 8: 'c'}
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd)):
            pass
        else:
            return(None)
    else:
        pass
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = 0
    if(deepcopy):
        new = copy.deepcopy(ltd)
    else:
        new = ltd
    len = new.__len__()
    end = len
    for i in range(len-1,-1,-1):
        if(new[i]==value):
            end = i
            break
    for i in range(end,len-1):
        new[i] = new [i+1]
    del new[len-1]
    return(new)
def remove_all(ltd,value,**kwargs):
    '''
        by default it will change the original ltd: deepcopy = 0;
        by default check=0: will not check if it is a ltd, return None if it is not a ltd
        ltd = {0:'a',1:'b',2:'c',3:'c',4:'d',5:'c',6:'e',7:'f',8:'c',9:'c'}
        remove_all(ltd,'c') == {0: 'a', 1: 'b', 2: 'd', 3: 'e', 4: 'f'}
        ltd == {0: 'a', 1: 'b', 2: 'd', 3: 'e', 4: 'f'}
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd)):
            pass
        else:
            return(None)
    else:
        pass
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = 0
    if(deepcopy):
        new = copy.deepcopy(ltd)
    else:
        new = ltd
    len = new.__len__()
    i = 0
    while(i<len):
        step = 0
        if(new[i]==value):
            for j in range(i,len-1):
                new[j] = new [j+1]
            del new[len-1]
            step = 1
        len = new.__len__()
        i = i + 1 -step
    return(new)
def reverse(ltd,**kwargs):
    '''
        by default it will change the original ltd: deepcopy = 0;
        by default check=0: will not check if it is a ltd, return None if it is not a ltd
        ltd = {0:'a',1:'b',2:'c',3:'c',4:'d',5:'c',6:'e',7:'f',8:'c',9:'c'}
        reverse(ltd) == {0: 'c', 1: 'c', 2: 'f', 3: 'e', 4: 'c', 5: 'd', 6: 'c', 7: 'c', 8: 'b', 9: 'a'}
        ltd == {0: 'c', 1: 'c', 2: 'f', 3: 'e', 4: 'c', 5: 'd', 6: 'c', 7: 'c', 8: 'b', 9: 'a'}
    '''
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd)):
            pass
        else:
            return(None)
    else:
        pass
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = 0
    if(deepcopy):
        new = copy.deepcopy(ltd)
    else:
        new = ltd
    len = new.__len__()
    if(len%2):
        mid = len//2
    else:
        mid = len//2 - 1
    for i in range(0,mid+1):
        temp = new[len-1-i]
        new[len-1-i] = new[i]
        new[i] = temp
    return(new)
def sort(ltd,**kwargs):
    '''
        by default it will change the original ltd: deepcopy = 0;
        by default check=0: will not check if it is a ltd, return None if it is not a ltd
        ltd = {0:'a',1:'b',2:'c',3:'c',4:'d',5:'c',6:'e',7:'f',8:'c',9:'c'}
        sort(ltd) == {0: 'a', 1: 'b', 2: 'c', 3: 'c', 4: 'c', 5: 'c', 6: 'c', 7: 'd', 8: 'e', 9: 'f'}
        ltd == {0: 'a', 1: 'b', 2: 'c', 3: 'c', 4: 'c', 5: 'c', 6: 'c', 7: 'd', 8: 'e', 9: 'f'}
    '''
    if('inverse' in kwargs):
        inverse = kwargs['inverse']
    else:
        inverse = False
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd)):
            pass
        else:
            return(None)
    else:
        pass
    if('deepcopy' in kwargs):
        deepcopy = kwargs['deepcopy']
    else:
        deepcopy = 0
    if(deepcopy):
        new = copy.deepcopy(ltd)
    else:
        new = ltd
    len = new.__len__()
    ol = sorted(new.items(), key=itemgetter(1),reverse=inverse)
    for i in range(0,ol.__len__()):
        new[i] = ol[i][1]
    return(new)

def comprise(ltd1,ltd2,**kwargs):
    if('strict' in kwargs):
        strict = kwargs['strict']
    else:
        strict = 1
    if('check' in kwargs):
        check = kwargs['check']
    else:
        check = 0
    if(check):
        if(is_ltdict(ltd1)):
            pass
        else:
            return(None)
        if(is_ltdict(ltd2)):
            pass
        else:
            return(None)
    else:
        pass
    len_1 = ltd1.__len__()
    len_2 = ltd2.__len__()
    if(len_2>len_1):
        return(False)
    else:
        ltd1 = to_list(ltd1)
        ltd2 = to_list(ltd2)
        if(strict):
            if(ltd2 == ltd1[:len_2]):
                return(True)
            else:
                return(False)
        else:
            end = len_1 - len_2
            for i in range(0,end+1):
                if(ltd2 == ltd1[i:(i+len_2)]):
                    return(True)
                else:
                    pass
            return(False)
           

def naturalize_intkeydict(ikd):
    ltd = {}
    ks = sorted(list(ikd.keys()))
    for i in range(0,ks.__len__()):
        ltd[i] = ikd[ks[i]]
    return(ltd)
 
