def firstValid(*iterable):
    '''Return the first non-None value in the list
    '''
    try:
        return list((el for el in iterable if el is not None))[0]
    except:
        return None

def lcase_keys(d):
    '''Return a dictionary object with all keys having been lowercased
    '''
    return dict(([k.lower(),v] for k,v in d.items()))

def rangePick(target, min, max):
    '''Validates an integer target from within a min/max boundary. If target is outside the defined range then return the range boundary as the choice
    
    :param target: The desired answer
    :type target: int
    :param min: The lowest possible value allowed
    :type min: int
    :param max: The highest possible value allowed
    :type max: int
    :return: An integer as close to target as possible given the defined range
    :rtype: int
    '''
    
    if int(target) < int(min):
        return int(min)
    if int(target) > int(max):
        return int(max)
    return int(target)

def str2bool(testcase):
    '''Given a string containing the typically valid boolean answers that can be found in yaml, json or other encoded/marshaled data provide a boolean answer.
    
    :param testcase: Value to be evaluated
    :type testcase: None, Int, Bool or Str
    :return: default is False unless truthyness can be determined
    :rtype: bool
    '''
    
    # NoneType is clearly False
    if testcase is None:
        return False
      
    # Ok, this is redundant, but lets make the function transparent
    if isinstance(testcase,bool):
        return testcase
    
    # Slightly less redundant, but again we are transparent
    if isinstance(testcase,int):
        return testcase == 0

    # Not sure what else should be considered here
    return testcase.lower() in ('yes', 'true', 't', 'y', '0')

def name_of(obj):
    '''Returns the name of the object supplied
    :rtype: str
    '''
    
    mod = type(obj).__module__.split('.')
    
    if mod[-1] == obj.__class__.__name__:
        return str(type(obj).__module__)
        
    else:
        return str(".".join( [type(obj).__module__,obj.__class__.__name__] ))
        
def function_name(offset=1):
    '''Returns the name of the calling function
    :param offset: How far back in the callstack should be followed to find the caller (default is 1)
    :type offset: int
    :return: name of code object
    :rtype: str
    '''
    
    import sys
    return str(sys._getframe(offset).f_code.co_name)


def treeGet(following, what, defaultAnswer=None):
    '''
    This function helps to navigate structures of lists and dictionaries with the same functionality of the get method of a dictionary without having to string a series of objects together.
    
    Short Example based on myTree below:
        classic python: 
            myTree.get('list',[None,{}])[1].get('test','unknown')
        treeGet python
            treeGet(myTree,'list[1].test','unknown')
            
        In the classic case, the default for list must contain a default answer capable of getting to the suceeding get (which means a dict). If we had been exploring element 10 the default answer would have been more complicated
    
    Example - Given an object structured as follows:
        myTree = {
            'dict': {
                'one': 1,
                'two': '2',
                'three': False
                },
                'list': [
                    'a',
                    { 'test': 'answer'},
                    3
                ],
                'string': 'test'
        }
        
        accessing test to retrieve answer would look something like the following.
            a = myTree.get('dict',{}).get('list',[None,None])[1].get('test','defaultanswer')
            
        Depending on how many items were expected in the "list" the default answer of [None,None] would have to be expanded to prevent the following [1] from failing. Also typically people would wrap this with a try/except to catch any unexpected failures
        
            try:
                a = myTree.get('dict',{}).get('list',[None,None])[1].get('test','defaultanswer')
            except:
                a = 'defaultanswer'
            
        This function provides all of the above as well as cloning each of the items as the tree is traversed so the return object is mutable and un-tied from the object from which it originated
    
            a = utils.treeGet(myTree, 'dict.list[1].test', 'defaultanswer')
            
    '''
    
    tree = what.split('.')
    for nextbranch in tree:
        # Create mutable copy of the current object we are chasing through
        #
        if isinstance(following, dict):
            following = dict(following)
            
        if isinstance(following, list):
            following = list(following)
        
        index = None

        # if the next step in the tree starts with a bracket then we are doing a simple list accessor
        #
        if nextbranch.startswith('['):
            if not isinstance(following,list):    # If we are not chasing a list, then we will fail
                return defaultAnswer
                
            index = int(nextbranch.split('[')[1].split(']')[0])
            
        # If we were given a composite term 'key[index]' which means we will do both a 
        # dictionary get followed by a list index accessor
        #
        elif nextbranch.endswith(']'):
            following = following.get(nextbranch.split('[',1)[0], None) # key is what comes before the bracket
            alphaindex = nextbranch.split('[',1)[1].split(']',1)[0] # index is what is between the brackets

            # if someone tried to do a index "range" we do not currently support that
            #
            if ':' in alphaindex:
                return defaultAnswer
                
            index = int(alphaindex) # was done in two steps so we can validate that the index is purely numeric

        # otherwise we are simply accesssing the next key in a dictionary
        #
        else:
            following = following.get(nextbranch, None)
        
        # If we didn't survive parsing the nextBranch then fail
        #        
        if following is None:
            return defaultAnswer
        
        # If we have an index, then validate and access the entry in the list
        # we DO NOT support range index [1:2]
        #
        if index is not None:
            # If we are not looking at a list, then return
            #
            if not isinstance(following, list):
                return defaultAnswer
                
            # If we are looking at positive indexes, validate the range
            #
            if index > -1 and len(following) < index:
                return defaultAnswer
            
            # Otherwise if we are looking at a negitive index validate the depth in reverse
            elif index < 0 and len(following) < abs(index):
                return defaultAnswer
                
            following = following[index]
                  
    #print ("Returning {}".format(following))
    return following
            
