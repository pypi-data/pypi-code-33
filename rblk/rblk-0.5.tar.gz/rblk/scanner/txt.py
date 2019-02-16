import rblk.mat.engine as mtmt
import rblk.tag.txt as tgtg
import rblk.ele.txt as etet
from  rblk.utils import fsm

#######unify params

def dcd_params(d):
    cursor = d['cursor']
    input_symbol = d['input_symbol']
    curr_state = d['curr_state']
    curr_depth = d['curr_depth']
    curr_breadth = d['curr_breadth']
    loc_stack = d['loc_stack']
    state_stack = d['state_stack']
    mat = d['mat']
    tag_pairs = d['tag_pairs']
    return((cursor,input_symbol,curr_state,curr_depth,curr_breadth,loc_stack,state_stack,mat,tag_pairs))

def encd_params(cursor,input_symbol,curr_state,curr_depth,curr_breadth,loc_stack,state_stack,mat,tag_pairs):
    d = {}
    d['cursor'] = cursor
    d['input_symbol'] = input_symbol
    d['curr_state'] = curr_state
    d['curr_depth'] = curr_depth
    d['curr_breadth'] = curr_breadth
    d['loc_stack'] = loc_stack
    d['state_stack'] = state_stack
    d['mat'] = mat
    d['tag_pairs'] = tag_pairs
    return(d)

def init_params_dict():
    d = {
        "cursor":None,
        "input_symbol":None,
        "curr_state":None,
        "curr_depth":None,
        "curr_breadth":None,
        "loc_stack":None,
        "state_stack":None,
        "mat":None,
        "tag_pairs":None
    }
    return(d)

##############

def init(txt,tag_pairs=tgtg.DFLT_PAIRS,**kwargs):
    if("root_tag" in kwargs):
        root_tag = kwargs['root_tag']
    else:
        root_tag = tgtg.ROOT
    if("implicit_tag" in kwargs):
        implicit_tag = kwargs['implicit_tag']
    else:
        implicit_tag = tgtg.IMPLICIT
    root_ele = etet.new_root_ele(0,len(txt))
    desc_mat = {}
    mtmt._set_via_loc_forcefully(desc_mat,[0,0],root_ele)
    d = init_params_dict()
    d["curr_state"] = "INIT"
    d["curr_depth"] = 0
    d["curr_breadth"] = 0
    d["loc_stack"] = [[0,0]]
    d["state_stack"] = ["INIT"]
    d["mat"] = desc_mat
    tag_pairs[root_tag] = root_tag
    tag_pairs[implicit_tag] = implicit_tag
    d["tag_pairs"] = tag_pairs
    return(d)


####open tag 

def exopen(d):
    '''
        creat new ele
        update si,tag,pbreadth,depth,breadth,
        add ele,to mat
        append ele_loc  to stack
    '''
    cursor,input_symbol,curr_state,curr_depth,curr_breadth,loc_stack,state_stack,mat,tag_pairs = dcd_params(d)
    parent_ele = mtmt._get_via_loc(mat,loc_stack[-1])
    curr_ele = etet.new_ele()
    curr_ele['si'] = cursor
    curr_ele['tag'] = input_symbol
    curr_ele['pbreadth'] = parent_ele['breadth']
    curr_depth = curr_depth + 1
    curr_breadth,curr_ele = mtmt._dfs_set_and_update_value(mat,curr_depth,curr_ele)
    loc = etet.ele2loc(curr_ele)
    loc_stack.append(loc)
    state_stack.append(curr_state)
    d = encd_params(cursor,input_symbol,curr_state,curr_depth,curr_breadth,loc_stack,state_stack,mat,tag_pairs)
    return(d)


def imopen(d):
    d['input_symbol'] = tgtg.IMPLICIT
    return(exopen(d))


#####close tag
def _close(ei,cursor,input_symbol,curr_state,curr_depth,curr_breadth,loc_stack,state_stack,mat,tag_pairs):
    '''
        ele already in mat
        update ei
        pop ele_loc from loc_stack to expose parent-ele
        update curr_depth curr_breadth to parent
    '''
    #update and pop last_ele
    curr_ele = mat[curr_depth][curr_breadth]
    curr_ele['ei'] = ei
    loc_stack.pop(-1)
    state_stack.pop(-1)
    #get curr_ele
    curr_ele = mtmt._get_via_loc(mat,loc_stack[-1])
    curr_depth = curr_ele['depth']
    curr_breadth = curr_ele['breadth']
    return((cursor,input_symbol,curr_state,curr_depth,curr_breadth,loc_stack,state_stack,mat,tag_pairs))

