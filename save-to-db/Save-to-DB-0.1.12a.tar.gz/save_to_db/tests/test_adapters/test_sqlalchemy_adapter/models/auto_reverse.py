import sqlalchemy as sa
from sqlalchemy.orm import backref, relationship
from save_to_db.adapters.utils.relation_type import RelationType
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
    

class ModelAutoReverseOne(__CommonColumns, Base):
    __tablename__ = 'model_auto_reverse_one'
    ITEM_RELATIONS = {
        'two_a_1_1_first': ('one_1_1_first', RelationType.ONE_TO_ONE),
        'two_a_1_1_second': ('one_1_1_second', RelationType.ONE_TO_ONE),
        'two_b_1_1': (None, RelationType.MANY_TO_ONE),  # no reverse setup
        'three_a_x_1_first': ('one_1_x_first', RelationType.MANY_TO_ONE),
        'three_a_x_1_second': ('one_1_x_second', RelationType.MANY_TO_ONE),
        'three_b_x_1': (None, RelationType.MANY_TO_ONE),
        'four_a_x_x_first': ('one_x_x_first', RelationType.MANY_TO_MANY),
        'four_a_x_x_second': ('one_x_x_second', RelationType.MANY_TO_MANY),
        'four_b_x_x': (None, RelationType.MANY_TO_MANY),
    }
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    #--- one-to-one ---
    
    # related name auto configured
    two_a_1_1_first_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_auto_reverse_two_a.id', ondelete='CASCADE'))
    # (this field will be many-to-one, as there is no way to set
    #  `uselist=False` on the other side)
    two_a_1_1_first = relationship(
        'ModelAutoReverseTwoA',
        backref=backref('one_1_1_first', uselist=False),
        foreign_keys=[two_a_1_1_first_id])
    
    # related name manually configured on both sides
    two_a_1_1_second_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_auto_reverse_two_a.id', ondelete='CASCADE'))
    two_a_1_1_second = relationship(
        'ModelAutoReverseTwoA',
        back_populates='one_1_1_second',
        foreign_keys=[two_a_1_1_second_id])
    
    # no related_name (it's a many-to-one-field)
    two_b_1_1_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_auto_reverse_two_b.id', ondelete='CASCADE'))
    two_b_1_1 = relationship('ModelAutoReverseTwoB')
    
    #--- one-to-many ---
    
    # related name auto configured
    three_a_x_1_first_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_auto_reverse_three_a.id'))
    three_a_x_1_first = relationship(
        'ModelAutoReverseThreeA',
        backref='one_1_x_first',
        foreign_keys=[three_a_x_1_first_id])
    
    # related name manually configured on both sides
    three_a_x_1_second_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_auto_reverse_three_a.id'))
    three_a_x_1_second = relationship(
        'ModelAutoReverseThreeA',
        back_populates='one_1_x_second',
        foreign_keys=[three_a_x_1_second_id])
    
    # no related_name
    three_b_x_1_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('model_auto_reverse_three_b.id'))
    three_b_x_1 = relationship('ModelAutoReverseThreeB')
    
    #--- many-to-many ---
    
    # related name auto configured
    four_a_x_x_first = relationship(
        'ModelAutoReverseFourA',
        secondary='model_auto_reverse_one_to_four_a_first',
        backref='one_x_x_first')
    
    # related name manually configured on both sides
    four_a_x_x_second = relationship(
        'ModelAutoReverseFourA',
        secondary='model_auto_reverse_one_to_four_a_second',
        back_populates='one_x_x_second')
    
    # no related_name
    
    four_b_x_x = relationship(
        'ModelAutoReverseFourB',
        secondary='model_auto_reverse_one_to_four_b')
    

