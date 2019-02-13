import unittest
from tests.definitions import ROOT_DIR
from pydnameth.config.data.data import Data
from pydnameth.config.experiment.experiment import Experiment
from pydnameth.config.annotations.annotations import Annotations
from pydnameth.config.attributes.attributes import Observables
from pydnameth.config.attributes.attributes import Cells
from pydnameth.config.attributes.attributes import Attributes
from pydnameth.config.config import Config
from pydnameth.infrastucture.load.annotations import load_annotations_dict


class TestLoadAnnotations(unittest.TestCase):

    def setUp(self):
        data = Data(
            name='cpg_beta',
            path=ROOT_DIR,
            base='fixtures'
        )

        experiment = Experiment(
            type=None,
            task=None,
            method=None,
            params=None
        )

        annotations = Annotations(
            name='annotations',
            exclude='none',
            cross_reactive='ex',
            snp='ex',
            chr='NS',
            gene_region='yes',
            geo='any',
            probe_class='any'
        )

        observables = Observables(
            name='observables',
            types={}
        )

        cells = Cells(
            name='cells',
            types='any'
        )

        attributes = Attributes(
            target='age',
            observables=observables,
            cells=cells
        )

        self.config = Config(
            data=data,
            experiment=experiment,
            annotations=annotations,
            attributes=attributes,
            is_run=True,
            is_root=True
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
