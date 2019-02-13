import abc
import numpy as np


class GetStrategy(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_single_base(self, config, items):
        pass

    @abc.abstractmethod
    def get_aux(self, config, item):
        pass

    def get_target(self, config, normed=False):
        target = config.attributes_dict[config.attributes.target]
        if normed:
            target_normed = [(float(x) - min(target)) /
                             (float(max(target)) - float(min(target)))
                             for x in target]
            target = target_normed
        return target


class CPGGetStrategy(GetStrategy):

    def get_single_base(self, config, items):
        rows = [config.base_dict[item] for item in items]
        return config.base_data[np.ix_(rows, config.attributes_indexes)]

    def get_aux(self, config, item):
        return ';'.join(config.cpg_gene_dict[item])


class AttributesGetStrategy(GetStrategy):

    def get_single_base(self, config, items):
        pass

    def get_aux(self, config, item):
        pass
