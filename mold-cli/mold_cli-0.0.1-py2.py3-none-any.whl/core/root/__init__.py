from mold.util import fs, git 
# from mold.color import get_color
from mold.core.root.install import install

def check(ctx):
    red = ctx.red
    yellow = ctx.yellow
    reset = ctx.reset
    if ctx.check_flag_set('--complete'):
        return ctx.OK
    if (not ctx.MOLD_ROOT) or (not fs.exists(ctx.MOLD_ROOT)) or (not fs.is_dir(ctx.MOLD_ROOT)):
        print(f'''{red}ERROR:{reset} Looks like your MOLD_ROOT directory hasent been set up yet.
    {yellow}Try runing "mold root --install"{reset}''')
        return ctx.MOLD_ROOT_ERROR
    for d in ['conf', 'plug', 'fold', 'leaf', 'exec']:
        if not fs.exists(ctx.MOLD_ROOT + '/' + d):
            print(f'''{red}ERROR:{reset} Somthing is wrong with your MOLD_ROOT directory.
    {yellow}Try runing "mold root --fix"{reset}''')
            return ctx.MOLD_ROOT_DIRS_ERROR
    return ctx.NEXT_COMMAND

def _usage(ctx):
    print(f'''USAGE: mold root [task] [options]  [--flags]
    run "mold root help" for more info''')
    return ctx.OK

def _check(ctx):
    result = check(ctx)
    if result == ctx.OK:
        print(f'MOLD_ROOT {ctx.MOLD_ROOT} is OK')
    return result

def _fix(ctx):
    print("Fixing mold root")
    if not fs.exists(ctx.MOLD_ROOT):
        print('''ERROR: There is no MOLD_ROOT to fix.
    Try runing "mold root --install"''')
        return ctx.MOLD_ROOT_ERROR
    try:
        for content_type in ['conf', 'plug', 'exec', 'fold', 'leaf']:
            content_dir = ctx.MOLD_ROOT + '/' + content_type
            if not fs.exists(content_dir):
                fs.mkdir(content_dir)
                fs.write_file(content_dir + '/.mold', 'KEEP ME')
        result = _check(ctx)
        if result != ctx.OK:
            print('''Sorry, Something went wrong.
    You may want to open an issue at https://github.com/slugbyte/mold/issues''')
        return ctx.NEXT_COMMAND
    except:
        return ctx.FAIL

def _clone(ctx):
    red = ctx.red
    cyan = ctx.cyan
    reset = ctx.reset
    remote = ctx.get_option(0)
    if not remote:
        print(f'''USAGE: mold root --clone (git-uri) [--force]
    run 'mold root --clone help' for more info''')
        return ctx.FAIL
    if fs.exists(ctx.MOLD_ROOT):
        if not ctx.check_flag_set('--force'):
            print(f'{red}WARNING:{reset} {ctx.MOLD_ROOT} allready exists do you want to remove it?')
            abort = 'y' != input(f'{cyan}Do you want to contiune the installation? y/n:{reset} ').strip()
            if (abort):
                print('Ok, mold --clone aborted.')
                return ctx.OK 
        fs.rimraf(ctx.MOLD_ROOT) 
    git.clone(ctx, remote)
    result = check(ctx)
    if result != ctx.NEXT_COMMAND:
        return ctx.FAIL
    ctx.link_conf()
    return ctx.OK


_task_handlers = {
    "--install": install,
    "--clone": _clone,
    "--check": _check,
    "--fix": _fix,
    "usage": _usage,
}

def handle_context(ctx):
    if ctx.command != 'root':
        return check(ctx)
    try:
        return _task_handlers[ctx.task or 'usage'](ctx)
    except:
        print(f'ERROR: mold root has not "{ctx.task}"')
        return ctx.FAIL
