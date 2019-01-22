"""Utils for working with SQLAlchemy."""
import csv
from contextlib import suppress
from decimal import Decimal
import fractions
import logging
import os.path
from typing import Sequence
import uuid

from flask import abort
import flask_sqlalchemy
import pytz
from sqlalchemy import (
	Column,
	Integer,
	String,
	ForeignKey,
	DateTime,
	TypeDecorator,
	Numeric,
	ForeignKeyConstraint,
	)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql.base import ischema_names
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm.collections import (
	InstrumentedList,
	InstrumentedSet,
	InstrumentedDict,
	)
from sqlalchemy.types import Concatenable, UserDefinedType

logger = logging.getLogger(__name__)
db = flask_sqlalchemy.SQLAlchemy()


class CIText(Concatenable, UserDefinedType):
	"""Class to use Postgres' CIText column in SQLAlchemy.

	From: https://github.com/mahmoudimus/sqlalchemy-citext
	"""

	def get_col_spec(self):
		return 'CITEXT'

	def bind_processor(self, dialect):
		def process(value):
			return value
		return process

	def result_processor(self, dialect, coltype):
		def process(value):
			return value
		return process


# Register CIText to SQLAlchemy's Postgres reflection subsystem.
ischema_names['citext'] = CIText


def psycopg_uri(username, password, db_name, host='', port=None):
	"""Create a URL for psycopg2.

	http://docs.sqlalchemy.org/en/latest/dialects/postgresql.html#module-sqlalchemy.dialects.postgresql.psycopg2  # noqa
	"""
	if port:
		return f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}'
	else:
		return f'postgresql+psycopg2://{username}:{password}@{host}/{db_name}'


def foreign_key_col(col, **kwargs):
	"""Create a column with a ForeignKey that cascades."""
	return Column(
		col.type,
		ForeignKey(col, ondelete='CASCADE', onupdate='CASCADE'),
		**kwargs
		)


def parent_key(column, col_type=Integer, nullable=False, index=True, **kwargs):
	"""Shorthand for a Column that is a foreign key to a parent."""
	return Column(
		col_type,
		ForeignKey(column, ondelete='CASCADE', onupdate='CASCADE'),
		nullable=nullable,
		index=index,
		**kwargs
		)


class Fraction(TypeDecorator):
	"""Type for storing and retrieving Fractions.

	Currently, this is backed by a Decimal, so some precision may be lost on
	conversion.
	"""

	impl = Numeric

	def process_bind_param(self, value, dialect):
		if value is None:
			return None
		assert isinstance(value, int) or isinstance(value, fractions.Fraction)
		return value.numerator / Decimal(value.denominator)

	def process_result_value(self, value, dialect):
		if value is None:
			return None
		assert isinstance(value, Decimal)
		return fractions.Fraction(value).limit_denominator()


class UTCDateTime(TypeDecorator):
	"""Type for storing and retrieving DateTimes as UTC.

	Naive datetimes are rejected.
	The returned value is always a non-naive UTC datetime.
	"""

	impl = DateTime

	def process_bind_param(self, value, dialect):
		"""Fix inputs."""
		if value is None:
			return None
		if value.tzinfo is None:
			raise ValueError
		return value.astimezone(pytz.utc)

	def process_result_value(self, value, dialect):
		"""Normalize output."""
		if value is None:
			return None
		return value.replace(tzinfo=pytz.utc)


