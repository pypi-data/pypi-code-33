'''
sync defines the logic for maintaining a MOLD_ROOT using git 
'''

from mold.util import git, query, system
# TODO v0.2.0 adde --unset-origin and --unset-upstream

def _usage(ctx, options=''):
    if ctx.task:
        print(f'''USAGE: mold {ctx.command} {ctx.task} {options}
    run "mold {ctx.command} {ctx.task} help" for more info''')
        return system.fail()
    else:
        print(f'''USAGE: mold {ctx.command} [task] [...options] [--flags]
    run "mold {ctx.command} help" for more info''')
        return system.fail()

def _link(ctx):
    ctx.link_conf()
    return ctx.OK 

def _auto(ctx):
    message = ctx.get_option(0)
    result = git.pull(ctx)
    if not result.check_ok():
        print('ERROR: unable to git pull')
        return result 
    ctx.link_conf()
    result = git.add(ctx)
    if not result.check_ok():
        print('ERROR: unable to git add -A')
        return result
    result = git.commit(ctx, message)
    if not result.check_ok():
        return result
    result = git.push(ctx)
    if not result.check_ok():
        print('ERROR: unable to git push')
    return result 

def _make_no_arg_git_task(name):
    methods = {
        "add": git.add,
        "log": git.log,
        "branch": git.branch,
        "status": git.status,
        "remote": git.remote,
        "fetch": git.fetch,
    }
    def handler(ctx):
        return methods[name](ctx)
    return handler

def _make_one_arg_git_task(name):
    methods = {
        "pull": git.pull,
        "diff": git.diff,
        "push": git.push,
        "commit": git.commit,
    }
    def handler(ctx):
        arg = ctx.get_option(0)
        return methods[name](ctx, arg)
    return handler

def _make_one_arg_git_task_with_usage_warning(name, option_text=None):
    methods = {
        "merge": git.merge,
        "checkout": git.checkout,
        "new_branch": git.new_branch,
        "hard_reset": git.hard_reset,
        "soft_reset": git.soft_reset,
        "force_push": git.force_push,
        "set_origin": git.set_origin,
        "set_upstream": git.set_upstream,
    }
    def handler(ctx):
        if not ctx.check_has_options():
            return _usage(ctx, option_text)
        arg = ctx.get_option(0)
        return methods[name](ctx, arg)
    return handler

def _link_conf_after_git(handler):
    def _handler(*args):
        result = handler(*args)
        if not result.check_ok():
            return result
        args[0].link_conf()
        return result
    return _handler

_task_handlers = {
    # custom 
    "auto": _auto, # internaly handles linking conf
    "link": _link,
    "usage": _usage,
    # curry no arg
    "add": _make_no_arg_git_task('add'),
    "log": _make_no_arg_git_task('log'),
    "status": _make_no_arg_git_task('status'),
    "branch": _make_no_arg_git_task('branch'),
    "remote": _make_no_arg_git_task('remote'),
    "fetch": _make_no_arg_git_task('fetch'),
    # curry one arg with usage warning
    "diff": _make_one_arg_git_task('diff'),
    "push": _make_one_arg_git_task('push'),
    "commit": _make_one_arg_git_task('commit'),
    "pull": _link_conf_after_git(_make_one_arg_git_task('pull')),
    # curry one arg dangerous tasks with usage warning
    "--set-origin": _make_one_arg_git_task_with_usage_warning('set_origin', '(git uri)'),
    "--set-upstream": _make_one_arg_git_task_with_usage_warning('set_upstream', '(git uri)'),
    "--new-branch": _make_one_arg_git_task_with_usage_warning('new_branch', '(branch)'),
    "--force-push": _make_one_arg_git_task_with_usage_warning('force_push', '(branch)'),
    "--merge": _link_conf_after_git(_make_one_arg_git_task_with_usage_warning('merge', '(branch) [--flags]')),
    "--checkout": _link_conf_after_git(_make_one_arg_git_task_with_usage_warning('checkout', '(branch) [--flags]')),
    "--soft-reset": _link_conf_after_git(_make_one_arg_git_task_with_usage_warning('soft_reset', '(commit hash or branch) [--flags]')),
    "--hard-reset": _link_conf_after_git(_make_one_arg_git_task_with_usage_warning('hard_reset', '(commit hash or branch) [--flags]')),
} 

def handle_context(ctx):
    if ctx.command != 'sync':
        return ctx.NEXT_COMMAND
    try:
        _task_handlers[ctx.task or 'usage'](ctx)
        return ctx.OK
    except:
        print(f'ERROR: mold sync can\'t {ctx.task} yet.')
        return ctx.FAIL

