import contextlib
import logging
import sys
import time

from lettuce import step

from selenium.common.exceptions import WebDriverException


from fattoush.driver.driver import Driver
from fattoush.util import filename_in_created_dir
from fattoush.namespace import per

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
HANDLER = logging.StreamHandler()
HANDLER.setLevel(logging.INFO)
LOGGER.addHandler(HANDLER)


class Decorated(object):
    def __init__(self, fn, decorators):
        self.fn = fn
        self.func_code = fn.func_code
        self.decorators = decorators

    def __call__(self, *args, **kwargs):
        head, tail = self.decorators[0], self.decorators[1:]
        fn, args, kwargs = head(self.fn, *args, **kwargs)

        if tail:
            return self.__class__(fn, tail)(*args, **kwargs)

        return fn(*args, **kwargs)


class Step(object):
    def __init__(self, *decorated):
        self._decorated = decorated

    def decorator(self, fn, step_regex):
        decorated = Decorated(fn, self._decorated)

        return step(step_regex)(decorated)

    def __call__(self, step_regex):

        def decorator(fn):
            return self.decorator(fn, step_regex)

        return decorator

    def then(self, decorated):
        chain = self._decorated + (decorated, )

        return self.__class__(*chain)


@contextlib.contextmanager
def _screenshot_after(step):
    """
    Ensure that a screenshot is taken after the decorated step definition
    is run.
    """
    file_path = filename_in_created_dir(dir_name='logs', step=step, ext='png')

    try:
        yield
    except:
        exc_type, exc_value, exc_tb = sys.exc_info()

        time.sleep(1)

        browser = per.scenario.get('browser')

        if browser is not None:
            try:
                taken = browser.get_screenshot_as_file(file_path)
            except WebDriverException:
                taken = False

            if taken:
                LOGGER.info(
                    "captured screen shot to {}".format(file_path)
                )
            else:
                LOGGER.exception(
                    "could not capture screen shot to {}".format(file_path)
                )

        raise exc_type, exc_value, exc_tb
    else:
        browser = per.scenario.get('browser')
        if browser is None:
            return

        try:
            if browser.is_sauce:
                browser.get_screenshot_as_png()
            else:
                browser.get_screenshot_as_file(file_path)
        except WebDriverException:
            pass


@Step
def without_step(definition, _, *args, **kwargs):
    return definition, args, kwargs


@Step
def just_hashes(definition, step_obj, *args, **kwargs):
    return definition, (step_obj.hashes,) + args, kwargs


@Step
def screenshot(definition, step_obj, *args, **kwargs):
    with _screenshot_after(step_obj):
        return definition, (step_obj,) + args, kwargs


@screenshot.then
def with_wd(definition, step_obj, *args, **kwargs):
    wd = Driver.instance(step_obj)

    return definition, (step_obj, wd) + args, kwargs


@with_wd.then
def just_wd(definition, _, *args, **kwargs):
    return definition, args, kwargs
