import sqlalchemy as sa
from sqlalchemy.orm import backref, relationship
from sqlalchemy.schema import ForeignKeyConstraint, UniqueConstraint

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


class ModelConstraintsOne(__CommonColumns, Base):
    __tablename__ = 'model_constraints_one'
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    f_text = sa.Column(sa.Text, nullable=False)
    f_integer = sa.Column(sa.Integer, unique=True)
    f_string = sa.Column(sa.String, nullable=False, unique=True)
    
    two_1_x = relationship(
        'ModelConstraintsTwo',
        back_populates='one_x_1',
        foreign_keys='[ModelConstraintsTwo.one_x_1_id]')
    
    three_1_x = relationship(
        'ModelConstraintsThree',
        back_populates='one_x_1',
        foreign_keys='[ModelConstraintsThree.one_x_1_id]')
    
    five_1_1 = relationship(
        'ModelConstraintsFive',
        back_populates='one_1_1',
        foreign_keys='[ModelConstraintsFive.one_1_1_id]',
        uselist=False)


class ModelConstraintsTwo(__CommonColumns, Base):
    __tablename__ = 'model_constraints_two'
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    one_x_1_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_constraints_one.id', ondelete='CASCADE'))
    one_x_1 = relationship(
        ModelConstraintsOne,
        back_populates='two_1_x',
        foreign_keys=[one_x_1_id])
    
    three_x_x = relationship(
        'ModelConstraintsThree',
        secondary='model_constraints_two_to_three',
        back_populates='two_x_x')

    four_primary_one = sa.Column(sa.Integer, nullable=False)
    four_primary_two = sa.Column(sa.Integer, nullable=False)
    four_x_1 = relationship(
        'ModelConstraintsFour',
        back_populates='two_1_x',
        foreign_keys=[four_primary_one, four_primary_two])
    
    __table_args__ = (
        ForeignKeyConstraint([four_primary_one, four_primary_two],
                             ['model_constraints_four.primary_one',
                              'model_constraints_four.primary_two'],
                             name='model_four_fkey'),
    )
    

class ModelConstraintsTwoToThree(Base):
    __tablename__ = 'model_constraints_two_to_three'
    
    two_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(ModelConstraintsTwo.id, ondelete='CASCADE'),
        primary_key=True)
    three_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_constraints_three.id', ondelete='CASCADE'),
        primary_key=True)
    

class ModelConstraintsThree(__CommonColumns, Base):
    __tablename__ = 'model_constraints_three'
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    one_x_1_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_constraints_one.id', ondelete='CASCADE'),
        nullable=False)
    one_x_1 = relationship(
        ModelConstraintsOne,
        back_populates='three_1_x',
        foreign_keys=[one_x_1_id])
    
    two_x_x = relationship(
        ModelConstraintsTwo,
        secondary='model_constraints_two_to_three',
        back_populates='three_x_x')
    
    four_primary_one = sa.Column(sa.Integer, nullable=True)
    four_primary_two = sa.Column(sa.Integer, nullable=True)
    four_x_1 = relationship(
        'ModelConstraintsFour',
        back_populates='three_1_x',
        foreign_keys=[four_primary_one, four_primary_two])
    
    __table_args__ = (
        ForeignKeyConstraint([four_primary_one, four_primary_two],
                             ['model_constraints_four.primary_one',
                              'model_constraints_four.primary_two'],
                             name='model_four_fkey'),
    )


class ModelConstraintsFour(__CommonColumns, Base):
    __tablename__ = 'model_constraints_four'
    
    primary_one = sa.Column(sa.Integer, primary_key=True)
    primary_two = sa.Column(sa.Integer, primary_key=True)
    
    two_1_x = relationship(
        ModelConstraintsTwo,
        back_populates='four_x_1',
        foreign_keys=[ModelConstraintsTwo.four_primary_one,
                      ModelConstraintsTwo.four_primary_two,])
    
    three_1_x = relationship(
        ModelConstraintsThree,
        back_populates='four_x_1',
        foreign_keys=[ModelConstraintsThree.four_primary_one,
                      ModelConstraintsThree.four_primary_two,])
    
    five_1_1 = relationship(
        'ModelConstraintsFive',
        back_populates='four_1_1',
        foreign_keys='[ModelConstraintsFive.four_primary_one,'
                      'ModelConstraintsFive.four_primary_two,]',
        uselist=False)
    
    __table_args__ = (
        UniqueConstraint('f_integer', 'f_string', name='unique_1'),
    )
    

