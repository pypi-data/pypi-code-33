__all__ = [
    "_is_ltag",
    "_is_not_ltag",
    "_is_rtag",
    "_is_not_rtag",
    "_is_tag",
    "_is_not_tag",
    "_is_ltag_of",
    "_is_not_ltag_of",
    "_is_rtag_of",
    "_is_not_rtag_of",
    "_is_pair_of",
    "_is_not_pair_of",
    "_is_not_ltag_and_not_rtag_of"
]

####

def _is_ltag(tag,tag_pairs):
    cond = (tag in tag_pairs)
    return(cond)

def _is_not_ltag(tag,tag_pairs):
    return(not(_is_ltag(tag,tag_pairs)))

def _is_rtag(tag,tag_pairs):
    cond = (tag in list(tag_pairs.values()))
    return(cond)

def _is_not_rtag(tag,tag_pairs):
    return(not(_is_rtag(tag,tag_pairs)))

def _is_tag(tag,tag_pairs):
    cond1 = (tag in tag_pairs)
    cond2 = (tag in list(tag_pairs.values()))
    return((cond1 or cond2))

def _is_not_tag(tag,tag_pairs):
    return(not(_is_tag(tag,tag_pairs)))

def _is_ltag_of(tag1,tag2,tag_pairs):
    cond = (tag_pairs[tag1] == tag2)
    return(cond)

def _is_not_ltag_of(tag1,tag2,tag_pairs):
    return(not(is_ltag_of(tag1,tag2,tag_pairs)))

def _is_rtag_of(tag1,tag2,tag_pairs):
    cond = (tag_pairs[tag2] == tag1)
    return(cond)

def _is_not_rtag_of(tag1,tag2,tag_pairs):
    return(not(_is_rtag_of(tag1,tag2,tag_pairs)))

def _is_pair_of(tag1,tag2,tag_pairs):
    cond1 = _is_ltag_of(tag1,tag2,tag_pairs)
    cond2 = _is_rtag_of(tag1,tag2,tag_pairs)
    return((cond1 or cond2))

def _is_not_pair_of(tag1,tag2,tag_pairs):
    return(not(_is_pair_of(tag1,tag2,tag_pairs)))


#####

def _is_not_ltag_and_not_rtag_of(tag1,tag2,tag_pairs):
    cond1 = _is_not_ltag(tag1,tag_pairs)
    cond2 = _is_not_rtag_of(tag1,tag2,tag_pairs)
    return((cond1 and cond2))

#####

