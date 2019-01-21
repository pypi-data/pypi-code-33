import json
from mlpc.entity.base_entities import BaseEntity
from mlpc.utils.log import debug


class _ParameterValues:
    def __init__(self):
        pass

    def __getitem__(self, item):
        return self.__dict__[item]


class ParameterReader:
    # noinspection PyMethodMayBeStatic
    def load_from_json(self, config_file_path):
        def _obj_encoder(dct):
            pv = _ParameterValues()
            for k in dct:
                setattr(pv, k, dct[k])
            return pv

        assert isinstance(config_file_path, str)
        debug("Reading parameter file", config_file_path)
        with open(config_file_path, 'r') as json_file:
            values_dict = json.load(json_file, object_hook=_obj_encoder)
        return values_dict


class Parameters(BaseEntity):
    def __init__(self, storage):
        super().__init__(storage)

    load_from_json = ParameterReader().load_from_json

    def save(self, parameter_values, parameter_set_name="parameters"):
        assert isinstance(parameter_set_name, str)
        from mlpc.utils.json_object_serializer import serialize_to_json_string
        json_string = serialize_to_json_string(parameter_values)
        file_path = self._storage.get_filepath_for_writing("parameters", parameter_set_name, "json")
        debug("Writing parameter values to:", file_path)
        with open(file_path, 'w') as json_file:
            json_file.writelines(json_string)
        return file_path
