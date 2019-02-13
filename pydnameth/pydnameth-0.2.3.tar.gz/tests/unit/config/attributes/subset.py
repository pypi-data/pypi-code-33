import unittest
from tests.definitions import ROOT_DIR
from pydnameth import Data
from pydnameth import Experiment
from pydnameth import Annotations
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

    def test_pass_indexes_num_elems(self):
        self.config.attributes.observables.types = {'gender': 'any'}
        self.config.attributes_dict = load_attributes_dict(self.config)
        indexes = pass_indexes(self.config, 'gender', 'any', 'any')
        self.assertEqual(len(indexes), 729)

    def test_pass_indexes_num_f(self):
        self.config.attributes.observables.types = {'gender': 'F'}
        self.config.attributes_dict = load_attributes_dict(self.config)
        indexes = pass_indexes(self.config, 'gender', 'F', 'any')
        self.assertEqual(len(indexes), 388)

    def test_pass_indexes_num_m(self):
        self.config.attributes.observables.types = {'gender': 'M'}
        self.config.attributes_dict = load_attributes_dict(self.config)
        indexes = pass_indexes(self.config, 'gender', 'M', 'any')
        self.assertEqual(len(indexes), 341)

    def test_get_indexes_num_elems(self):
        self.config.attributes.observables.types = {'gender': 'any'}
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
