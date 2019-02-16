
def new_ele():
    d = {
        "tag": None,
        "breadth": None,
        "depth": None,
        "pbreadth":None,
        "si":None,
        "ei":None
    }
    return(d)

def new_root_ele(txtsi,txtei):
    d = new_ele()
    d['tag'] = "root"
    d['pbreadth'] = -1
    d['depth'] = 0
    d['breadth'] = 0
    d['si'] = txtsi
    d['ei'] = txtei
    return(d)


def ele2loc(ele):
    return([ele['depth'],ele['breadth']])



