import coeus_test.commands as commands

default_parameters = {}


def assert_entity_is_registered(cli, entity_id):
    """
    Asserts that the entity is registered.
    :param cli:
    :param entity_id:
    :return:
    """
    result = commands.query_entity_is_registered(cli, entity_id)
    assert result is True
    return result


def assert_entity_is_not_registered(cli, entity_id):
    """
    Asserts that the entity is registered.
    :param cli:
    :param entity_id:
    :return:
    """
    result = commands.query_entity_is_registered(cli, entity_id)
    assert result is False
    return result


def assert_await_entity_registered(cli, entity_id, is_registered=True, timeout_seconds=60):
    """
    Asserts that we successfully awaited for the registration state of the entity. If the timeout passes
    or the expression is_registered != actual state, then it will fail.
    :param cli:
    :param entity_id:
    :param is_registered: (True | False) the state change we are waiting for.
    :param timeout_seconds: The amount of time to wait for a change before fail.
    :return:
    """
    result = commands.await_entity_registered(cli, entity_id, is_registered, timeout_seconds)
    assert result is True
    return result
