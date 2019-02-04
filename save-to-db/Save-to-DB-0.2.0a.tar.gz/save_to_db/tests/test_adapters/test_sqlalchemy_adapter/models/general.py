import sqlalchemy as sa
from sqlalchemy.orm import backref, relationship

from ..config import Base



class __CommonColumns(object):
    f_binary = sa.Column(sa.LargeBinary, nullable=True)
    f_boolean = sa.Column(sa.Boolean, nullable=True)
    f_string = sa.Column(sa.String, nullable=True)
    f_text = sa.Column(sa.Text, nullable=True)
    f_integer = sa.Column(sa.Integer, nullable=True)
    f_float = sa.Column(sa.Float, nullable=True)
    f_date = sa.Column(sa.Date, nullable=True)
    f_time = sa.Column(sa.Time, nullable=True)
    f_datetime = sa.Column(sa.DateTime, nullable=True)


class ModelGeneralOneToOne(Base):
    __tablename__ = 'model_general_one_to_one'
    
    parent_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_general_one.id', ondelete='CASCADE'),
        primary_key=True)
    parent = relationship(
        'ModelGeneralOne',
        foreign_keys=[parent_id])
    
    child_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_general_one.id', ondelete='CASCADE'),
        primary_key=True)
    child = relationship(
        'ModelGeneralOne',
        foreign_keys=[child_id])


class ModelGeneralOne(__CommonColumns, Base):
    __tablename__ = 'model_general_one'
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    #--- self relations ---
    
    # self one-to-one
    parent_1_1_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_general_one.id', ondelete='CASCADE'))
    child_1_1 = relationship(
        'ModelGeneralOne',
        backref=backref('parent_1_1', remote_side=[id]),
        foreign_keys=[parent_1_1_id],
        uselist=False)
    
    # self one-to-many and many-to-one
    parent_x_1_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_general_one.id'))
    child_1_x = relationship(
        'ModelGeneralOne',
        backref=backref('parent_x_1', remote_side=[id]),
        foreign_keys=[parent_x_1_id])
    
    # self many-to-many
    parent_x_x = relationship(
        'ModelGeneralOne',
        secondary='model_general_one_to_one',
        back_populates='child_x_x',
        primaryjoin=(id==ModelGeneralOneToOne.__table__.c.parent_id),
        secondaryjoin=(id==ModelGeneralOneToOne.__table__.c.child_id))
    child_x_x = relationship(
        'ModelGeneralOne',
        secondary='model_general_one_to_one',
        back_populates='parent_x_x',
        primaryjoin=(id==ModelGeneralOneToOne.__table__.c.child_id),
        secondaryjoin=(id==ModelGeneralOneToOne.__table__.c.parent_id))
    
    #--- relations with other ---
    
    # one-to-one
    two_1_1_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_general_two.id', ondelete='CASCADE'))
    two_1_1 = relationship(
        'ModelGeneralTwo',
        back_populates='one_1_1',
        foreign_keys=[two_1_1_id])
    
    # one-to-many
    two_1_x = relationship(
        'ModelGeneralTwo',
        foreign_keys='[ModelGeneralTwo.one_x_1_id]',
        back_populates='one_x_1')
    
    # many-to-one
    two_x_1_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_general_two.id', ondelete='CASCADE'))
    two_x_1 = relationship(
        'ModelGeneralTwo',
        back_populates='one_1_x',
        foreign_keys=[two_x_1_id])
    
    # many-to-many
    two_x_x = relationship(
        'ModelGeneralTwo',
        secondary='model_general_one_to_two',
        back_populates='one_x_x')


class ModelGeneralOneToTwo(Base):
    __tablename__ = 'model_general_one_to_two'
    
    one_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(ModelGeneralOne.id, ondelete='CASCADE'),
        primary_key=True)
    one = relationship(
        ModelGeneralOne,
        foreign_keys=[one_id])
    
    two_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_general_two.id', ondelete='CASCADE'),
        primary_key=True)
    two = relationship(
        'ModelGeneralTwo',
        foreign_keys=[two_id])


class ModelGeneralTwoToTwo(Base):
    __tablename__ = 'model_general_two_to_two'
    
    parent_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_general_two.id', ondelete='CASCADE'),
        primary_key=True)
    parent = relationship(
        'ModelGeneralTwo',
        foreign_keys=[parent_id])
    
    child_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_general_two.id', ondelete='CASCADE'),
        primary_key=True)
    child = relationship(
        'ModelGeneralTwo',
        foreign_keys=[child_id])


class ModelGeneralTwo(__CommonColumns, Base):
    __tablename__ = 'model_general_two'
    
    id = sa.Column(sa.Integer, primary_key=True)

    #--- self relations ---
    
    # self one-to-one
    parent_1_1_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_general_two.id', ondelete='CASCADE'))
    child_1_1 = relationship(
        'ModelGeneralTwo',
        backref=backref('parent_1_1', remote_side=[id]),
        foreign_keys=[parent_1_1_id],
        uselist=False)
    
    # self one-to-many and many-to-one
    parent_x_1_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_general_two.id'))
    child_1_x = relationship(
        'ModelGeneralTwo',
        backref=backref('parent_x_1', remote_side=[id]),
        foreign_keys=[parent_x_1_id])
    
    # self many-to-many
    parent_x_x = relationship(
        'ModelGeneralTwo',
        secondary='model_general_two_to_two',
        back_populates='child_x_x',
        primaryjoin=(id==ModelGeneralTwoToTwo.__table__.c.parent_id),
        secondaryjoin=(id==ModelGeneralTwoToTwo.__table__.c.child_id))
    child_x_x = relationship(
        'ModelGeneralTwo',
        secondary='model_general_two_to_two',
        back_populates='parent_x_x',
        primaryjoin=(id==ModelGeneralTwoToTwo.__table__.c.child_id),
        secondaryjoin=(id==ModelGeneralTwoToTwo.__table__.c.parent_id))
    
    
    #--- relations with other ---
    
    # one-to-one
    one_1_1 = relationship(
        ModelGeneralOne,
        back_populates='two_1_1', uselist=False,
        foreign_keys=[ModelGeneralOne.two_1_1_id])
    
    # one-to-many
    one_1_x = relationship(
        ModelGeneralOne,
        foreign_keys=[ModelGeneralOne.two_x_1_id],
        back_populates='two_x_1')
    
    # many-to-one
    one_x_1_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(ModelGeneralOne.id, use_alter=True, ondelete='CASCADE'))
    one_x_1 = relationship(
        ModelGeneralOne,
        back_populates='two_1_x',
        foreign_keys=[one_x_1_id])
    
    # many-to-many
    one_x_x = relationship(
        ModelGeneralOne,
        secondary='model_general_one_to_two',
        back_populates='two_x_x')
    

