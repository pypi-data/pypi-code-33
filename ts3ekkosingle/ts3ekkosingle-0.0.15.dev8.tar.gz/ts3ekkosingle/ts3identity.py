from sqlalchemy import Column, Integer, create_engine, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import hashlib
import logging

Base = declarative_base()


class ProtobufItems(Base):
    __tablename__ = 'ProtobufItems'
    timestamp = Column(Integer, nullable=False)
    key = Column(VARCHAR, nullable=False, unique=True, primary_key=True)
    value = Column(VARCHAR)


def startup(path_to_settings_db):
    engine = create_engine(f'sqlite:///{path_to_settings_db}')

    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)

    session = DBSession()
    return session


def replace_identity(sess, key, old_identity, new_identity):
    """
    Replaces the private identity in the record identified by the key.
    :param sess: sqalchemy session
    :param key: identifier of the record to be edited
    :param old_identity: string which should be replaced
    :param new_identity: replacement string
    """
    if type(old_identity) == str:
        logging.debug('encoded old identity to bytes')
        old_identity = old_identity.encode('latin1')

    if type(new_identity) == str:
        logging.debug('encoded new identity to bytes')
        new_identity = new_identity.encode('latin1')

    identity_query = sess.query(ProtobufItems).filter_by(key=key)
    identity_record = identity_query.one()
    identity_query.update({'value': identity_record.value.replace(old_identity, new_identity)})
    sess.commit()
    checksum_update(sess)
    logging.debug('identity thing should be done')


def checksum_update(sess):
    """
    Recalculates the Checksum record in the ProtobufItems table in the given sqlalchemy session
    :param sess: sqlalchemy session
    """
    identity_query = sess.query(ProtobufItems).filter(ProtobufItems.key != 'Checksum')
    joined_pool = b''.join([iden.value for iden in identity_query])
    new_checksum = hashlib.sha1(joined_pool).digest()

    checksum_query = sess.query(ProtobufItems).filter_by(key='Checksum')
    logging.debug(sess.query(ProtobufItems).filter_by(key='Checksum').one().value)
    checksum_query.update({'value': new_checksum})
    logging.debug(sess.query(ProtobufItems).filter_by(key='Checksum').one().value)
    sess.commit()

    logging.debug(sess.query(ProtobufItems).filter_by(key='Checksum').one().value)


if __name__ == '__main__':
    old_identity = '15456318Vrjp+cffeguX6meh5OMc6vEcNT51xCFp1awUMZVFiWnYiWXl4A1dGCFYACyZeJn9SL1NLWl9hAz8iUn0GcFNEeUEIaXdwLVUIOS8JPQ8WVz9GBlthIm1BOAIvR1N0F2B0DV9Sdk1sa0NJUURUTGhjbnZHQnU4QWUzbXBEQkhRMVBKeDUrc2RuYXFmYXFQOUVwM0lQbXdnPT0='
    new_identity = '34951128VxRulcsSPzgOgHnjUisP10QWbuoJ7LkRkclsocCFLYngnfkNZdUhHE1FWKA5RKkx6GQF3Vnhif1NWcQwie39EcAhGAWFnLn1eVwhDCQwAJBZjH296NFdAI0IJWXx6BFlgIXEEV2x3ZW9BaUVBNEcwa0VVSGltQndWdEtkZTd2SVY4bm01N2pBcXB6Yzh3YmdYcGw5V0w1bz0='
    #new_identity = '68103251VWij5a8B5ezKXh+lQreyptqbPg8xfCFB+X3c7BhYaXVI1WV5AW1kFBiFDARZ2UGNlDVN6eUpYalY0Qn0GVnF+SlhGCEpnA3V2Dw94V1APIj0FXFBUJ3p/CVNXUE5CL1VJDghXQk5Ra0NJUUNKVVJoYis1cmd1YUpKUjZvNG51QUhyZjlZMUN5S0VIMXJPQXRXeVdBNjhnPT0='
    sess = startup('/home/xyoz/.ts3client/settings.db')
    replace_identity(sess, 4, old_identity, new_identity)
