from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, create_engine, desc, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import logging

Base = declarative_base()

class PermissionServerGroups(Base):
    __tablename__ = 'permission_server_groups'
    id = Column(Integer, Sequence('permission_server_groups_id_seq', start=1001, increment=1), primary_key=True)
    server_group_id = Column(Integer, nullable=False)
    permission_grant_id = Column(Integer, ForeignKey('permission_grant.id'))
    permission_grant = relationship('PermissionGrant', back_populates='server_groups')

    def __eq__(self, other):
        return self.server_group_id == other.server_group_id and \
               self.permission_grant_id == other.permission_grant_id

    def __ne__(self, other):
        return not self.server_group_id == other.server_group_id and \
               self.permission_grant_id == other.permission_grant_id

    def __repr__(self):
        return f'<ts3ekkosingle.models.PermissionServerGroups id={self.id}, server_group={self.server_group_id}>'


class PermissionGrant(Base):
    __tablename__ = 'permission_grant'
    id = Column(Integer, Sequence('permission_grant_id_seq', start=1001, increment=1), primary_key=True)
    name = Column(String, nullable=False)
    deny = Column(Boolean, default=False)

    server_groups = relationship('PermissionServerGroups', back_populates='permission_grant')
    channel_group = Column(Integer)
    unique_id = Column(String(50))

    @property
    def server_group_set(self):
        return set([sg.server_group_id for sg in self.server_groups])

    def __eq__(self, other):
        return self.channel_group == other.channel_group and \
               self.unique_id == other.unique_id and \
               self.server_group_set == other.server_group_set

    def __ne__(self, other):
        return not self.channel_group == other.channel_group and \
               self.unique_id == other.unique_id and \
               self.server_group_set == other.server_group_set

    def __repr__(self):
        return f'<ts3ekkosingle.models.PermissionGrant id={self.id}, deny={self.deny}, name={self.name} ' \
               f'channel_group={self.channel_group}, unique_id={self.unique_id}, ' \
               f'server_groups={self.server_groups}, prop:server_group_set={self.server_group_set}>'

    @property
    def pretty_repr(self):
        return f'<Grant deny={self.deny}, name={self.name} ' \
               f'channel_group={self.channel_group}, unique_id={self.unique_id}, ' \
               f'server_groups={self.server_group_set}>'

    def pretty_noname_repr(self, sgid_data=None):
        logging.debug(sgid_data)
        server_groups_resolved = []
        for sgid in self.server_group_set:
            try:
                server_groups_resolved.append(str(sgid_data[sgid]))
            except KeyError:
                server_groups_resolved.append(str(sgid))

        output = f'(id={self.id}): Channel Group: {self.channel_group or "any"}, '
        logging.debug(output)
        if server_groups_resolved:
            output += f'Server Groups: {",".join(sorted(server_groups_resolved))}, '
        else:
            output += f'Server Groups: any, '

        if self.unique_id:
            output += f'Unique ID: {self.unique_id}'
        logging.debug(output)
        return output


def startup(username='ekko', password='ekkopassword', dbhost='dbhost', dbname='ekkodb'):
    engine = create_engine(f'postgres://{username}:{password}@{dbhost}/{dbname}')

    Base.metadata.create_all(engine)

    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)

    session = DBSession()
    return session
