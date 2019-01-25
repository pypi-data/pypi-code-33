import abc
import json
import os
import tempfile

import sri.pipelines.datasets as datasets
from sri.common import constants

# If the NIST testing executable is available, then we will try to evaluate predictions with it.
try:
    import d3m_outputs
    EVAL_PREDICTIONS = True
except ImportError:
    EVAL_PREDICTIONS = False

PREDICTIONS_PATH = os.path.join(tempfile.gettempdir(), 'test_predictions.csv')

class BasePipeline(object):
    # Prediction pipelines are epcected to go all the way and end with a single dataframe.
    def __init__(self, datasets, prediction_pipeline):
        self._datasets = datasets
        self._prediction_pipeline = prediction_pipeline
        self._pipeline = self._gen_pipeline()

    @abc.abstractmethod
    def _gen_pipeline(self):
        '''
        Create a D3M pipeline for this class.
        '''
        pass

    def assert_result(self, tester, results, dataset, score_dir):
        '''
        Make sure that the results from an invocation of this pipeline are valid.
        Children should override if they have more details.
        '''

        # The results are always nested.
        tester.assertEquals(len(results), 1)

        # Prediction pipelines should always have a d3m index and give the correct number of rows.
        if (self._prediction_pipeline):
            tester.assertTrue(constants.D3M_INDEX in results[0].columns)
            tester.assertEquals(len(results[0]), datasets.get_size(dataset))

            if (EVAL_PREDICTIONS):
                self._eval_predictions(tester, results[0], score_dir)

    def is_prediction_pipeline(self):
        return self._prediction_pipeline

    def get_id(self):
        return self._pipeline.id

    def get_datasets(self):
        '''
        Get the name of datasets compatibile with this pipeline.
        '''
        return self._datasets

    def get_json(self):
        # Make it pretty.
        return json.dumps(json.loads(self._pipeline.to_json()), indent = 4)

    def _eval_predictions(self, tester, predictions, score_dir):
        predictions.to_csv(PREDICTIONS_PATH, index = False)

        nist_predictions = d3m_outputs.Predictions(PREDICTIONS_PATH, score_dir)
        tester.assertTrue(nist_predictions.is_valid())

        targets_path = os.path.join(score_dir, 'targets.csv')
        scores = nist_predictions.score(targets_path)
        tester.assertIsNotNone(scores)
