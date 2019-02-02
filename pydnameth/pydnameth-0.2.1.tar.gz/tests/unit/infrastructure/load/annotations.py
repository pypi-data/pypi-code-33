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
from pydnameth.infrastucture.load.annotations import load_annotations_dict


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

    def test_load_annotations_dict_num_elems(self):
        annotations_dict = load_annotations_dict(self.config)
        self.assertEqual(len(annotations_dict['ID_REF']), 300)

    def test_load_annotations_dict_num_keys(self):
        annotations_dict = load_annotations_dict(self.config)
        self.assertEqual(len(list(annotations_dict.keys())), 10)

    def test_load_annotations_dict_num_chrs(self):
        annotations_dict = load_annotations_dict(self.config)
        self.assertEqual(len(set(annotations_dict['CHR'])), 11)

    def test_load_annotations_dict_num_bops(self):
        annotations_dict = load_annotations_dict(self.config)
        self.assertEqual(len(set(annotations_dict['BOP'])), 82)


if __name__ == '__main__':
    unittest.main()
