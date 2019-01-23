'''
git defines an api for running git opperartions in DOT_ROOT

The Public interface returns a Bool on the success of the opperation
'''

import mold.util.system as system 

# PRIVATE
def _git_exec(ctx, args):
    system.cd(ctx.MOLD_ROOT)
    return system.exec('git ' + args)

def _git_shell(ctx, args):
    system.cd(ctx.MOLD_ROOT)
    return system.shell('git ' + args)

def _check_remote_uri(ctx, uri=None):
    '''checks that a git remote uri is valid'''
    print(f'Checking {uri}: ', end='')
    result = _git_exec(ctx, 'ls-remote ' + uri)
    if not result.check_ok():
        print(f'Sorry, that a not valid remote uri.') 
        return result
    print('OK')
    return result

def _check_has_remote(ctx):
    r = _git_exec(ctx, 'remote -v')
    if not r.check_ok() or not r.out:
        return False
    return True

def _get_remote_name(ctx):
    r = _git_exec(ctx, 'remote -v')
    if not r.check_ok() or not r.out:
        return None
    try:
        return r.out.split(' ')[0].split('\t')[0]
    except: 
        return None

def _get_remote_uri(ctx):
    r = _git_exec(ctx, 'remote -v')
    if not r.check_ok() or not r.out:
        return None
    try:
        return r.out.split(' ')[0].split('\t')[1]
    except: 
        return None

def _get_current_branch(ctx):
    r = _git_exec(ctx, 'branch')
    if not r.check_ok() or not r.out:
        print('fooey', r.check_ok())
        return None
    try:
        for branch in r.out.split('\n'):
            if branch.strip().startswith('*'):
                return branch.replace('*', '').strip()
    except: 
        return None

def _set_remote(ctx, uri=None, remote_name='origin'):
    '''works as both git add and git set for the MOLD_ROOT'''
    if not uri:
        return system.fail()
    if not _check_remote_uri(ctx, uri).check_ok():
        return system.fail()
    _git_exec(ctx, 'remote remove ' + remote_name)  # remove and ignore failure (if no remote)
    result = _git_shell(ctx, f'remote add {remote_name} {uri}')
    if not result.check_ok():
        return result
    result = _git_shell(ctx, f'fetch --all -v')
    if not result.check_ok():
        print(f'WARNING: failed to git fetch {remote_name}')
        return result 
    print(f'MOLD_ROOT\'s git remote {remote_name} is now:', uri)
    return result 

# API INTERFACE
def set_origin(ctx, uri):
    return _set_remote(ctx, uri, 'origin')

def set_upstream(ctx, uri):
    return _set_remote(ctx, uri, 'upstream')

def add(ctx):
    return _git_shell(ctx, 'add -A')

def status(ctx):
    return _git_shell(ctx, 'status')

def remote(ctx):
    return _git_shell(ctx, 'remote -v')

def diff(ctx, githash=None):
    if not githash:
        githash= 'HEAD'
    return _git_shell(ctx, f'diff {githash}')

def commit(ctx, message=None):
    sign = '-S' if ctx.MOLD_SIGN else ''
    if message:
        return _git_shell(ctx, f"commit {sign} -m '{message}'")
    return _git_shell(ctx, f'commit -v {sign}')

def hard_reset(ctx, githash=None):
    if not githash:
        githash = 'HEAD'
    return _git_shell(ctx, f"reset --hard {githash}")

def soft_reset(ctx, githash=None):
    if not githash:
        githash = 'HEAD'
    return _git_shell(ctx, f"reset --soft {githash}")

def log(ctx):
    return _git_shell(ctx, 'log --graph --oneline --tags')

def branch(ctx):
    return _git_shell(ctx, 'branch -av')

def fetch(ctx):
    return _git_shell(ctx, 'fetch -v --all')

def merge(ctx, branch=None):
    print('merging', branch)
    if not branch:
        branch = 'HEAD'
    return _git_shell(ctx, f'merge {branch}')

def checkout(ctx, branch=None):
    if not branch:
        branch = 'HEAD'
    return _git_shell(ctx, f'checkout  {branch}')

def new_branch(ctx, branch=None):
    if not branch:
        return system.fail()
    return _git_shell(ctx, f'checkout -b {branch}')

def pull(ctx, branch=None):
    if not _check_has_remote(ctx):
        print('ERROR: no remote origin unable to push')
        return system.fail()
    if not branch:
        branch = _get_current_branch(ctx)
    return _git_shell(ctx, f'pull origin {branch}')

def push(ctx, branch=None):
    if not _check_has_remote(ctx):
        print('ERROR: no remote origin unable to push')
        return system.fail()
    if not branch:
        branch = 'HEAD'
    return _git_shell(ctx, f'push origin {branch}')

def force_push(ctx, branch=None):
    if not _check_has_remote(ctx):
        print('ERROR: no remote origin unable to push')
        return system.fail()
    if not branch:
        branch = 'HEAD'
    _git_shell(ctx, f'push origin {branch} --force')

def clone(ctx, uri=None):
    # clone uses system.exec and shell because there is not MOLD_ROOT to cd into
    if not uri:
        print('ERROR: git clone requires a git-uri')
        return system.fail()
    # DO NOT refactor to USE _check_remote_uri because it will try to cd to MOLD_ROOT 
    # whitch does not exits 
    print(f'Checking {uri}: ', end='')
    result = system.exec('git ls-remote ' + uri)
    if not result.check_ok():
        print(f'Sorry, that a not valid remote uri.') 
        return result
    print('OK')
    return system.shell(f'git clone {uri} {ctx.MOLD_ROOT}' )

def init(ctx):
    sign = '-S' if ctx.MOLD_SIGN else ''
    result = _git_shell(ctx, 'init .')
    if not result.check_ok():
        print('Error: git init failed')
        return result
    result = _git_shell(ctx, 'add -A')
    if not result.check_ok():
        print('Error: git add -A failed')
        return result
    result = _git_shell(ctx, f'commit {sign} -m "initial commit"') 
    if not result .check_ok():
        print('Error: inital git commit failed')
    return result 

