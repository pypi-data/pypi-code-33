
def dict_updates(old, new):
    updates = {}

    for k in set(new.keys()).intersection(set(old.keys())):
        if old[k] != new[k]:
            updates.update({k: new[k]})

    return updates
