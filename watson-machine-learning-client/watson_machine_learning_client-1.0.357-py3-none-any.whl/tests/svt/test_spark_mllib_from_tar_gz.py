import unittest
import os
import sys
from os.path import join as path_join
import json
from watson_machine_learning_client.log_util import get_logger
from preparation_and_cleaning import *


class TestWMLClientWithSpark(unittest.TestCase):
    deployment_uid = None
    model_uid = None
    scoring_url = None
    definition_url = None
    logger = get_logger(__name__)

    @classmethod
    def setUpClass(self):
        TestWMLClientWithSpark.logger.info("Service Instance: setting up credentials")

        self.wml_credentials = get_wml_credentials()
        self.client = get_client()
        self.model_path = os.path.join(os.getcwd(), 'artifacts', 'heart-drug-sample', 'drug-selection-model.tgz')
        self.pipeline_path = os.path.join(os.getcwd(), 'artifacts', 'heart-drug-sample', 'drug-selection-pipeline.tgz')
        self.meta_path = os.path.join(os.getcwd(), 'artifacts', 'heart-drug-sample', 'drug-selection-meta.json')

        with open(TestWMLClientWithSpark.meta_path) as json_data:
            metadata = json.load(json_data)

        self.model_meta = metadata['model_meta']
        self.pipeline_meta = metadata['pipeline_meta']

    def test_1_service_instance_details(self):
        TestWMLClientWithSpark.logger.info("Check client ...")
        self.assertTrue(type(self.client).__name__ == 'WatsonMachineLearningAPIClient')

        TestWMLClientWithSpark.logger.info("Getting instance details ...")
        details = self.client.service_instance.get_details()
        TestWMLClientWithSpark.logger.debug(details)

        self.assertTrue("published_models" in str(details))
        self.assertEqual(type(details), dict)

    def test_2_publish_pipeline(self):
        TestWMLClientWithSpark.logger.info("Publishing spark pipeline ...")

        definition_meta = {
            self.client.repository.DefinitionMetaNames.AUTHOR_NAME: self.pipeline_meta['author']['name'],
            self.client.repository.DefinitionMetaNames.NAME: self.pipeline_meta['name'],
            self.client.repository.DefinitionMetaNames.FRAMEWORK_NAME: self.pipeline_meta['framework']['name'],
            self.client.repository.DefinitionMetaNames.FRAMEWORK_VERSION: self.pipeline_meta['framework']['version'],
            self.client.repository.DefinitionMetaNames.RUNTIME_NAME: self.pipeline_meta['framework']['runtimes'][0]['name'],
            self.client.repository.DefinitionMetaNames.RUNTIME_VERSION: self.pipeline_meta['framework']['runtimes'][0]['version'],
            self.client.repository.DefinitionMetaNames.DESCRIPTION: self.pipeline_meta['description'],
            self.client.repository.DefinitionMetaNames.TRAINING_DATA_REFERENCES: self.pipeline_meta['training_data_reference']
        }

        definition_details = self.client.repository.store_definition(TestWMLClientWithSpark.pipeline_path, meta_props=definition_meta)

        print('ZZZ; ' + str(definition_details))

        TestWMLClientWithSpark.definition_url = definition_details['entity']['training_definition_version']['url']
        print('DEF URL: ' + TestWMLClientWithSpark.definition_url)
        self.assertTrue('training_definitions' in TestWMLClientWithSpark.definition_url)

    def test_3_publish_model(self):
        TestWMLClientWithSpark.logger.info("Publishing spark model ...")
        self.client.repository.ModelMetaNames.show()

        model_props = {
            self.client.repository.ModelMetaNames.NAME: self.model_meta['name'],
            self.client.repository.ModelMetaNames.FRAMEWORK_NAME: self.model_meta['framework']['name'],
            self.client.repository.ModelMetaNames.FRAMEWORK_VERSION: self.model_meta['framework']['version'],
            self.client.repository.ModelMetaNames.LABEL_FIELD: self.model_meta['label_column'],
            self.client.repository.ModelMetaNames.RUNTIME_NAME: self.model_meta['framework']['runtimes'][0]['name'],
            self.client.repository.ModelMetaNames.RUNTIME_VERSION: self.model_meta['framework']['runtimes'][0]['version'],
            self.client.repository.ModelMetaNames.TRAINING_DATA_REFERENCE: self.model_meta['training_data_reference'][0],
            self.client.repository.ModelMetaNames.TRAINING_DATA_SCHEMA: self.model_meta['training_data_schema'],
            self.client.repository.ModelMetaNames.OUTPUT_DATA_SCHEMA: self.model_meta['output_data_schema'],
            self.client.repository.ModelMetaNames.EVALUATION_METHOD: self.model_meta['evaluation']['method'],
            self.client.repository.ModelMetaNames.EVALUATION_METRICS: self.model_meta['evaluation']['metrics'],
            self.client.repository.ModelMetaNames.TRAINING_DEFINITION_URL: self.definition_url,
            self.client.repository.ModelMetaNames.INPUT_DATA_SCHEMA: {'fields': [d for d in self.model_meta['training_data_schema']['fields'] if d.get('name') != self.model_meta['label_column']]}
        }

        print('XXX' + str(model_props))
        published_model = self.client.repository.store_model(model=self.model_path, meta_props=model_props)
        print("Model details: " + str(published_model))

        TestWMLClientWithSpark.model_uid = self.client.repository.get_model_uid(published_model)
        TestWMLClientWithSpark.logger.info("Published model ID:" + str(TestWMLClientWithSpark.model_uid))
        self.assertIsNotNone(TestWMLClientWithSpark.model_uid)

    def test_4_get_details(self):
        TestWMLClientWithSpark.logger.info("Get model details")
        details = self.client.repository.get_details(self.model_uid)
        TestWMLClientWithSpark.logger.debug("Model details: " + str(details))
        self.assertTrue(self.model_meta['name'] in str(details))

    def test_5_create_deployment(self):
        TestWMLClientWithSpark.logger.info("Create deployment")
        deployment = self.client.deployments.create(self.model_uid, 'best-drug model deployment')
        TestWMLClientWithSpark.logger.info("model_uid: " + self.model_uid)
        TestWMLClientWithSpark.logger.debug("Online deployment: " + str(deployment))
        TestWMLClientWithSpark.scoring_url = self.client.deployments.get_scoring_url(deployment)
        TestWMLClientWithSpark.deployment_uid = self.client.deployments.get_uid(deployment)
        self.assertTrue("online" in str(deployment))

    def test_6_get_deployment_details(self):
        TestWMLClientWithSpark.logger.info("Get deployment details")
        deployment_details = self.client.deployments.get_details()
        self.assertTrue('best-drug model deployment' in str(deployment_details))

    def test_6_score(self):
        TestWMLClientWithSpark.logger.info("Score the model")
        scoring_data = {
            "fields": ["AGE", "SEX", "BP", "CHOLESTEROL", "NA", "K"],
            "values": [[20.0, "F", "HIGH", "HIGH", 0.71, 0.07], [55.0, "M", "LOW", "HIGH", 0.71, 0.07]]
        }
        predictions = self.client.deployments.score(TestWMLClientWithSpark.scoring_url, scoring_data)
        self.assertTrue("predictedLabel" in str(predictions))

    def test_7_delete_deployment(self):
        TestWMLClientWithSpark.logger.info("Delete deployment")
        self.client.deployments.delete(TestWMLClientWithSpark.deployment_uid)

    def test_8_delete_model(self):
        TestWMLClientWithSpark.logger.info("Delete model")
        self.client.repository.delete(TestWMLClientWithSpark.model_uid)


if __name__ == '__main__':
    unittest.main()
