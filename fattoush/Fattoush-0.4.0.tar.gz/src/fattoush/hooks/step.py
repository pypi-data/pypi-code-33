"""
Hooks that run before and after steps
"""
import functools

from lettuce import after

from fattoush.namespace import per


def if_browser(fn):
    @functools.wraps(fn)
    def _inner(step, *args, **kwargs):
        browser = per.scenario.get('browser')

        if browser is not None:
            fn(step, *args, **kwargs)

    return _inner


def if_scenario(fn):
    @functools.wraps(fn)
    def _inner(step):
        if getattr(step, 'scenario', None) is not None:
            fn(step)

    return _inner


@after.each_step
@if_browser
def hook_mark_failures(step):
    if step.failed:
        per.scenario['browser'].sauce.fail_session()