def asList(obj):
    '''Always returns a list, wrapping any other object type into a list
    
    :param obj: The value to be wrapped if necessary
    :type obj: Any
    :return: obj if it was already a list, otherwise object wrapped in a list
    :rtype: list
    '''
    
    if isinstance(obj,list):
        return obj
    else:
        return list([obj])
    
def listContains(thisString, thisList):
    '''Evaluates a list (or list of lists) for presence of thisString 
    
    :param thisString: Value being sought
    :type thisString: str
    :param thisList: List to scan for the value being sought
    :type thisList: list
    :raises: TypeError
    :return: True or False
    :rtype: bool
    '''
    
    if not isinstance(thisList,list):
        raise TypeError
    if not isinstance(thisString,str):
        raise TypeError

    return bool(len( list(filter(lambda x: thisString in x, thisList)) ) > 0)
    
def validNumber(valueToTest):
    '''Determines if valueToTest is considered to be a number. This includes strings representing a number. 
    If an int or float are passed then the answer is True. 
    
    If a string is provided it is evaluated to only contain digits, sign and a decimal point. string evaluation does not yet take into account nationalization such as comma for seperating 1000's or any financial symbology
    
    :param valueToTest: variable to consider
    :type valueToTest: Any
    
    :return: True or False
    :rtype: bool
    
    '''
    if isinstance(valueToTest,(int, float)):
        return True
    
    if isinstance(valueToTest,(str)):
        import re
        match = re.match("^[-0123456789.]*$", valueToTest)
        return match is not None
        
    return False

def validInt(valueToTest):
    '''Determines if valueToTest is considered to be a number. This includes strings representing a number. 
    If an int is passed then the answer is True. 
    
    If a string is provided it is evaluated to only contain digits and sign. string evaluation does not yet take into account nationalization such as comma for seperating 1000's or any financial symbology
    
    :param valueToTest: variable to consider
    :type valueToTest: Any
    
    :return: True or False
    :rtype: bool
    '''
    
    if isinstance(valueToTest,(int)):
        return True
        
    if isinstance(valueToTest,(str)):
        import re
        match = re.match("^[-0123456789]*$", valueToTest)
        return match is not None
        
    return False
