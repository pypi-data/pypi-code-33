import rblk.mat.engine as mtmt
from rblk.tag.engine import * 
import elist.elist as elel
import edict.edict as eded

ROOT = "root"
IMPLICIT = "null"
DFLT_PAIRS = {
    "{":"}",
    "[":"]",
    "(":")",
    "<":">",
    "'":"'",
    '"':'"'
}
#####

def str2pairs(s):
    arr = list(s)
    kl = elel.select_evens(arr)
    vl = elel.select_odds(arr)
    d = eded.kvlist2d(kl,vl)
    return(d)

def pairs2str(d):
    kl,vl =eded.d2kvlist(d)
    arr = elel.interleave(kl,vl)
    s = elel.join(arr,"")
    return(d)

#####
def get_tag_from_loc_stack(d,which):
    try:
        tag = mtmt._get_via_loc(d['mat'],d['loc_stack'][which])['tag']
    except:
        tag = None
    else:
        pass
    return(tag)

#有些情况需要回溯，所以采用下面的形式

def dcd_params(d):
    curr_tag = d['input_symbol']
    stack_top_tag = get_tag_from_loc_stack(d,-1)
    stack_sec_tag = get_tag_from_loc_stack(d,-2)
    tag_pairs = d['tag_pairs']
    return((curr_tag,stack_top_tag,stack_sec_tag,tag_pairs))

def is_ltag(d):
    curr_tag,stack_top_tag,stack_sec_tag,tag_pairs = dcd_params(d)
    return(_is_ltag(curr_tag,tag_pairs))

def is_not_ltag(d):
    curr_tag,stack_top_tag,stack_sec_tag,tag_pairs = dcd_params(d)
    return(_is_not_ltag(curr_tag,tag_pairs))

def is_rtag(d):
    curr_tag,stack_top_tag,stack_sec_tag,tag_pairs = dcd_params(d)
    return(_is_rtag(curr_tag,tag_pairs))

def is_not_rtag(d):
    curr_tag,stack_top_tag,stack_sec_tag,tag_pairs = dcd_params(d)
    return(_is_not_rtag(curr_tag,tag_pairs))


def is_ltag_only(d):
    cond1 = is_ltag(d)
    cond2 = is_not_rtag(d)
    return((cond1 and cond2))

def is_not_ltag_only(d):
    return(not(is_ltag_only(d)))

def is_rtag_only(d):
    cond1 = is_rtag(d)
    cond2 = is_not_ltag(d)
    return((cond1 and cond2))

def is_not_rtag_only(d):
    return(not(is_rtag_only(d)))

def is_lrtag(d):
    cond1 = is_ltag(d)
    cond2 = is_rtag(d)
    return((cond1 and cond2))

def is_not_lrtag(d):
    return(not(is_lrtag(d)))


def is_tag(d):
    curr_tag,stack_top_tag,stack_sec_tag,tag_pairs = dcd_params(d)
    return(_is_tag(curr_tag,tag_pairs))

def is_not_tag(d):
    curr_tag,stack_top_tag,stack_sec_tag,tag_pairs = dcd_params(d)
    return(_is_not_tag(curr_tag,tag_pairs))

def is_ltag_of(d):
    curr_tag,stack_top_tag,stack_sec_tag,tag_pairs = dcd_params(d)
    return(_is_ltag_of(curr_tag,stack_top_tag,tag_pairs))

def is_not_ltag_of(d):
    curr_tag,stack_top_tag,stack_sec_tag,tag_pairs = dcd_params(d)
    return(_is_not_ltag_of(curr_tag,stack_top_tag,tag_pairs))

def is_rtag_of(d):
    curr_tag,stack_top_tag,stack_sec_tag,tag_pairs = dcd_params(d)
    return(_is_rtag_of(curr_tag,stack_top_tag,tag_pairs))

def is_not_rtag_of(d):
    curr_tag,stack_top_tag,stack_sec_tag,tag_pairs = dcd_params(d)
    return(_is_not_rtag_of(curr_tag,stack_top_tag,tag_pairs))

def is_pair_of(d):
    curr_tag,stack_top_tag,stack_sec_tag,tag_pairs = dcd_params(d)
    return(_is_pair_of(curr_tag,stack_top_tag,tag_pairs))

def is_not_pair_of(d):
    curr_tag,stack_top_tag,stack_sec_tag,tag_pairs = dcd_params(d)
    return(_is_not_pair_of(curr_tag,stack_top_tag,tag_pairs))

def is_not_ltag_and_not_rtag_of(d):
    curr_tag,stack_top_tag,stack_sec_tag,tag_pairs = dcd_params(d)
    return(_is_not_ltag_and_not_rtag_of(curr_tag,stack_top_tag,tag_pairs))

def is_rtag_of_sec(d):
    curr_tag,stack_top_tag,stack_sec_tag,tag_pairs = dcd_params(d)
    return(_is_rtag_of(curr_tag,stack_sec_tag,tag_pairs))

def is_not_rtag_of_sec(d):
    return(not(is_rtag_of_sec(d)))

def is_not_ltag_and_not_rtag_of_sec(d):
    cond1 = is_not_ltag(d)
    cond2 = is_not_rtag_of_sec(d)
    return((cond1 and cond2))

def is_rtag_and_not_rtag_of(d):
    cond1 = is_rtag(d)
    cond2 = is_not_rtag_of(d)
    return((cond1 and cond2))

def is_rtag_and_not_rtag_of_sec(d):
    cond1 = is_rtag(d)
    cond2 = is_not_rtag_of_sec(d)
    return((cond1 and cond2))

def is_lrtag_and_not_rtag_of_sec(d):
    cond1 = is_lrtag(d)
    cond2 = is_not_rtag_of_sec(d)
    return((cond1 and cond2))

def is_lrtag_and_not_rtag_of(d):
    cond1 = is_lrtag(d)
    cond2 = is_not_rtag_of(d)
    return((cond1 and cond2))

def is_rtag_only_and_not_rtag_of(d):
    cond1 = is_rtag_only(d)
    cond2 = is_not_rtag_of(d)
    return((cond1 and cond2))

def is_rtag_only_and_not_rtag_of_sec(d):
    cond1 = is_rtag_only(d)
    cond2 = is_not_rtag_of_sec(d)
    return((cond1 and cond2))