def imclose(d):
    ele = mtmt._get_via_loc(d['mat'],d['loc_stack'][-1])
    if(ele['tag'] != tgtg.IMPLICIT):
        return(d)
    else:
        cursor,input_symbol,curr_state,curr_depth,curr_breadth,loc_stack,state_stack,mat,tag_pairs = dcd_params(d)
        cursor,input_symbol,curr_state,curr_depth,curr_breadth,loc_stack,state_stack,mat,tag_pairs = _close(cursor,cursor,input_symbol,curr_state,curr_depth,curr_breadth,loc_stack,state_stack,mat,tag_pairs)
        d = encd_params(cursor,input_symbol,curr_state,curr_depth,curr_breadth,loc_stack,state_stack,mat,tag_pairs)
        return(d)

def exclose(d):
    cursor,input_symbol,curr_state,curr_depth,curr_breadth,loc_stack,state_stack,mat,tag_pairs = dcd_params(d)
    cursor,input_symbol,curr_state,curr_depth,curr_breadth,loc_stack,state_stack,mat,tag_pairs = _close(cursor+1,cursor,input_symbol,curr_state,curr_depth,curr_breadth,loc_stack,state_stack,mat,tag_pairs)
    d = encd_params(cursor,input_symbol,curr_state,curr_depth,curr_breadth,loc_stack,state_stack,mat,tag_pairs)
    return(d)

#####

        
##############################################
##############################################

def final_exopen(d):
    print("some opened tag not closed,please check the params_dict['mat'] whose ei is None")
    return(d)

def final_imopen(d):
    cursor,input_symbol,curr_state,curr_depth,curr_breadth,loc_stack,state_stack,mat,tag_pairs = dcd_params(d)
    curr_ele = mtmt._get_via_loc(mat,loc_stack[-1])
    curr_ele['ei'] = d['cursor'] + 1 
    loc_stack.pop(-1)
    state_stack.pop(-1)
    d = encd_params(cursor,input_symbol,curr_state,curr_depth,curr_breadth,loc_stack,state_stack,mat,tag_pairs)
    return(d)

#####################
#####################

def get_descmat(txt,tag_pairs=tgtg.DFLT_PAIRS):
    stream = txt
    init_state = "INIT"
    params_dict = init(stream,tag_pairs=tag_pairs)
    machine = fsm.FSM(stream=stream,params_dict=params_dict,init_state=init_state)
    machine.add("INIT",tgtg.is_ltag_only,exopen,"EXOPEN")
    machine.add("INIT",tgtg.is_rtag_of,exclose,"INIT")
    #############
    machine.add("INIT",tgtg.is_lrtag_and_not_rtag_of,exopen,"EXOPEN")
    machine.add("INIT",tgtg.is_rtag_only_and_not_rtag_of,imopen,"IMOPEN")
    machine.add("INIT",tgtg.is_not_tag,imopen,"IMOPEN")
    ###########
    ###########
    machine.add("IMOPEN",tgtg.is_ltag_only,fsm.pipeline([imclose,exopen]),"EXOPEN")
    machine.add("IMOPEN",tgtg.is_rtag_of_sec,fsm.pipeline([imclose,exclose]),"INIT")
    machine.add("IMOPEN",tgtg.is_lrtag_and_not_rtag_of_sec,fsm.pipeline([imclose,exopen]),"EXOPEN")
    machine.add("IMOPEN",tgtg.is_rtag_only_and_not_rtag_of_sec,None,"IMOPEN")
    machine.add("IMOPEN",tgtg.is_not_tag,None,"IMOPEN")
    machine.add("EXOPEN",tgtg.is_ltag_only,exopen,"EXOPEN")
    machine.add("EXOPEN",tgtg.is_rtag_of,exclose,"INIT")
    machine.add("EXOPEN",tgtg.is_lrtag_and_not_rtag_of,exopen,"EXOPEN")
    machine.add("EXOPEN",tgtg.is_rtag_only_and_not_rtag_of,imopen,"IMOPEN")
    machine.add("EXOPEN",tgtg.is_not_tag,imopen,"IMOPEN")
    machine.add_final("IMOPEN",final_imopen)
    machine.add_final("EXOPEN",final_exopen)
    machine.add_final("INIT",None)
    machine.scan()
    desc_mat = machine.params_dict['mat']
    return(desc_mat)



