from shuttlis.log import configure_logging

_LOG = configure_logging("pyshuttlis", "DEBUG")


def test_prints_without_erros():
    _LOG.debug("hey.there", extra={"one": "one"})


def test_prints_out_exc():
    try:
        raise ValueError
    except ValueError:
        _LOG.error("an.error", exc_info=True)
