import unittest
from tests.definitions import ROOT_DIR
from pydnameth.config.data.data import Data
from pydnameth.config.experiment.experiment import Experiment
from pydnameth.config.annotations.annotations import Annotations
from pydnameth.config.attributes.attributes import Observables
from pydnameth.config.attributes.attributes import Cells
from pydnameth.config.attributes.attributes import Attributes
from pydnameth.config.config import Config
from pydnameth.infrastucture.load.attributes import load_attributes_dict


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

    def test_load_attributes_dict_num_elems(self):
        attributes_dict = load_attributes_dict(self.config)
        self.assertEqual(len(attributes_dict['age']), 729)

    def test_load_attributes_dict_age_range(self):
        attributes_dict = load_attributes_dict(self.config)
        self.assertEqual(max(attributes_dict['age']) - min(attributes_dict['age']), 80)


if __name__ == '__main__':
    unittest.main()
