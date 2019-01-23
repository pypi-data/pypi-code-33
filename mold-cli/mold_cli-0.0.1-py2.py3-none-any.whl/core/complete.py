'''
complete defines the routing routing logic for arguments to  mold --complete. 
'''

from mold.util import git 

# PRIVATE 
_completable_commands = ['conf', 'plug', 'exec', 'temp', 'leaf', 'sync']
_completable_content_default_tasks = ['help', 'make', 'load', 'list', 'edit', 'drop']
_completable_root_commands = ['--set-origin', '--fix', '--check']
# sync "--" tasks do not show up in tab completion because they are dangerous
_completable_sync_tasks = ['auto', 'log', 'link', 'add', 'commit', 'push', 'pull', 'diff', 'status', 'branch', 'fetch']

def _complete_no_suggestions(ctx):
    print('')
    return ctx.OK

def _complete_magic_mold(ctx):
    print('__MAGIC_MOLD__')
    return ctx.OK

def _complete_command_dirlist(ctx):
    print(' '.join(ctx.get_command_dirlist()))
    return ctx.OK

def _complete_branch_names(ctx):
    result = git._git_exec(ctx, 'branch')
    if not result.check_ok():
        return ctx.OK
    print(result.out.replace('*', ''))
    return ctx.OK

def _create_handler_from_word_list(words):
    def _complete_words(ctx):
        print(' '.join(words))
        return ctx.OK
    return _complete_words

_completion_handlers = {
    # main 
    "main": _create_handler_from_word_list(['fold', 'leaf', 'conf', 'plug', 'exec', 'sync', 'help', 'root']),
    # commands
    "help": _complete_no_suggestions,
    "root": _create_handler_from_word_list(_completable_root_commands),
    "conf": _create_handler_from_word_list(_completable_content_default_tasks),
    "exec": _create_handler_from_word_list(_completable_content_default_tasks),
    "plug": _create_handler_from_word_list(_completable_content_default_tasks),
    "fold": _create_handler_from_word_list(_completable_content_default_tasks + ['take']),
    "leaf": _create_handler_from_word_list(_completable_content_default_tasks + ['take']),
    "sync": _create_handler_from_word_list(_completable_sync_tasks),
    "--install": _complete_no_suggestions,
    "--set-remote": _complete_no_suggestions,
    # root tasks
    "--fix": _complete_no_suggestions,
    "--check": _complete_no_suggestions,
    "--set-origin": _complete_no_suggestions,
    # content tasks
    "load": _complete_magic_mold,
    "make": _complete_no_suggestions,
    "list": _complete_no_suggestions,
    "edit": _complete_command_dirlist,
    "drop": _complete_command_dirlist, 
    "take": _complete_command_dirlist, 
    # sync tasks
    "link": _complete_no_suggestions,
    "auto": _complete_no_suggestions,
    "log": _complete_no_suggestions,
    "add": _complete_no_suggestions,
    "commit": _complete_no_suggestions,
    "push": _complete_no_suggestions,
    "pull": _complete_no_suggestions,
    "diff": _complete_no_suggestions,
    "status": _complete_no_suggestions,
    "branch": _complete_no_suggestions,
    "--merge": _complete_no_suggestions,
    "--checkout": _complete_branch_names,
    "--new-branch": _complete_no_suggestions,
    "--force-push": _complete_no_suggestions,
    "--soft-reset": _complete_no_suggestions,
    "--hard-reset": _complete_no_suggestions,
}

# INTERFACE

# complete gets passed $COMPLINE and needs to reparse argv[2] and 
def handle_context(ctx):
    if not ctx.check_flag_set('--complete'):
        return ctx.NEXT_COMMAND

    # if MOLD_ROOT is not setup no completion 4 you
    # if no command show main until command 
    if ctx.check_help_set():
        return _completion_handlers['help'](ctx)
    if ctx.command == None or ctx.command == 'mold': 
        return _completion_handlers['main'](ctx)
    try:
        if ctx.task == None:
            return _completion_handlers[ctx.command](ctx)   
    except:
        return _completion_handlers['main'](ctx)

    # if no task show command until task 
    try:
        return _completion_handlers[ctx.task](ctx)
    except:
        return _completion_handlers[ctx.command](ctx)

