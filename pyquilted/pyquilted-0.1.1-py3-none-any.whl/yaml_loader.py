import ruamel.yaml


class YamlLoader:
    @staticmethod
    def ordered_load(stream):
        return ruamel.yaml.load(stream, Loader=ruamel.yaml.RoundTripLoader)
