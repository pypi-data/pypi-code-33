import unittest
from tests.definitions import ROOT_DIR
from pydnameth import Data
from pydnameth import DataType
from pydnameth import Setup
from pydnameth import Annotations
from pydnameth import CommonTypes
from pydnameth import CrossReactive
from pydnameth import SNP
from pydnameth import Chromosome
from pydnameth import GeneRegion
from pydnameth import Observables
from pydnameth import Cells
from pydnameth import Attributes
from pydnameth import Config
from pydnameth.infrastucture.load.attributes import load_attributes_dict
from pydnameth.config.attributes.subset import pass_indexes
from pydnameth.config.attributes.subset import get_indexes


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
            types={'gender': 'vs'}
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
            attributes=attributes
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
