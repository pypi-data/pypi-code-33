# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import sys
import traceback


class AzureMLException(Exception):
    """
    A base_sdk_common class for all azureml exceptions.
    AzureMLException extends Exception, so if users want to catch only azureml exceptions
    then they can catch AzureMLException.
    """

    def __init__(self, exception_message, inner_exception=None, **kwargs):
        Exception.__init__(self, exception_message, **kwargs)
        self._exception_message = exception_message
        self._inner_exception = inner_exception
        self._exc_info = sys.exc_info()

    @property
    def message(self):

        return self._exception_message

    @property
    def inner_exception(self):

        return self._inner_exception

    def print_stacktrace(self):
        traceback.print_exception(*self._exc_info)


class TrainingException(AzureMLException):
    def __init__(self, exception_message, **kwargs):
        super(TrainingException, self).__init__(exception_message, **kwargs)


class ExperimentExecutionException(AzureMLException):
    def __init__(self, exception_message, **kwargs):
        super(ExperimentExecutionException, self).__init__(exception_message, **kwargs)


class ProjectSystemException(AzureMLException):
    def __init__(self, exception_message, **kwargs):
        super(ProjectSystemException, self).__init__(exception_message, **kwargs)


class SnapshotException(AzureMLException):
    def __init__(self, exception_message, **kwargs):
        super(SnapshotException, self).__init__(exception_message, **kwargs)


class RunEnvironmentException(AzureMLException):
    def __init__(self, **kwargs):
        super(RunEnvironmentException, self).__init__(
            ("Failed to load a submitted run, if outside "
             "of an execution context, use experiment.start_logging to "
             "initialize an azureml.core.Run."), **kwargs)


class WorkspaceException(AzureMLException):
    def __init__(self, exception_message, found_multiple=False, **kwargs):
        super(WorkspaceException, self).__init__(exception_message, **kwargs)
        self.found_multiple = found_multiple


class ComputeTargetException(AzureMLException):
    def __init__(self, exception_message, **kwargs):
        super(ComputeTargetException, self).__init__(exception_message, **kwargs)


class AuthenticationException(AzureMLException):
    def __init__(self, exception_message, **kwargs):
        super(AuthenticationException, self).__init__(exception_message, **kwargs)


class UserErrorException(AzureMLException):
    def __init__(self, exception_message, **kwargs):
        super(UserErrorException, self).__init__(exception_message, **kwargs)


class RunConfigurationException(AzureMLException):
    def __init__(self, exception_message, **kwargs):
        super(RunConfigurationException, self).__init__(exception_message, **kwargs)


class WebserviceException(AzureMLException):
    def __init__(self, exception_message, status_code=None, **kwargs):
        super(WebserviceException, self).__init__(exception_message, **kwargs)
        self.status_code = status_code


class ModelNotFoundException(AzureMLException):
    def __init__(self, exception_message, **kwargs):
        super(ModelNotFoundException, self).__init__(exception_message, **kwargs)


class DiscoveryUrlNotFoundException(AzureMLException):
    def __init__(self, discovery_key, **kwargs):
        super(DiscoveryUrlNotFoundException, self).__init__(
            ("Failed to load discovery key {}, from environment variables.".format(discovery_key)), **kwargs)


class ActivityFailedException(AzureMLException):
    def __init__(self, error_details, **kwargs):
        super(ActivityFailedException, self).__init__(
            ("Activity Failed:\n{}".format(error_details)), **kwargs)
