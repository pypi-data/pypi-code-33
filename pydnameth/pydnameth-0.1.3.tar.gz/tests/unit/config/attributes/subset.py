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
from pydnameth.config.attributes.subset import pass_indexes
from pydnameth.config.attributes.subset import get_indexes


class TestLoadAnnotations(unittest.TestCase):

    def setUp(self):
        target = 'age'
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
            chr=Chromosome.non_gender.value,
            gene_region=GeneRegion.yes.value,
            geo=CommonTypes.any.value,
            probe_class=CommonTypes.any.value
        )

        observables = Observables(
            file_name='observables',
            types={'gender': 'vs'}
        )

        cells = Cells(
            file_name='cells',
            types=CommonTypes.any.value
        )

        attributes = Attributes(
            observables=observables,
            cells=cells
        )

        self.config = Config(
            data=data,
            setup=setup,
            annotations=annotations,
            attributes=attributes,
            target=target
        )


    def test_pass_indexes_num_elems(self):
        self.config.attributes.observables.types = {'gender': CommonTypes.any.value}
        self.config.attributes_dict = load_attributes_dict(self.config)
        indexes = pass_indexes(self.config, 'gender', CommonTypes.any.value, CommonTypes.any.value)
        self.assertEqual(len(indexes), 729)


    def test_pass_indexes_num_f(self):
        self.config.attributes.observables.types = {'gender': 'F'}
        self.config.attributes_dict = load_attributes_dict(self.config)
        indexes = pass_indexes(self.config, 'gender', 'F', CommonTypes.any.value)
        self.assertEqual(len(indexes), 388)


    def test_pass_indexes_num_m(self):
        self.config.attributes.observables.types = {'gender': 'M'}
        self.config.attributes_dict = load_attributes_dict(self.config)
        indexes = pass_indexes(self.config, 'gender', 'M', CommonTypes.any.value)
        self.assertEqual(len(indexes), 341)


    def test_get_indexes_num_elems(self):
        self.config.attributes.observables.types = {'gender': CommonTypes.any.value}
        self.config.attributes_dict = load_attributes_dict(self.config)
        indexes = get_indexes(self.config)
        self.assertEqual(len(indexes), 729)


    def test_get_indexes_num_f(self):
        self.config.attributes.observables.types = {'gender': 'F'}
        self.config.attributes_dict = load_attributes_dict(self.config)
        indexes = get_indexes(self.config)
        self.assertEqual(len(indexes), 388)


    def test_get_indexes_num_m(self):
        self.config.attributes.observables.types = {'gender': 'M'}
        self.config.attributes_dict = load_attributes_dict(self.config)
        indexes = get_indexes(self.config)
        self.assertEqual(len(indexes), 341)


if __name__ == '__main__':
    unittest.main()
