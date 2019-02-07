class ProcessorInitNoneOrWrongTypeVariant(Exception):
    """Variant is not found in provided VariantSchemaMaster
    dependencies"""


class ProcessorInitWrongTypeCustomSchema(Exception):
    """Provided Custom Schema is of wrong type"""


class ProcessorExtractCantSetDestinationAttr(Exception):
    """Invalid destination"""


class NoSpanException(Exception):
    """Attempt to process span without span itself, skipping"""


class SpanIsNotStartedException(Exception):
    """Attempt to fill in or finish span that has not been started"""


class SpanNoParentException(Exception):
    """Outgoing point without parent span,
        it's no error just a normal case flow
    """


class SpanNoStageForMethod(Exception):
    """Method decorated as stage-bound has no stage linked
    """


class HTTPPathSkip(Exception):
    """Skip HTTP path, it's no error just an option"""


class TornadoNotAvailable(Exception):
    """use_tornado_loop does not work without Tornado dependency installed"""
