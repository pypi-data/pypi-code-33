from .workflows import BUGTRACK_WORKFLOW

def get_next_statuses(bug, next_state=False):
    statuses = BUGTRACK_WORKFLOW
    state = bug.bugstatus.code
    print('1')
    if state in statuses:
        print('2')
        if next_state:
            print('3')
            return next_state in statuses[state]
        else:
            return [st for st in statuses[state]]
    else:
        return False