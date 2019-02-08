import unittest
import time
import sys
import io
from multiprocessing import Process, Queue
from watson_machine_learning_client.log_util import get_logger
from watson_machine_learning_client.experiments import Experiments
from preparation_and_cleaning import *


class TestWMLClientWithExperiment(unittest.TestCase):
    deployment_uid = None
    model_uid = None
    scoring_url = None
    definition_1_uid = None
    definition_1_url = None
    definition_2_uid = None
    definition_2_url = None
    trained_model_uid = None
    experiment_uid = None
    experiment_run_uid = None
    logger = get_logger(__name__)

    @classmethod
    def setUpClass(self):
        TestWMLClientWithExperiment.logger.info("Service Instance: setting up credentials")
        self.wml_credentials = get_wml_credentials()
        # reload(site)
        self.client = get_client()
        self.cos_resource = get_cos_resource()
        self.bucket_names = prepare_cos(self.cos_resource)

    @classmethod
    def tearDownClass(self):
        clean_cos(self.cos_resource, self.bucket_names)

    def test_01_service_instance_details(self):
        TestWMLClientWithExperiment.logger.info("Check client ...")
        self.assertTrue(self.client.__class__.__name__ == 'WatsonMachineLearningAPIClient')

        TestWMLClientWithExperiment.logger.info("Getting instance details ...")
        details = self.client.service_instance.get_details()
        TestWMLClientWithExperiment.logger.debug(details)

        self.assertTrue("published_models" in str(details))
        self.assertEqual(type(details), dict)

    def test_02_save_definition1(self):
        TestWMLClientWithExperiment.logger.info("Save model definition ...")

        self.client.repository.DefinitionMetaNames.show()

        metadata = {
            self.client.repository.DefinitionMetaNames.NAME: "my_training_definition",
            self.client.repository.DefinitionMetaNames.DESCRIPTION: "my_description",
            self.client.repository.DefinitionMetaNames.AUTHOR_NAME: "John Smith",
            self.client.repository.DefinitionMetaNames.FRAMEWORK_NAME: "tensorflow",
            self.client.repository.DefinitionMetaNames.FRAMEWORK_VERSION: "1.5",
            self.client.repository.DefinitionMetaNames.RUNTIME_NAME: "python",
            self.client.repository.DefinitionMetaNames.RUNTIME_VERSION: "3.5",
            self.client.repository.DefinitionMetaNames.EXECUTION_COMMAND: "python3 tensorflow_mnist_softmax.py --trainingIters 20"
            }

        model_content_path = './artifacts/tf-softmax-model.zip'
        definition_details = self.client.repository.store_definition(training_definition=model_content_path, meta_props=metadata)
        TestWMLClientWithExperiment.definition_1_uid = self.client.repository.get_definition_uid(definition_details)
        TestWMLClientWithExperiment.definition_1_url = self.client.repository.get_definition_url(definition_details)
        TestWMLClientWithExperiment.logger.info("Saved model definition uid: " + str(TestWMLClientWithExperiment.definition_1_uid))

    def test_03_save_definition2(self):
        TestWMLClientWithExperiment.logger.info("Save model definition ...")
        metadata = {
            self.client.repository.DefinitionMetaNames.NAME: "my_training_definition",
            self.client.repository.DefinitionMetaNames.DESCRIPTION: "my_description",
            self.client.repository.DefinitionMetaNames.AUTHOR_NAME: "John Smith",
            self.client.repository.DefinitionMetaNames.FRAMEWORK_NAME: "tensorflow",
            self.client.repository.DefinitionMetaNames.FRAMEWORK_VERSION: "1.5",
            self.client.repository.DefinitionMetaNames.RUNTIME_NAME: "python",
            self.client.repository.DefinitionMetaNames.RUNTIME_VERSION: "3.5",
            self.client.repository.DefinitionMetaNames.EXECUTION_COMMAND: "python3 tensorflow_mnist_softmax.py --trainingIters 20"
            }

        model_content_path = './artifacts/tf-softmax-model.zip'
        definition_details = self.client.repository.store_definition(training_definition=model_content_path, meta_props=metadata)
        TestWMLClientWithExperiment.definition_2_uid = self.client.repository.get_definition_uid(definition_details)
        TestWMLClientWithExperiment.definition_2_url = self.client.repository.get_definition_url(definition_details)
        TestWMLClientWithExperiment.logger.info("Saved model definition uid: " + str(TestWMLClientWithExperiment.definition_2_uid))

    def test_04_list_definitions(self):
        TestWMLClientWithExperiment.logger.info("List definitions")
        self.client.training.list_definitions()

    def test_05_get_uid_url(self):
        def_details = self.client.training.get_definition_details(TestWMLClientWithExperiment.definition_1_uid)
        uid = self.client.training.get_definition_uid(def_details)
        url = self.client.training.get_definition_url(def_details)
        self.assertIsNotNone(uid)
        self.assertIsNotNone(url)

    def test_06_get_definition_details(self):
        TestWMLClientWithExperiment.logger.info("Getting definition details ...")
        details_1 = self.client.training.get_definition_details(TestWMLClientWithExperiment.definition_1_uid)
        TestWMLClientWithExperiment.logger.info(details_1)
        self.assertTrue('my_training_definition' in str(details_1))

        details_2 = self.client.training.get_definition_details(TestWMLClientWithExperiment.definition_2_uid)
        TestWMLClientWithExperiment.logger.info(details_2)
        self.assertTrue('my_training_definition' in str(details_2))

    def test_07_save_experiment(self):
        metadata = {
                    self.client.repository.ExperimentMetaNames.NAME: "xxx",
                    self.client.repository.ExperimentMetaNames.AUTHOR_EMAIL: "js@js.com",
                    self.client.repository.ExperimentMetaNames.TRAINING_DATA_REFERENCE: get_cos_training_data_reference(self.bucket_names),
                    self.client.repository.ExperimentMetaNames.TRAINING_RESULTS_REFERENCE: get_cos_training_results_reference(self.bucket_names),
                    self.client.repository.ExperimentMetaNames.TRAINING_REFERENCES: [
                        {
                            "name": "mnist_nn",
                            "training_definition_url": TestWMLClientWithExperiment.definition_1_url,
                            "compute_configuration": {"name": "p100"}
                        },
                        {
                            "name": "mnist_cnn",
                            "training_definition_url": TestWMLClientWithExperiment.definition_2_url,
                            "compute_configuration": {"name": "p100"}
                        },
                    ]
                }

        TestWMLClientWithExperiment.logger.info(get_cos_training_data_reference(self.bucket_names))
        TestWMLClientWithExperiment.logger.info(get_cos_training_results_reference(self.bucket_names))
        experiment_details = self.client.repository.store_experiment(meta_props=metadata)

        TestWMLClientWithExperiment.experiment_uid = self.client.experiments.get_definition_uid(experiment_details)
        url = self.client.experiments.get_definition_url(experiment_details)

        experiment_specific_details = self.client.experiments.get_definition_details(TestWMLClientWithExperiment.experiment_uid)
        self.assertTrue(TestWMLClientWithExperiment.experiment_uid in str(experiment_specific_details))
        self.assertIsNotNone(url)

    def test_08_list_experiment_definitions(self):
        stdout_ = sys.stdout
        captured_output = io.StringIO()  # Create StringIO object
        sys.stdout = captured_output  # and redirect stdout.
        self.client.experiments.list_definitions()  # Call function.
        sys.stdout = stdout_  # Reset redirect.
        self.assertTrue(TestWMLClientWithExperiment.experiment_uid in captured_output.getvalue())
        self.client.experiments.list_definitions()  # Just to see values.

    def test_09_delete_experiment(self):
        self.client.repository.delete(TestWMLClientWithExperiment.experiment_uid)

    def test_10_delete_definitions(self):
        self.client.repository.delete(TestWMLClientWithExperiment.definition_1_uid)
        self.client.repository.delete(TestWMLClientWithExperiment.definition_2_uid)


if __name__ == '__main__':
    unittest.main()
