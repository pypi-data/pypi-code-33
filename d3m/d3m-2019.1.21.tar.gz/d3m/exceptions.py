class NotSupportedError(RuntimeError):
    """
    Functionality is not supported.
    """


class NotSupportedVersionError(RuntimeError):
    """
    This version is not supported.
    """


class InvalidArgumentValueError(ValueError):
    """
    Provided argument to the function is invalid in value.
    """


class InvalidReturnValueError(ValueError):
    """
    Returned value from the function is invalid.
    """


class InvalidArgumentTypeError(TypeError):
    """
    Provided argument to the function is invalid in type.
    """


class InvalidReturnTypeError(TypeError):
    """
    Type of the returned value from the function is invalid.
    """


class NotFoundError(ValueError):
    """
    Something requested could not be found.
    """


class AlreadyExistsError(ValueError):
    """
    Something which should not exist already exists.
    """


class MismatchError(ValueError):
    """
    A value does not match expected value.
    """


class MissingValueError(ValueError):
    """
    The required value has not been provided.
    """


class DigestMismatchError(MismatchError):
    """
    A digest does not match the expect digest.
    """


class DimensionalityMismatchError(MismatchError):
    """
    Dimensionality mismatch occurs in array computations.
    """


class UnexpectedValueError(ValueError):
    """
    Value occurred not in a fixed list of possible or supported values,
    e.g., during parsing of data with expected schema.
    """


class DatasetUriNotSupportedError(NotSupportedError):
    """
    Provided dataset URI is not supported.
    """


class DatasetNotFoundError(FileNotFoundError, NotFoundError):
    """
    Provided dataset URI cannot be resolved to a dataset.
    """


class InvalidStateError(AssertionError):
    """
    Program ended up in an invalid or unexpected state, or a state does not match the current code path.
    """


class InvalidMetadataError(ValueError):
    """
    Metadata is invalid.
    """


class InvalidPrimitiveCodeError(ValueError):
    """
    Primitive does not match standard API.
    """


class ColumnNameError(KeyError):
    """
    Table column with name not found.
    """


class InvalidPipelineError(ValueError):
    """
    Pipeline is invalid.
    """


class PrimitiveNotFittedError(InvalidStateError):
    """
    The primitive has not been fitted.
    """


class PermissionDeniedError(RuntimeError):
    """
    No permissions to do or access something.
    """


class StepFailedError(RuntimeError):
    """
    Running a pipeline step failed.
    """
