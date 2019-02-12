"""This module implements the Aug class."""
import time

from rook.logger import logger
from rook.user_warnings import UserWarnings
from rook.processor.error import Error
from rook.processor.namespaces.container_namespace import ContainerNamespace
from rook.processor.namespaces.stack_namespace import StackNamespace
from rook.processor.namespaces.python_utils_namespace import PythonUtilsNamespace
from rook.exceptions import RookRuleRateLimited


class Aug(object):
    """The Aug class is the skeleton that holds together all the components that define a modification to the application.

    This class brings together the following elements:
    - location - specifies when to run the modification.
    - extractor - specifies attributes to extract from the application's state before evaluating the modification.
    - condition - specifies an optional filter as to when to run the modification.
    - action - specifies the modification to preform.
    """

    def __init__(self, aug_id, location, extractor, condition, action, output, min_time_between_hits=0):
        """Build an Aug object from the individual elements."""
        self.aug_id = aug_id
        self._location = location
        self._extractor = extractor
        self._condition = condition
        self._action = action
        self._output = output
        self._last_executed = 0
        self._min_time_between_hits = min_time_between_hits
        self._enabled = True

        self._status = None

    def add_aug(self, trigger_services):
        """Use the location to add the Aug to the relevant trigger service."""
        try:
            self._location.add_aug(trigger_services, self._output, self)
        except Exception as exc:
            message = "Exception when adding aug"
            logger.exception(message)
            self.set_error(Error(exc=exc, message=message))

    def execute(self, frame_namespace, extracted):
        """Called by the trigger service to run the extractor, condition and action."""
        if not self._enabled:
            return

        try:
            with UserWarnings(self):
                logger.info("Executing aug-\t%s", self.aug_id)
                now = int(time.time() * 1000)

                if self._min_time_between_hits > 0 and now < self._last_executed + self._min_time_between_hits:
                    self.set_error(Error(exc=RookRuleRateLimited()))
                    self._enabled = False
                    return

                self._last_executed = now

                if self._extractor:
                    self._extractor.execute(frame_namespace, extracted)

                store = ContainerNamespace({})

                namespace = ContainerNamespace({
                    'frame': frame_namespace,
                    'stack': StackNamespace(frame_namespace),
                    'extracted': ContainerNamespace(extracted),
                    'store': store,
                    'temp': ContainerNamespace({}),
                    'python': PythonUtilsNamespace(),
                    'utils': PythonUtilsNamespace()
                })

                if not self._condition or self._condition.evaluate(namespace, extracted):
                    self._action.execute(self.aug_id, namespace, self._output)

        # Don't stop test exceptions from propagating
        except AssertionError:
            raise
        # Catch and silence everything else
        except Exception as exc:
            message = "Exception while processing Aug"
            logger.exception(message)
            self.send_warning(Error(exc=exc, message=message))
        finally:
            self._last_executed = now

    def set_active(self):
        self._send_rule_status("Active")

    def set_pending(self):
        self._send_rule_status("Pending")

    def set_removed(self):
        self._send_rule_status("Deleted")

    def set_error(self, error):
        self._send_rule_status("Error", error)

    def set_unknown(self, error):
        self._send_rule_status("Unknown", error)

    def send_warning(self, error):
        self._output.send_warning(self.aug_id, error)

    def _send_rule_status(self, status, error=None):
        if self._status == status:
            return

        logger.info("Updating rule status for %s to %s", self.aug_id, status)

        self._status = status
        self._output.send_rule_status(self.aug_id, status, error)
