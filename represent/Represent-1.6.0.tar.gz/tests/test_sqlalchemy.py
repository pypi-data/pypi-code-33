from __future__ import absolute_import, division

from contextlib import contextmanager

import pytest
from sqlalchemy import Column, Integer, Text, create_engine, event, func, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import column_property, defer, sessionmaker

from represent.sqlalchemy import ModelReprMixin

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


@contextmanager
def ephemeral_transaction(connection):
    transaction = connection.begin()
    try:
        yield transaction
    finally:
        # Rollback all changes since connection.begin
        transaction.rollback()


def fix_sqlite(engine):
    """See http://docs.sqlalchemy.org/en/rel_1_0/dialects/sqlite.html#pysqlite-serializable"""

    @event.listens_for(engine, 'connect')
    def do_connect(dbapi_connection, connection_record):
        # disable pysqlite's emitting of the BEGIN statement entirely.
        # also stops it from emitting COMMIT before any DDL.
        dbapi_connection.isolation_level = None

    @event.listens_for(engine, 'begin')
    def do_begin(conn):
        # emit our own BEGIN
        conn.execute('BEGIN')


@pytest.fixture(scope='session')
def engine():
    engine = create_engine('sqlite://')
    fix_sqlite(engine)
    return engine


@pytest.yield_fixture(scope='session')
def connection(engine):

    with engine.connect() as conn:
        # Put outer connection in a transaction that will be rolled back
        # at the end.
        with ephemeral_transaction(conn):
            yield conn


@pytest.yield_fixture(scope='session')
def session(connection):
    conn = connection

    Session = sessionmaker()

    # bind the session to our connection within the outer transaction.
    session = Session(bind=conn)

    # Start the session in a SAVEPOINT, allowing it to be rolled back
    # independent of the outer connection's transaction.
    session.begin_nested()

    # Register an event to start a new SAVEPOINT when the session's transaction
    # ends.
    @event.listens_for(session, 'after_transaction_end')
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:
            # ensure that state is expired the way
            # session.commit() at the top level normally does
            session.expire_all()
            session.begin_nested()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope='session')
def base():
    return declarative_base()


@pytest.fixture(scope='session')
def model(connection, base):
    Base = base

    class Model(ModelReprMixin, Base):
        __tablename__ = 'model'

        id = Column(Integer, primary_key=True)
        a = Column(Integer)
        b = Column(Integer)

    Model.__table__.create(bind=connection)

    return Model


@pytest.fixture(scope='session')
def model_test_data(model, session):
    Model = model

    session.add_all([
        Model(a=1, b=2),
    ])

    session.commit()


@contextmanager
def assert_no_emit(engine):
    @event.listens_for(engine, 'before_cursor_execute', named=True)
    def before_cursor_execute(**kw):
        assert False, 'Statement emitted: {}'.format(kw['statement'])

    yield

    event.remove(engine, 'before_cursor_execute', before_cursor_execute)


def test_transient(model, model_test_data, engine):
    Model = model

    m = Model(a=2, b=3)
    assert inspect(m).transient

    with assert_no_emit(engine):
        assert repr(m) == 'Model(id=None, a=2, b=3)'


def test_transient_to_pending(session, model, model_test_data, engine):
    Model = model

    callback = Mock()
    event.listen(session, 'transient_to_pending', callback, once=True)

    m = Model(a=2, b=3)
    assert inspect(m).transient
    session.add(m)
    assert inspect(m).pending
    assert callback.called

    with assert_no_emit(engine):
        assert repr(m) == 'Model(id=None, a=2, b=3)'


def test_pending_to_persistent(session, model, model_test_data, engine):
    Model = model

    callback = Mock()
    event.listen(session, 'pending_to_persistent', callback, once=True)

    m = Model(a=2, b=3)
    session.add(m)
    assert inspect(m).pending
    session.flush()
    assert inspect(m).persistent
    assert callback.called

    with assert_no_emit(engine):
        assert repr(m) == 'Model(id={}, a=2, b=3)'.format(m.id)
        assert m.id is not None


def test_pending_to_transient(session, model, model_test_data, engine):
    Model = model

    callback = Mock()
    event.listen(session, 'pending_to_transient', callback, once=True)

    m = Model(a=2, b=3)
    session.add(m)
    assert inspect(m).pending
    session.rollback()
    assert inspect(m).transient
    assert callback.called

    with assert_no_emit(engine):
        assert repr(m) == 'Model(id=None, a=2, b=3)'


