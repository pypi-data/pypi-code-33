import copy
from aether.sky_utils import sky_utils

class app_io_utilities(object):

    @staticmethod
    def mimic_placeholder_output_structure(output_structure, placeholder_variants, app):
        if isinstance(output_structure, dict):
            response = {}
            for key, leaf in output_structure.iteritems():
                value = app_io_utilities._replace_leaf_with_placeholder(leaf, placeholder_variants, app)
                if value is None:
                    return None
                response[key] = value
        else:
            response = app_io_utilities._replace_leaf_with_placeholder(output_structure, placeholder_variants, app)
            if response is None:
                return None

        return response

    @staticmethod
    def _replace_leaf_with_placeholder(leaf, placeholder_variants, app):
        name = leaf.__class__.__name__
        if name in placeholder_variants:
            p = copy.deepcopy(placeholder_variants[name])
            if hasattr(p, 'set_app'):
                p.set_app(app)
            return p
        return leaf


    @staticmethod
    def _structure_as_string(structure):
        if isinstance(structure, str):
            return structure

        if isinstance(structure, dict):
            r = {}
            for key, leaf in structure.iteritems():
                if isinstance(leaf, str):
                    r[key] = leaf
                else:
                    r[key] = leaf.__class__.__name__
            return r

        return structure.__class__.__name__

    @staticmethod
    def string_as_structure(string_structure, structure_objects):
        if isinstance(string_structure, str) or isinstance(string_structure, unicode):
            if string_structure in structure_objects:
                string_structure = copy.deepcopy(structure_objects[string_structure])
            return string_structure

        if isinstance(string_structure, dict):
            s = {}
            for key, leaf in string_structure.iteritems():
                if leaf in structure_objects:
                    leaf = copy.deepcopy(structure_objects[leaf])
                s[key] = leaf
            return s

        return None

    # @staticmethod
    # def serialize_to_input(uri_parameters, input_structure):
    #     """Transform the keys listed in input_structure into Serialized Protocol Buffers"""
    #     for key in input_structure:
    #         if key not in uri_parameters.keys():
    #             raise KeyError("Key {} from input_structure missing in url_parameters: {}".format(key, uri_parameters.keys()))
    #
    #         if hasattr(uri_parameters[key], 'is_placeholder_object'):
    #             uri_parameters[key] = uri_parameters[key].to_pb()
    #
    #         # uri_parameters[key] = uri_parameters[key].SerializeToString()
    #         uri_parameters[key] = json_format.MessageToJson(uri_parameters[key])
    #
    #     return uri_parameters

    @staticmethod
    def marshal_output(content, output_structure):
        if isinstance(output_structure, dict):
            for key, leaf in output_structure.iteritems():
                if key not in content:
                    raise KeyError("Key {} from output_structure missing in content: {}".format(key, content.keys()))
                content[key] = sky_utils.deserialize_pb(content[key], leaf)
        else:
            content = sky_utils.deserialize_pb(content, output_structure)
        return content