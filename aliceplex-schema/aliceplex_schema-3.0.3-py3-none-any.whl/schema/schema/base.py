from dataclasses import Field, asdict, fields, is_dataclass
from typing import Any, Dict, List, Optional

from marshmallow import Schema, post_load, pre_dump, pre_load

__all__ = ["DataClassSchema"]


class DataClassSchema(Schema):

    @pre_dump
    def convert(self, data) -> Dict[str, Any]:
        """
        Convert dataclass object to dict.

        :param data: Input data
        :type data: Any
        :return: Dictionary for dumping.
        :rtype: Dict[str, Any]
        """
        new_data = asdict(data) if is_dataclass(data) else {**data}
        self.filter_data(new_data)
        return new_data

    @pre_load
    def filter(self, data: Dict[str, Any]) -> Dict[str, Any]:
        new_data = {**data}
        self.filter_data(new_data)
        return new_data

    def filter_data(self, data: Dict[str, Any]):
        data_class_fields = self._get_field()
        for field in data_class_fields:
            name = field.name
            if name not in data:
                continue
            f_type = field.type
            origin = getattr(f_type, "__origin__", None)
            args = getattr(f_type, "__args__", ())
            if list in (f_type, origin):
                data[name] = self._filter_list(data[name])
            elif self._is_str(f_type, origin, args) and data[name] == "":
                # Replace empty string with None
                data[name] = None

    @staticmethod
    def _is_str(f_type, origin, args) -> bool:
        return str in (f_type, origin) or str in args

    @staticmethod
    def _filter_list(data: Optional[list]) -> list:
        if data is None:
            # Convert None to empty list for List field
            return []
        # Filter None and empty string in list
        return [value for value in data if value is not None and value != ""]

    def _get_field(self) -> List[Field]:
        """
        Get fields of the dataclass

        :return: Defined fields on dataclass
        :rtype: List[Field]
        :raises ValueError: if data_class is not a dataclass
        """
        data_class = self.data_class
        if not is_dataclass(data_class):
            raise ValueError("You should use dataclass for DataClassSchema")
        # noinspection PyDataclass
        return fields(data_class)

    @post_load
    def post_load(self, data) -> Any:
        """
        Convert dict to dataclass object

        :param data: Input data
        :type data: Dict[str, Any]
        :return: Dataclass
        :rtype: Any
        """
        data_class = self.data_class
        return data_class(**data)

    @property
    def data_class(self) -> type:
        """
        Provide the dataclass of this schema.

        :return: Dataclass
        :rtype: type
        """
        raise NotImplementedError()
