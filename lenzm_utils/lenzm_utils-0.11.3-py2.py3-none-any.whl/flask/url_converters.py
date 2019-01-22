from datetime import date, datetime
from typing import List, Iterable, Type
from uuid import UUID

from werkzeug.routing import BaseConverter, ValidationError


class DateConverter(BaseConverter):
	"""URL converter for dates."""

	def to_python(self, value: str) -> date:
		"""Turn a string into a date."""
		try:
			return datetime.strptime(value, '%Y-%m-%d').date()
		except ValueError:
			raise ValidationError()

	def to_url(self, d: date) -> str:
		"""Format a date for a URL."""
		return d.isoformat()


def ListConverter(char: str) -> Type[BaseConverter]:
	"""Factory to create a Converter that turns delimited strings into lists."""

	class _ListConverter(BaseConverter):
		f"""URL converter for Iterable <-> '{char}' delimited string."""

		def to_python(self, value: str) -> List[str]:
			"""Create a tuple from char delimited values."""
			return value.split(char)

		def to_url(self, value: Iterable[str]) -> str:
			"""Serialize Iterable to char delimited values."""
			return char.join(value)

	return _ListConverter


class UUIDConverter(BaseConverter):
	"""URL converter for UUIDs."""

	def to_python(self, value: str) -> UUID:
		"""Create the UUID from string."""
		return UUID(value)

	def to_url(self, value: UUID) -> str:
		"""Turn a UUID into a string."""
		return str(value)
