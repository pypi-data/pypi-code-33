import elist.elist as elel
from rblk.utils import ltdict as ltlt

####
def _get_via_loc(mat,loc):
    depth = loc[0]
    breadth = loc[1]
    return(mat[depth][breadth])

####

def _set_via_loc_forcefully(mat,loc,value):
    depth = loc[0]
    breadth = loc[1]
    if(depth in mat):
        mat[depth][breadth] = value
    else:
        mat[depth] = {}
        mat[depth][breadth] = value


def _set_via_loc_when_loc_exist(mat,loc,value):
    depth = loc[0]
    breadth = loc[1]
    if(depth in mat):
        if(breadth in mat[depth]):
            mat[depth][breadth] = value
        else:
            raise(IndexError("breadth",breadth))
    else:
        raise(IndexError("depth",depth))


def _dfs_set_and_update_value(mat,depth,value):
    value['depth'] = depth
    if(depth in mat):
        breadth = len(mat[depth])
    else:
        mat[depth] = {}
        breadth = 0
    value['breadth'] = breadth
    mat[depth][breadth] = value
    return((breadth,value))



####

def _get_layer_lengths(mat):
    arr = elel.mapv(mat,lambda layer:len(layer))
    return(arr)

####

def _init(mat,layer_lengths,value=None):
    mat = {}
    for i in range(len(layer_lengths)):
        layer = elel.init(layer_lengths[i],value)
        layer = ltlt.list2ltdict(layer)
        mat[i] = layer
    return(mat)

####
