from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData, Column, ForeignKey
from sqlalchemy.types import  String, Text, TIMESTAMP, PickleType, Integer, Boolean,DateTime
from sqlalchemy.orm import  relationship, sessionmaker, scoped_session
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature
import rsa

from Reger.config import default

engine = create_engine(default['uri'])
Base = declarative_base(engine)
Session = scoped_session(sessionmaker(engine))

def get_session():
    return Session()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    user_name = Column(String(64))
    pw_hash = Column(String(256))
    role = Column(Integer, default=2) # 二进制位图
    email = Column(String(64))
    phone = Column(String(32))
    servers = relationship('Servers', backref='user')

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.pw_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def generate_auth_token(self, expiration=3 * 24 * 60 * 60):
        s = Serializer(default['secret_key'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def query_user_by_token(token):
        s = Serializer(default['secret_key'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = Session().query(User).filter_by(id=data['id']).first()
        return user

    @staticmethod
    def verify_auth_token(token, user_name):
        user = User.query_user_by_token(token)
        if not user:
            return False
        return user.user_name == user_name

class Roles(Base):
    __tablename__ = 'roles'

    name = Column(String(32))
    code = Column(Integer, primary_key=True, autoincrement=False) # 二进制位表示
    description = Column(String(64))
    info = Column(Text) # json 控制面板选项

class Servers(Base):
    __tablename__ = 'server_test'

    hash = Column(String(32), primary_key=True)
    serve_key = Column(String(32))
    name = Column(String(64), unique=True)
    auth = Column(ForeignKey(User.id))
    domain = Column(String(128))
    host = Column(String(16))
    port = Column(Integer)
    status = Column(Integer)
    # 0 - 未确认 1 - 运行中 2 - 运行异常
    subscription = relationship('API', secondary='Subscription')
    tables = relationship('Tables', backref='server_test')
    pubkey = Column(Text)
    check_time = Column(TIMESTAMP)
    apis = relationship('API')

    def verify(self, sign):
        """
        签名验证
        :param sign:
        :return:
        """
        # self.pubkey = load_key()[0]
        # return verify(pubkey_str(), sign, self.get('pubkey'))
        if isinstance(sign, str):
            sign = bytes(sign, encoding='utf-8')
        try:
            rsa.verify(self.pubkey.encode(), sign, rsa.PublicKey.load_pkcs1(self.pubkey.encode()))
            return True
        except rsa.pkcs1.VerificationError:
            return False

class Subscription(Base):
    __tablename__ = 'subscription'

    server_hash = Column(ForeignKey(Servers.hash), primary_key=True)
    API_id = Column(ForeignKey('api.id'))
    time = Column(TIMESTAMP)
    updated = Column(Boolean)
    pushed = Column(Boolean)

class API(Base):
    __tablename__ = 'api'

    id = Column(Integer, primary_key=True, autoincrement=True)
    server_hash = Column(ForeignKey(Servers.hash))
    name = Column(String(32))
    route = Column(String(128))
    description = Column(String(128))
    params = Column(String(128))
    res = Column(Text)
    status = Column(Integer)
    sensitivity = Column(Integer)
    note = Column(Text)
    subscriber = relationship('Servers', secondary=Subscription)

class Tables(Base):
    __tablename__ = 'table'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), unique=True)
    description = Column(String(256))
    server_hash = Column(ForeignKey(Servers.hash))
    fields = relationship('Fields', backref='table')
    status = Column(Integer)
    note = Column(Text)
    sensitivity = Column(Integer)

class Fields(Base):
    __tablename__ = 'field'

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(256))
    note = Column(Text)
    name = Column(String(64))
    table_id = Column(Integer, ForeignKey(Tables.id))
    sensitivity = Column(Integer)

if __name__ == '__main__':
    Base.metadata.create_all()