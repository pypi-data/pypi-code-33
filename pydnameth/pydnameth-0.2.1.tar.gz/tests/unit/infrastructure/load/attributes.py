import unittest
from tests.definitions import ROOT_DIR
from pydnameth.config.data.data import Data
from pydnameth.config.data.types import DataType
from pydnameth.config.setup.setup import Setup
from pydnameth.config.annotations.annotations import Annotations
from pydnameth.config.common import CommonTypes
from pydnameth.config.annotations.types import CrossReactive
from pydnameth.config.annotations.types import SNP
from pydnameth.config.annotations.types import Chromosome
from pydnameth.config.annotations.types import GeneRegion
from pydnameth.config.attributes.attributes import Observables
from pydnameth.config.attributes.attributes import Cells
from pydnameth.config.attributes.attributes import Attributes
from pydnameth.config.config import Config
from pydnameth.infrastucture.load.attributes import load_attributes_dict


class TestLoadAnnotations(unittest.TestCase):

    def setUp(self):

        data = Data(
            name='cpg_beta',
            type=DataType.cpg,
            path=ROOT_DIR,
            base='fixtures'
        )

        setup = Setup(
            experiment='',
            task='',
            method='',
            params={}
        )

        annotations = Annotations(
            name='annotations',
            exclude=CommonTypes.none.value,
            cross_reactive=CrossReactive.exclude.value,
            snp=SNP.exclude.value,
            chr=Chromosome.non_sex.value,
            gene_region=GeneRegion.yes.value,
            geo=CommonTypes.any.value,
            probe_class=CommonTypes.any.value
        )

        observables = Observables(
            name='observables',
            types={}
        )

        cells = Cells(
            name='cells',
            types=CommonTypes.any.value
        )

        attributes = Attributes(
            target='age',
            observables=observables,
            cells=cells
        )

        self.config = Config(
            data=data,
            setup=setup,
            annotations=annotations,
            attributes=attributes,
        )

    def test_load_attributes_dict_num_elems(self):
        attributes_dict = load_attributes_dict(self.config)
        self.assertEqual(len(attributes_dict['age']), 729)

    def test_load_attributes_dict_num_keys(self):
        attributes_dict = load_attributes_dict(self.config)
        self.assertEqual(len(list(attributes_dict.keys())), 2)

    def test_load_attributes_dict_age_range(self):
        attributes_dict = load_attributes_dict(self.config)
        self.assertEqual(max(attributes_dict['age']) - min(attributes_dict['age']), 80)


if __name__ == '__main__':
    unittest.main()
