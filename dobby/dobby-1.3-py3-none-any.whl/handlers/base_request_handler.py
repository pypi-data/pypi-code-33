from dobby.results.failed_result import FailedResult
from dobby.results.internal_error_result import InternalErrorResult

from .validation_error import ValidationError


class BaseRequestHandler:
    """A base class for all request handlers. 
    Provides a templated execution of the request handling.
    The request handling is carried out in the `handle` template method. 
    To create your own handler you only need to implement your own `validate` 
    and `execute` methods. 

    Usage: 
        >>> class SomeHandler(BaseRequestHandler):
        ...     def _execute(self, request):
        ...         result = <SomeResult>("hi")
        ...         return result
        ...
        >>> def handle():
        ...     handler = SomeHandler(SomeRequestAdapter(), SomeResultBuilder())
        ...     return handler.handle()
    """

    def __init__(self, request_adapter, response_builder):
        self._request_adapter = request_adapter
        self._response_builder = response_builder

    def handle(self, event, context):
        """A template function for handling the event.
        Encapsulates the validation and execution of business logic associated 
        with the request. 

        See https://docs.aws.amazon.com/lambda/latest/dg/python-programming-model-handler-types.html

        Arguments:
            event {Event} -- contains the event data
            context {Context} -- runtime information for the event

        Returns:
            BaseResponse -- the response from handler's response builder
        """
        try:
            return self._try_handle(event, context)

        except Exception as e:
            # TODO: provide the means for this handling to be custom?
            result = InternalErrorResult(e)
            return self._response_builder.create_response(result)

    def _try_handle(self, event, context):
        """
        Attempts to handle the event
        
        Arguments:
            event {Event} -- contains the event data
            context {Context} -- runtime information for the event

        Returns:
            BaseResponse -- the response from handler's response builder
        """

        try:
            request = self._request_adapter.translate(event, context)
            self._validate(request)
            result = self._execute(request)
            return self._response_builder.create_response(result)

        except ValidationError as e:
            # TODO: provide the means for this handling to be custom?
            result = FailedResult(e.message)
            return self._response_builder.create_response(result)

    def _validate(self, request):
        """Validate the request. 
        To report a validation result, use `self._report_validation_error`.

        Arguments:
            request {BaseRequest} -- the request to be validated

        Returns:
            bool -- indication whether validaiton was successful
        """

        return True

    def _execute(self, request):
        """The execution method that is the entrypoint to the business logic. """

        raise NotImplementedError

    def _report_validation_error(self, message, errors=[]):
        """Report the validation failure

        Arguments:
            message {[type]} -- [description]

        Keyword Arguments:
            errors {list} -- [description] (default: {[]})

        Raises:
            ValidationError -- [description]
        """

        raise ValidationError(message, errors=errors)