class BaseMixin():
	# Build table args using inheritance

	_table_args = ()
	_table_kwargs = {}

	@declared_attr
	def __table_args__(cls):
		args = []
		kwargs = {}
		for par_cls in reversed(cls.mro()):
			with suppress(AttributeError):
				args.extend(par_cls._table_args)
			with suppress(AttributeError):
				kwargs.update(par_cls._table_kwargs)
		return tuple(args) + (kwargs,)

	@classmethod
	def find_one(cls, **kwargs):
		"""Query this table for a single row matching kwargs filters."""
		return cls.query.filter_by(**kwargs).one()

	@classmethod
	def find_one_or_404(cls, **kwargs):
		"""Query this table for a single row, flask.abort(404) if not found."""
		try:
			cls.find_one(**kwargs)
		except (NoResultFound, MultipleResultsFound):
			abort(404)

	@classmethod
	def create(cls, **kwargs):
		obj = cls(**kwargs)
		cls.query.session.add(obj)
		return obj

	@classmethod
	def find_create(cls, create_args=None, **kwargs):
		"""Find or create an instance of this model.

		Optionally provide arguments used only for creating the object, not
		querying.
		"""
		try:
			return cls.find_one(**kwargs)
		except NoResultFound:
			create_args = dict(create_args or {})
			create_args.update(kwargs)
			return cls.create(**create_args)

	@classmethod
	def exists(cls, **kwargs):
		try:
			cls.find_one(**kwargs)
		except NoResultFound:
			return False
		else:
			return True

	@classmethod
	def cast(cls, obj, allow_none=True):
		if obj is None:
			if allow_none:
				return None
			else:
				raise ValueError(f'Cannot cast None to {cls}')
		elif isinstance(obj, cls):
			return obj
		else:
			raise TypeError(f'Cannot cast an object of {type(obj)} to {cls}')

	@classmethod
	def _repr_class_template(cls):
		col_names = [col.name for col in cls.__table__.columns]
		item_format = '{col}={{self.{col}!r}}'
		fields = ', '.join(item_format.format(col=col) for col in col_names)
		return '{class_name}({fields})'.format(
			class_name=cls.__name__,
			fields=fields,
			)

	def __repr__(self):
		class_template = self._repr_class_template()
		return class_template.format(obj=self, self=self)

	@classmethod
	def query_default_order(cls):
		"""Return a class query with a default (stable) order."""
		primary_key_cols = inspect(cls).primary_key
		cls.query.order_by(*primary_key_cols)

	@classmethod
	def _get_pkey_col(cls):
		primary_key_cols = inspect(cls).primary_key
		if len(primary_key_cols) != 1:
			msg = 'Class %s does not have exactly one primary key column' % cls
			raise NotImplementedError(msg)
		return primary_key_cols[0]

	@classmethod
	def fkey_constraint(
		cls, cols: Sequence,
		ondelete='CASCADE',
		onupdate='CASCADE',
		) -> ForeignKeyConstraint:
		"""Return a ForeignKeyConstraint for the primary keys of this model."""
		return ForeignKeyConstraint(
			cols,
			inspect(cls).primary_key,
			ondelete=ondelete,
			onupdate=onupdate,
			)

	@classmethod
	def pkey(cls, **kwargs):
		"""Return a Column definition for the primary key of this model."""
		pkey_col = cls._get_pkey_col()
		return foreign_key_col(pkey_col, **kwargs)

	def to_dict(self, sub=None):
		"""Create a dict of this obj's attributes and optionally related objects.

		Specify which relationships to include as keys in `sub`. The value of
		each key is the argument to pass to that relation's `to_dict`.

		For example:

		class Character(BaseModel):
			first_name = Column(String)
			last_name = Column(String)
			parents = relationship(Character)
			siblings = relationship(Character)

		`bart.to_dict({'parents': {'siblings': None}}) == {
			'first_name': 'Bart',
			'last_name': 'Simpson',
			'parents': [
				{
					'first_name': 'Homer',
					'last_name': 'Simpson',
					'siblings': [],
					},
				{
					'first_name': 'Marge',
					'last_name': 'Simpson',
					'siblings': [
						{
							'first_name': 'Patty',
							'last_name': 'Bouvier',
							},
						{
							'first_name': 'Selma',
							'last_name': 'Bouvier',
							},
						],
					},
				]
			}`
		"""
		instance_state = inspect(self)
		columns = instance_state.mapper.column_attrs
		out = {col.key: getattr(self, col.key) for col in columns}
		sub = sub or {}
		for relationship_name, args in sub.items():
			relationship = getattr(self, relationship_name)
			try:
				out[relationship_name] = relationship.to_dict(args)
			except AttributeError:
				if isinstance(relationship, (InstrumentedList, InstrumentedSet)):
					out[relationship_name] = []
					for relation in relationship:
						out[relationship_name].append(relation.to_dict(args))
				elif isinstance(relationship, InstrumentedDict):
					out[relationship_name] = {}
					for k, relation in relationship.items():
						out[relationship_name][k] = relation.to_dict(args)
				else:
					msg = "Don't know how to handle relationship of type {rel_type}".format(
						rel_type=type(relationship),
						)
					raise NotImplementedError(msg)
		return out

	@classmethod
	def _get_path(cls, path, directory):
		if path is None:
			path = '%s.csv' % cls.__tablename__
			if directory:
				path = os.path.join(directory, path)
		else:
			if directory:
				raise ValueError('Must not pass path and directory')
		return path

	@classmethod
	def merge_csv(cls, path=None, directory=None, io_wrapper=None):
		"""Load data from a csv file and merge into db.

		This is slower than import because orm objects are created.
		"""
		path = cls._get_path(path, directory)
		logger.info('Importing %s to %s', path, cls)
		with open(path, 'r', newline='') as infile:
			cls.merge_from_file(infile, io_wrapper=io_wrapper)

	@classmethod
	def import_csv(cls, path=None, directory=None, io_wrapper=None):
		"""Import data from a csv file."""
		path = cls._get_path(path, directory)
		logger.info('Importing %s to %s', path, cls)
		with open(path, 'r', newline='') as infile:
			cls.import_from_file(infile, io_wrapper=io_wrapper)

	@classmethod
	def export_csv(cls, path=None, directory=None, io_wrapper=None):
		"""Export data to csv file."""
		path = cls._get_path(path, directory)
		logger.info('Exporting %s to %s', cls, path)
		try:
			with open(path, 'r', newline='') as infile:
				reader = csv.DictReader(infile)
				fieldnames = reader.fieldnames
		except IOError:
			fieldnames = None
		with open(path, 'w', newline='') as outfile:
			cls.export_to_file(outfile, fieldnames=fieldnames, io_wrapper=io_wrapper)

	@classmethod
	def import_from_file(cls, infile, io_wrapper=None):
		logger.info('Importing to %s', cls)
		if io_wrapper:
			infile = io_wrapper(infile)
		reader = csv.DictReader(infile)
		# TODO try insert many (not on session)
		# http://stackoverflow.com/questions/25694234/bulk-update-in-sqlalchemy-core-using-where
		# db.session.bulk_insert_mappings(cls, reader)
		rows = list(reader)
		db.engine.execute(cls.__table__.insert(), rows)

	@classmethod
	def merge_from_file(cls, infile, io_wrapper=None):
		logger.info('Merging to %s', cls)
		if io_wrapper:
			infile = io_wrapper(infile)
		reader = csv.DictReader(infile)
		for row in reader:
			obj = cls(**row)
			cls.query.session.merge(obj)

	@classmethod
	def export_to_file(cls, outfile, fieldnames=None, io_wrapper=None):
		logger.info('Exporting %s', cls)
		if io_wrapper:
			outfile = io_wrapper(outfile)
		fieldnames = fieldnames or []
		for col in cls.__table__.columns:
			if col.name not in fieldnames:
				fieldnames.append(col.name)
		writer = csv.DictWriter(outfile, fieldnames, extrasaction='ignore')
		writer.writeheader()
		try:
			query = cls.query_default_order()
		except NotImplementedError:
			query = cls.query
		for obj in query:
			writer.writerow(obj.__dict__)


