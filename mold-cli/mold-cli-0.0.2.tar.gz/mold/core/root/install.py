'''
install defines an api for installing a MOLD_ROOT.
'''

from mold.util import fs, git, system

# PRIVATE
BUILD_DIR = __file__.replace('install.py', '../../asset')

def _log_success(ctx, extra='.'):
    reset = ctx.reset
    green = ctx.green
    yellow = ctx.yellow
    magenta = ctx.magenta
    print(f'''
{green}SUCCESS{reset}
A MOLD_ROOT has installed to {ctx.MOLD_ROOT}{extra}
{yellow}Follow these IMPORTANT instructions to complete setting up mold.{reset}
First add the follwing two lines to your shell config file (i.e. ~/.bashrc).
    {magenta}export MOLD_ROOT='{ctx.MOLD_ROOT}'
    source $MOLD_ROOT/mold-loader.sh{reset}
Next source your shell config (e.g. "source ~/.bashrc"). 
Then then you will be good to go, {green}Enjoy mold!{reset} :)''')

def _log_warning(ctx, extra='.'):
    reset = ctx.reset
    red = ctx.red
    green = ctx.green
    yellow = ctx.yellow
    magenta = ctx.magenta
    print(f'''
{red}!WARNING!{reset}
{yellow}A MOLD_ROOT directory was installed to {ctx.MOLD_ROOT}{extra}{yellow}
{yellow}If you dont want to re-install, follow these IMPORTANT instructions to complete setting up mold.{reset}
{yellow}First add the follwing two lines to your shell config file (i.e. ~/.bashrc).{reset}
    {magenta}export MOLD_ROOT='{ctx.MOLD_ROOT}'
    source $MOLD_ROOT/mold-loader.sh{reset}
{yellow}Next source your shell config (e.g. "source ~/.bashrc").{reset} 
{yellow}Then then you will be good to go, {green}Enjoy mold!{reset} :)''')

def _fail(ctx):
    reset = ctx.reset
    red = ctx.red
    print(f'''{red}Sorry, something went wrong, a MOLD_ROOT was not installed.{reset}
You can create an issue at https://github.com/slugbyte/mold/issues for support.''')
    return ctx.FAIL

def _create_mold_root(ctx):
    try:
        if fs.exists(ctx.MOLD_ROOT):
            fs.rimraf(ctx.MOLD_ROOT)
        fs.copy_dir(BUILD_DIR + '/mold_root', ctx.MOLD_ROOT)
        return True
    except: 
        return False

def _setup_git(ctx, remote):
    system.cd(ctx.MOLD_ROOT)
    return git.init(ctx, remote)

# RETURN TRUE FOR CONTINE FALSE FOR EXIT
def _handle_mold_root_exists(ctx):
    red = ctx.red
    cyan = ctx.cyan
    reset = ctx.reset
    if ctx.check_flag_set('--force'):
        return True
    if fs.exists(ctx.MOLD_ROOT):
        if ctx.check_flag_set('--no-prompt') and not ctx.check_flag_set('--force'):
            print(f'''Sorry, {ctx.MOLD_ROOT} allread exists
    Use the interactive installer or the flag '--force' to overwrite it.''')
            return False

        print(f'{red}Hmm,{reset} {ctx.MOLD_ROOT} {red}allready exits.{reset}')
        cancel = 'y' != input(f'{cyan}Do you want to remove it and continue? y/n:{reset} ').strip()
        if cancel: 
            print(f'Ok, MOLD_ROOT installation canceled.')
            return False
    return True

def _handle_mold_root_set_origin(ctx):
    red = ctx.red
    cyan = ctx.cyan
    reset = ctx.reset
    remote = ''
    if not ctx.check_flag_set('--no-prompt'):
        cancel = 'y' != input(f'{cyan}Do you want to setup a git remote? y/n:{reset} ').strip()
        if cancel: 
            print(f'Ok, no git remote will be configured.')
        else: 
            remote = input(f'{cyan}Enter a git remote uri:{reset} ').strip()
    if not remote:
        _log_success(ctx, f''' 
{red}WARNING: your mold-root was created with out a remote remote repository.
    run {cyan}'mold sync --set-origin (git uri)'{red} to setup a git remote origin{reset}''')
        return False 
    if not git.set_origin(ctx, remote).check_ok():
        return _log_warning(ctx, f'''.
{red}However, git failed to add the remote uri "{remote}" 
Run mold help and read the about using "mold --set-remote" to add a remote.{reset}''')
    if not git.push(ctx).check_ok():
        _log_warning(ctx, f'''.
{red}However, git failed to push to the remote uri {remote}
Your remote probbly allready has content in it. If you want to 
overwrite the remote run {cyan}mold sync --force-push{red}, or you can run
{cyan}mold --install{red} again and overwrite the current $MOLD_ROOT.{reset}''')
        return False
    return True

# INTERFACE
def install(ctx):
    # colors
    green = ctx.green
    reset = ctx.reset

    if not _handle_mold_root_exists(ctx):
        return ctx.OK
    print(f'{green}Installing{reset} a MOLD_ROOT in {ctx.MOLD_ROOT}')
    if not _create_mold_root(ctx):
        return _fail(ctx)
    if not git.init(ctx).check_ok():
        return _fail(ctx)
    if not _handle_mold_root_set_origin(ctx):
        return ctx.OK
    _log_success(ctx, f' with the remote repository {remote}')
    return ctx.OK