class ModelAutoReverseTwoA(__CommonColumns, Base):
    __tablename__ = 'model_auto_reverse_two_a'
    ITEM_RELATIONS = {
        'one_1_1_first': ('two_a_1_1_first', RelationType.ONE_TO_ONE),
        'one_1_1_second': ('two_a_1_1_second', RelationType.ONE_TO_ONE),
    }
    
    id = sa.Column(sa.Integer, primary_key=True)
    one_1_1_second = relationship(
        ModelAutoReverseOne,
        back_populates='two_a_1_1_second',
        foreign_keys=[ModelAutoReverseOne.two_a_1_1_second_id],
        uselist=False)
    

class ModelAutoReverseTwoB(__CommonColumns, Base):
    __tablename__ = 'model_auto_reverse_two_b'
    ITEM_RELATIONS = {}
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    
class ModelAutoReverseThreeA(__CommonColumns, Base):
    __tablename__ = 'model_auto_reverse_three_a'
    ITEM_RELATIONS = {
        'one_1_x_first': ('three_a_x_1_first', RelationType.ONE_TO_MANY),
        'one_1_x_second': ('three_a_x_1_second', RelationType.ONE_TO_MANY),
    }

    
    id = sa.Column(sa.Integer, primary_key=True)
    one_1_x_second = relationship(
        ModelAutoReverseOne,
        back_populates='three_a_x_1_second',
        foreign_keys=[ModelAutoReverseOne.three_a_x_1_second_id])
    

class ModelAutoReverseThreeB(__CommonColumns, Base):
    __tablename__ = 'model_auto_reverse_three_b'
    ITEM_RELATIONS = {}
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    
class ModelAutoReverseFourA(__CommonColumns, Base):
    __tablename__ = 'model_auto_reverse_four_a'
    ITEM_RELATIONS = {
        'one_x_x_first': ('four_a_x_x_first', RelationType.MANY_TO_MANY),
        'one_x_x_second': ('four_a_x_x_second', RelationType.MANY_TO_MANY),
    }
    
    id = sa.Column(sa.Integer, primary_key=True)
    
    one_x_x_second = relationship(
        ModelAutoReverseOne,
        secondary='model_auto_reverse_one_to_four_a_second',
        back_populates='four_a_x_x_second')


class ModelAutoReverseOneToFourAFirst(Base):
    __tablename__ = 'model_auto_reverse_one_to_four_a_first'
    
    one_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(ModelAutoReverseOne.id, ondelete='CASCADE'),
        primary_key=True)
    one = relationship(
        ModelAutoReverseOne,
        foreign_keys=[one_id])
    
    four_a_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(ModelAutoReverseFourA.id, ondelete='CASCADE'),
        primary_key=True)
    four_a = relationship(
        ModelAutoReverseFourA,
        foreign_keys=[four_a_id])


class ModelAutoReverseOneToFourASecond(Base):
    __tablename__ = 'model_auto_reverse_one_to_four_a_second'
    
    one_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(ModelAutoReverseOne.id, ondelete='CASCADE'),
        primary_key=True)
    one = relationship(
        ModelAutoReverseOne,
        foreign_keys=[one_id])
    
    four_a_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(ModelAutoReverseFourA.id, ondelete='CASCADE'),
        primary_key=True)
    four_a = relationship(
        ModelAutoReverseFourA,
        foreign_keys=[four_a_id])
    

class ModelAutoReverseFourB(__CommonColumns, Base):
    __tablename__ = 'model_auto_reverse_four_b'
    
    id = sa.Column(sa.Integer, primary_key=True)
    ITEM_RELATIONS = {}
    

class ModelAutoReverseOneToFourB(Base):
    __tablename__ = 'model_auto_reverse_one_to_four_b'
    
    one_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(ModelAutoReverseOne.id, ondelete='CASCADE'),
        primary_key=True)
    one = relationship(
        ModelAutoReverseOne,
        foreign_keys=[one_id])
    
    four_b_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(ModelAutoReverseFourB.id, ondelete='CASCADE'),
        primary_key=True)
    four_b = relationship(
        ModelAutoReverseFourB,
        foreign_keys=[four_b_id])