class ModelConstraintsFive(__CommonColumns, Base):
    __tablename__ = 'model_constraints_five'
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    one_1_1_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_constraints_one.id', ondelete='CASCADE'),
        unique=True)
    one_1_1 = relationship(
        ModelConstraintsOne,
        back_populates='five_1_1',
        foreign_keys=[one_1_1_id])
    
    four_primary_one = sa.Column(sa.Integer)
    four_primary_two = sa.Column(sa.Integer)
    four_1_1 = relationship(
        ModelConstraintsFour,
        back_populates='five_1_1',
        foreign_keys=[four_primary_one, four_primary_two])
    
    six_1_1 = relationship(
        'ModelConstraintsSix',
        back_populates='five_1_1',
        foreign_keys='[ModelConstraintsSix.five_1_1_id,]',
        uselist=False)
    
    __table_args__ = (
        UniqueConstraint('four_primary_one', 'four_primary_two',
                         name='unique_1'),
        ForeignKeyConstraint([four_primary_one, four_primary_two],
                             ['model_constraints_four.primary_one',
                              'model_constraints_four.primary_two'],
                             name='model_four_fkey'),
    )

class ModelConstraintsSix(__CommonColumns, Base):
    __tablename__ = 'model_constraints_six'
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    five_1_1_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_constraints_five.id', ondelete='CASCADE'),
        nullable=False)
    five_1_1 = relationship(
        ModelConstraintsFive,
        back_populates='six_1_1',
        foreign_keys=[five_1_1_id])
    
    __table_args__ = (
        UniqueConstraint('five_1_1_id', 'f_integer', name='unique_1'),
    )
    
    
class ModelConstraintsSelf(__CommonColumns, Base):
    __tablename__ = 'model_constraints_self'
    
    code = sa.Column(sa.String, primary_key=True)
    
    # many-to-one, not_null
    parent_x_1_code = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_constraints_self.code', ondelete='CASCADE'),
        nullable=False)
    child_1_x = relationship(
        'ModelConstraintsSelf',
        backref=backref('parent_x_1', remote_side=[code]),
        foreign_keys=[parent_x_1_code])
    
    # self one-to-one, unique
    first_parent_1_1_code = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_constraints_self.code', ondelete='CASCADE'),
        unique=True)
    first_child_1_1 = relationship(
        'ModelConstraintsSelf',
        backref=backref('first_parent_1_1', remote_side=[code]),
        foreign_keys=[first_parent_1_1_code],
        uselist=False)
    
    # self one-to-one, unique, not_null
    second_parent_1_1_code = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_constraints_self.code', ondelete='CASCADE'),
        unique=True,
        nullable=False)
    second_child_1_1 = relationship(
        'ModelConstraintsSelf',
        backref=backref('second_parent_1_1', remote_side=[code]),
        foreign_keys=[second_parent_1_1_code],
        uselist=False)
    
    # self many-to-many
    parent_x_x = relationship(
        'ModelConstraintsSelf',
        secondary='model_constraints_self_to_self',
        foreign_keys='[ModelConstraintsSelfToSelf.parent_code]',
        back_populates='child_x_x')
    child_x_x = relationship(
        'ModelConstraintsSelf',
        secondary='model_constraints_self_to_self',
        foreign_keys='[ModelConstraintsSelfToSelf.child_code]',
        back_populates='parent_x_x')


class ModelConstraintsSelfToSelf(__CommonColumns, Base):
    __tablename__ = 'model_constraints_self_to_self'
    
    parent_code = sa.Column(
        sa.Integer,
        sa.ForeignKey(ModelConstraintsSelf.code, ondelete='CASCADE'),
        primary_key=True)
    parent = relationship(
        ModelConstraintsSelf,
        foreign_keys=[parent_code])
    
    child_code = sa.Column(
        sa.Integer,
        sa.ForeignKey(ModelConstraintsSelf.code, ondelete='CASCADE'),
        primary_key=True)
    child = relationship(
        ModelConstraintsSelf,
        foreign_keys=[child_code])