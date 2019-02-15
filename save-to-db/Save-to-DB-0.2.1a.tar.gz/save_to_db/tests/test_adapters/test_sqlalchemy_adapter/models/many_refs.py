import sqlalchemy as sa
from sqlalchemy.orm import relationship

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


class ModelManyRefsOne(__CommonColumns, Base):
    __tablename__ = 'model_many_refs_one'
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    # many-to-one
    two_x_1_id_a = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_many_refs_two.id', ondelete='CASCADE',
                      use_alter=True))
    two_x_1_a = relationship(
        'ModelManyRefsTwo',
        back_populates='one_1_x_a',
        foreign_keys=[two_x_1_id_a],
        post_update=True)
    
    # one-to-many
    two_1_x_b = relationship(
        'ModelManyRefsTwo',
        back_populates='one_x_1_b',
        foreign_keys='[ModelManyRefsTwo.one_x_1_id_b]',
        post_update=True)
    
    # many-to-many
    two_x_x_a = relationship(
        'ModelManyRefsTwo',
        secondary='model_many_refs_one_to_two_a',
        back_populates='one_x_x_a',
        post_update=True)
    
    two_x_x_b = relationship(
        'ModelManyRefsTwo',
        secondary='model_many_refs_one_to_two_b',
        back_populates='one_x_x_b',
        post_update=True)
    
    # one-to-one
    two_1_1_id_a = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_many_refs_two.id', ondelete='CASCADE',
                      use_alter=True),
        unique=True)
    two_1_1_a = relationship(
        'ModelManyRefsTwo',
        back_populates='one_1_1_a',
        foreign_keys=[two_1_1_id_a],
        post_update=True)
    
    two_1_1_b = relationship(
        'ModelManyRefsTwo',
        back_populates='one_1_1_b',
        foreign_keys='[ModelManyRefsTwo.one_1_1_id_b]',
        uselist=False,
        post_update=True)
    

class ModelManyRefsOneToTwoA(Base):
    __tablename__ = 'model_many_refs_one_to_two_a'
    
    one_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(ModelManyRefsOne.id, ondelete='CASCADE'),
        primary_key=True)
    two_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_many_refs_two.id', ondelete='CASCADE'),
        primary_key=True)


class ModelManyRefsOneToTwoB(Base):
    __tablename__ = 'model_many_refs_one_to_two_b'
    
    one_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(ModelManyRefsOne.id, ondelete='CASCADE',
                      use_alter=True),
        primary_key=True)
    two_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_many_refs_two.id', ondelete='CASCADE',
                      use_alter=True),
        primary_key=True)


class ModelManyRefsTwo(__CommonColumns, Base):
    __tablename__ = 'model_many_refs_two'
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    # one-to-many
    one_1_x_a = relationship(
        ModelManyRefsOne,
        back_populates='two_x_1_a',
        foreign_keys='[ModelManyRefsOne.two_x_1_id_a]',
        post_update=True)
    
    # many-to-one
    one_x_1_id_b = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_many_refs_one.id', ondelete='CASCADE'))
    one_x_1_b = relationship(
        ModelManyRefsOne,
        back_populates='two_1_x_b',
        foreign_keys=[one_x_1_id_b],
        post_update=True)
    
    # many-to-many
    one_x_x_a = relationship(
        ModelManyRefsOne,
        secondary='model_many_refs_one_to_two_a',
        back_populates='two_x_x_a',
        post_update=True)
    
    one_x_x_b = relationship(
        ModelManyRefsOne,
        secondary='model_many_refs_one_to_two_b',
        back_populates='two_x_x_b',
        post_update=True)
    
    # one-to-one
    one_1_1_a = relationship(
        ModelManyRefsOne,
        back_populates='two_1_1_a',
        foreign_keys=[ModelManyRefsOne.two_1_1_id_a],
        uselist=False,
        post_update=True)
    
    one_1_1_id_b = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_many_refs_one.id', ondelete='CASCADE'),
        unique=True)
    one_1_1_b = relationship(
        ModelManyRefsOne,
        back_populates='two_1_1_b',
        foreign_keys=[one_1_1_id_b],
        post_update=True)