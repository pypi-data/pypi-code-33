import contextlib
import functools
import logging
import sys
import time

from selenium.common.exceptions import WebDriverException

from fattoush import world
from fattoush.util import filename_in_created_dir

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
HANDLER = logging.StreamHandler()
HANDLER.setLevel(logging.INFO)
LOGGER.addHandler(HANDLER)


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

        browser = world.per_scenario.get('browser')

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
        browser = world.per_scenario.get('browser')
        if browser is None:
            return

        try:
            if browser.is_sauce:
                browser.get_screenshot_as_png()
            else:
                browser.get_screenshot_as_file(file_path)
        except WebDriverException:
            pass


def screenshot(fn):
    @functools.wraps(fn)
    def _inner(step, *args, **kwargs):
        with _screenshot_after(step):
            return fn(step, *args, **kwargs)
    return _inner