def test_loaded_as_persistent(session, model, model_test_data, engine):
    Model = model

    callback = Mock()
    event.listen(session, 'loaded_as_persistent', callback, once=True)

    m = (
        session.query(Model)
        .filter_by(a=1, b=2)
        .options(defer('a'))
        .one()
    )

    assert inspect(m).persistent
    assert callback.called

    with assert_no_emit(engine):
        assert repr(m) == 'Model(id=1, a=<not loaded>, b=2)'

    session.expire(m, ['b'])
    assert inspect(m).persistent

    with assert_no_emit(engine):
        assert repr(m) == 'Model(id=1, a=<not loaded>, b=<not loaded>)'


def test_persistent_to_transient(session, model, model_test_data, engine):
    Model = model

    callback = Mock()
    event.listen(session, 'persistent_to_transient', callback, once=True)

    m = Model(a=2, b=3)
    session.add(m)
    session.flush()
    assert inspect(m).persistent
    session.rollback()
    assert inspect(m).transient
    assert callback.called

    with assert_no_emit(engine):
        assert repr(m) == 'Model(id={}, a=2, b=3)'.format(m.id)


def test_persistent_to_deleted(session, model, model_test_data, engine):
    Model = model

    callback = Mock()
    event.listen(session, 'persistent_to_deleted', callback, once=True)

    m = (
        session.query(Model)
        .filter_by(a=1, b=2)
        .options(defer('a'))
        .one()
    )

    assert inspect(m).persistent
    session.delete(m)
    session.flush()
    assert inspect(m).deleted
    assert callback.called

    with assert_no_emit(engine):
        assert repr(m) == 'Model(id=1, a=<not loaded>, b=2)'

    session.rollback()


@pytest.mark.skip
def test_deleted_to_detached(session, model, model_test_data, engine):
    Model = model

    callback = Mock()
    event.listen(session, 'deleted_to_detached', callback, once=True)

    m = Model(a=4, b=5)
    session.add(m)
    session.commit()

    session.refresh(m)

    session.delete(m)
    session.flush()
    assert inspect(m).deleted
    session.commit()
    assert inspect(m).detached
    assert callback.called

    with assert_no_emit(engine):
        assert repr(m) == 'Model(id=1, a=<not loaded>, b=2)'

    session.rollback()


def test_persistent_to_detached(session, model, model_test_data, engine):
    Model = model

    callback = Mock()
    event.listen(session, 'persistent_to_detached', callback, once=True)

    m = (
        session.query(Model)
        .filter_by(a=1, b=2)
        .options(defer('a'))
        .one()
    )

    assert inspect(m).persistent
    session.expunge(m)
    assert inspect(m).detached
    assert callback.called

    with assert_no_emit(engine):
        assert repr(m) == 'Model(id={}, a=<not loaded>, b=2)'.format(m.id)


def test_detached_to_persistent(session, model, model_test_data, engine):
    Model = model

    callback = Mock()
    event.listen(session, 'detached_to_persistent', callback, once=True)

    m = (
        session.query(Model)
        .filter_by(a=1, b=2)
        .options(defer('a'))
        .one()
    )

    session.expunge(m)
    assert inspect(m).detached
    session.add(m)
    assert callback.called

    with assert_no_emit(engine):
        assert repr(m) == 'Model(id={}, a=<not loaded>, b=2)'.format(m.id)


def test_deleted_to_persistent(session, model, model_test_data, engine):
    Model = model

    callback = Mock()
    event.listen(session, 'deleted_to_persistent', callback, once=True)

    m = (
        session.query(Model)
        .filter_by(a=1, b=2)
        .options(defer('a'))
        .one()
    )

    session.delete(m)
    session.flush()
    assert inspect(m).deleted
    session.rollback()
    assert inspect(m).persistent
    assert callback.called

    with assert_no_emit(engine):
        assert repr(m) == 'Model(id=<not loaded>, a=<not loaded>, b=<not loaded>)'

    session.rollback()


def test_repr(connection, base, session):
    Base = base

    class Message(ModelReprMixin, Base):
        __tablename__ = 'message'

        id_ = Column('id', Integer, primary_key=True)
        message = Column(Text)
        preview = column_property(func.substr(message, 0, 10))

    Message.__table__.create(bind=connection)
    message = Message(message='abcdefghijklmnopqrstuvwxyz')
    session.add(message)
    session.commit()
    message = session.query(Message).one()
    # assert repr(message) == ''

