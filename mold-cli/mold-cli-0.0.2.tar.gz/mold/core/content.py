'''
content defines the logic for the sub commands make load list edit drop.
It also defines the abilty for file and fold to export content.
'''

import os 
import re
import requests 
from mold.util import fs, system, query

# TODO: v0.2.0 have each task handler return an exit code from the ctx
# then refactor main to return the result of the task handler
# IDEA create two log functions for OK and FAIL , they can be used
# They should return OK or FAIL exit codes they can be used 
# to log a status and exit in one one :) 
def _usage(ctx, options='[options]'):
    if ctx.task:
        return print(f'''USAGE: mold {ctx.command} {ctx.task} {options} [--flags]
    run "mold {ctx.command} {ctx.task + ' '}help" for more info''')
    print(f'''USAGE: mold {ctx.command} [task] [options] [--flags]
    run "mold {ctx.command} help" for more info''')

def _link_conf(ctx, filename):
    if ctx.command != 'conf':
        return 
    if ctx.task == 'make' or ctx.task == 'load':
        if ctx.check_flag_set('--no-linking'):
            print(f'NOTICE: conf {filename} was NOT linked')
            return 
    src = ctx.MOLD_ROOT + '/conf/' + filename
    dest = ctx.HOME + '/' + filename
    fs.force_link(src, dest)
    print('LINKED conf:', filename)

def _make(ctx):
    if not ctx.check_has_options():
        return _usage(ctx, '(name)')
    filename = ctx.get_option(0)
    filepath = ctx.get_command_dir() + '/' + filename
    if fs.exists(filepath):
        return print(f'ERROR: {filepath} allready exits try "mold {ctx.command} edit" instead')
    if ctx.command == 'fold':
        fs.mkdir(filepath)
        system.cd(filepath)
    if not system.shell(ctx.EDITOR + ' ' + filepath).check_ok():
        return print(f'ERROR: {ctx.EDITOR} could not open {filepath}')
    if not fs.exists(filepath):
        return print(f'MAKE {ctx.command} ABORTED: {filename} not created')
    if ctx.command == 'exec':
        fs.chmod(filepath, 0o755)
    print(f'MADE {ctx.command}:', filename)
    if ctx.command == 'conf':
        _link_conf(ctx, filename)

def _load_file(ctx, filepath):
    filename = ctx.get_option(1) or fs.basename(filepath)
    destpath = ctx.get_command_dir() + '/' + filename 
    if fs.exists(filepath):
        # first load content
        if ctx.command == 'fold':
            if not fs.is_dir(filepath):
                return print(f'USAGE ERROR: {filepath} is not a directory, use mold file instead.')
            fs.copy_dir(filepath, destpath)
        else:
            if fs.is_dir(filepath):
                return print(f'USAGE ERROR: {filepath}" is a directory, mold {ctx.command} only supports files.')
            fs.copy(filepath, destpath)
        # then if its a conf link it 
        if ctx.command == 'exec':
            fs.chmod(destpath, 0o755)
        if ctx.command == 'conf':
            _link_conf(ctx, filename)
        print(f'LOADED {ctx.command}: {filename}')
        return 
    print(f'ERROR: could not find "{filepath}"')

def _load_URI(ctx, uri):
    if ctx.command == 'fold':
        print(f'USAGE ERROR: "mold fold" load does not support URI downloads')
        return ctx.FAIL
    filename = ctx.get_option(1) or fs.basename(uri)
    destpath = ctx.get_command_dir() + '/' + filename 
    r = requests.get(uri)
    if r.status_code != 200:
        print(f'ERROR: unable to fetch {ctx.command} {uri}')
        return ctx.FAIL
    if not fs.write_file(destpath, r.text.strip()):
        print(f'ERROR: trouble saving {filename}')
        return ctx.FAIL
    print(f'LOADED {ctx.command}: {filename}')
    if ctx.command == 'exec':
        fs.chmod(destpath, 0o755)
    if ctx.command == 'conf':
        _link_conf(ctx, filename)
    return ctx.OK

def _load(ctx):
    if not ctx.check_has_options():
        return _usage(ctx, '(filepath or URL) [new name]')
    resource = ctx.get_option(0)
    # CHECK IF ITS A URL AND IF SO DOWNLOAD IT
    if re.match('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', resource):
        return _load_URI(ctx, resource)
    return _load_file(ctx, resource)

def _list(ctx):
    print('\n'.join(ctx.get_command_dirlist()).strip() or f'No {ctx.command}s')

def _edit(ctx):
    if not ctx.check_has_options():
        return _usage(ctx, '(name)')
    if ctx.command == 'conf':
        if ctx.check_flag_set('--no-linking'):
            return print('ERROR: conf is allready link --no-linking can not be used with "mold conf edit".')
    filename = ctx.get_option(0)
    filepath = ctx.get_command_dir() + '/' + filename
    if fs.exists(filepath):
        if ctx.command == 'fold': # IF you dont cd when using TUI editors its edit a dir structure
            system.cd(filepath) 
        if not system.shell(ctx.EDITOR + ' ' + filepath).check_ok():
            return print(f'ERROR: unable to edit {filepath}')
        if ctx.command == 'conf':
            _link_conf(ctx, filename) # RELINK CONF ON SUCCES
        return 
    print(f'ERROR: no "{filename}" {ctx.command} file found')

def _drop(ctx):
    if not ctx.check_has_options():
        return _usage(ctx, '(name)')
    filename = ctx.get_option(0)
    filepath = ctx.get_command_dir() + '/' + filename
    if fs.exists(filepath):
        if ctx.command == 'fold':
            fs.rimraf(filepath)
        else:
            fs.rm(filepath)
        print(f'REMOVED {filename} FROM $MOLD_ROOT/{ctx.command}')
        return 
    print(f'ERROR: no "{filename}" {ctx.command} file found')

# EXPORT and LINK
def _take(ctx):
    if not ctx.check_has_options():
        return _usage(ctx, '(name) [new name]')
    if not (ctx.command == 'fold' or ctx.command == 'leaf'): 
        print(f'ERROR: {ctx.command} does not support the file task')
        return 
    filename = ctx.get_option(0)
    filepath = ctx.get_command_dir() + '/' + filename
    output  = ctx.get_option(1) or filename
    if fs.exists(filepath):
        if ctx.command == 'leaf': 
            fs.copy(filepath, './' + output) 
            return 
        if ctx.command == 'fold':
            fs.copydir(filepath, './' + output)
            return 
    print(f'ERROR: no "{filename}" {ctx.command} file found')


_task_handlers = {
    "make": _make,
    "load": _load,
    "list": _list,
    "edit": _edit,
    "drop": _drop,
    "take": _take,
    "usage": _usage,
}


_content_commands = set(['leaf', 'fold', 'exec', 'conf', 'plug'])

def handle_context(ctx):
    if not _content_commands.issuperset([ctx.command]):
        return ctx.NEXT_COMMAND
    try: 
        _task_handlers[ctx.task or 'usage'](ctx)
        return ctx.OK
    except: 
        print(f'USAGE ERROR: "mold {ctx.command}" has no task named "{ctx.task}"')
        return ctx.FAIL