class IntegerPKey():
	"""Mixin for models with an integer 'id' as the primary key."""

	id = Column(Integer, primary_key=True)

	@classmethod
	def cast(cls, obj, **kwargs):
		if isinstance(obj, int):
			value = cls.query.get(obj)
			if not value:
				raise ValueError(f"No {cls} could be found from int {obj}")
			return value
		else:
			return super().cast(obj, **kwargs)

	@classmethod
	def _get_pkey_col(cls):
		return cls.id

	def __hash__(self):
		return self.id

	def __eq__(self, other):
		return self.__class__ == other.__class__ and self.id == other.id

	@classmethod
	def query_default_order(cls):
		return cls.query.order_by(cls.id)


def parse_uuid(obj) -> uuid.UUID:
	"""Parse a UUID from obj.

	Raises:
		ValueError: If obj cannot be parsed into a UUID
		TypeError: If the type of obj isn't known how to parse
	"""
	# TODO this would be more pythonic with try except instead of checking types
	if isinstance(obj, uuid.UUID):
		return obj
	if isinstance(obj, str):
		return uuid.UUID(obj)
	if isinstance(obj, (bytes, bytearray)):
		return uuid.UUID(bytes=obj)
	if isinstance(obj, tuple):
		return uuid.UUID(fields=obj)
	if isinstance(obj, int):
		return uuid.UUID(int=obj)
	raise TypeError


class UUID4Pkey():
	"""Mixin for models with a UUID4 'id' as the primary key."""

	id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

	@classmethod
	def cast(cls, obj, **kwargs):
		try:
			obj_as_uuid = parse_uuid(obj)
		except (ValueError, TypeError):
			return super().cast(obj, **kwargs)
		else:
			value = cls.query.get(obj_as_uuid)
			if not value:
				raise ValueError(f"No {cls} could be found from uuid {obj}")
			return value

	@classmethod
	def _get_pkey_col(cls):
		return cls.id

	def __hash__(self):
		return hash((self.__class__, self.id))

	def __eq__(self, other):
		return self.__class__ == other.__class__ and self.id == other.id

	@classmethod
	def query_default_order(cls):
		return cls.query.order_by(cls.id)


class AbbrPKey():

	abbr = Column(String, primary_key=True)

	@classmethod
	def cast(cls, obj, **kwargs):
		if isinstance(obj, str):
			value = cls.query.get(obj)
			if not value:
				raise ValueError(f"No {cls} could be found from str {obj}")
			return value
		else:
			return super().cast(obj, **kwargs)

	@classmethod
	def _get_pkey_col(cls):
		return cls.abbr

	def __hash__(self):
		return hash(self.abbr)

	def __eq__(self, other):
		return self.__class__ == other.__class__ and self.abbr == other.abbr

	@classmethod
	def query_default_order(cls):
		return cls.query.order_by(cls.abbr)


class no_autoflush(object):
	"""A context manager to suppress autoflush."""
	def __init__(self, session):
		self.session = session
		self.autoflush = session.autoflush

	def __enter__(self):
		self.session.autoflush = False

	def __exit__(self, type, value, traceback):
		self.session.autoflush = self.autoflush
