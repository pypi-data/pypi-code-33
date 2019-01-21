# coding: utf-8

# flake8: noqa

"""
    Endpoints

    Endpoints API for different services in SKIL  # noqa: E501

    OpenAPI spec version: 1.2.0-rc1
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import

# import apis into sdk package
from skil_client.api.default_api import DefaultApi

# import ApiClient
from skil_client.api_client import ApiClient
from skil_client.configuration import Configuration
# import models into sdk package
from skil_client.models.accumulated_results import AccumulatedResults
from skil_client.models.add_credentials_request import AddCredentialsRequest
from skil_client.models.add_example_request import AddExampleRequest
from skil_client.models.add_model_history_request import AddModelHistoryRequest
from skil_client.models.add_resource_request import AddResourceRequest
from skil_client.models.aggregate_prediction import AggregatePrediction
from skil_client.models.auth_policy import AuthPolicy
from skil_client.models.azure_storage_resource_details import AzureStorageResourceDetails
from skil_client.models.base64_nd_array_body import Base64NDArrayBody
from skil_client.models.base64_nd_array_body_knn import Base64NDArrayBodyKNN
from skil_client.models.batch_csv_record import BatchCSVRecord
from skil_client.models.batch_image_record import BatchImageRecord
from skil_client.models.best_model import BestModel
from skil_client.models.change_password_request import ChangePasswordRequest
from skil_client.models.classification_result import ClassificationResult
from skil_client.models.create_deployment_request import CreateDeploymentRequest
from skil_client.models.create_job_request import CreateJobRequest
from skil_client.models.data_proc_resource_details import DataProcResourceDetails
from skil_client.models.deployment_objects import DeploymentObjects
from skil_client.models.deployment_response import DeploymentResponse
from skil_client.models.detected_object import DetectedObject
from skil_client.models.detection_result import DetectionResult
from skil_client.models.download_output_file_request import DownloadOutputFileRequest
from skil_client.models.emr_resource_details import EMRResourceDetails
from skil_client.models.evaluation_results_entity import EvaluationResultsEntity
from skil_client.models.example_entity import ExampleEntity
from skil_client.models.experiment_entity import ExperimentEntity
from skil_client.models.feedback_response import FeedbackResponse
from skil_client.models.file_upload import FileUpload
from skil_client.models.file_upload_list import FileUploadList
from skil_client.models.google_storage_resource_details import GoogleStorageResourceDetails
from skil_client.models.hdfs_resource_details import HDFSResourceDetails
from skil_client.models.hd_insight_resource_details import HDInsightResourceDetails
from skil_client.models.ind_array import INDArray
from skil_client.models.image_transform_process import ImageTransformProcess
from skil_client.models.import_model_request import ImportModelRequest
from skil_client.models.inline_response200 import InlineResponse200
from skil_client.models.job_entity import JobEntity
from skil_client.models.json_array_response import JsonArrayResponse
from skil_client.models.log_batch import LogBatch
from skil_client.models.log_request import LogRequest
from skil_client.models.login_request import LoginRequest
from skil_client.models.login_response import LoginResponse
from skil_client.models.meta_data import MetaData
from skil_client.models.minibatch_entity import MinibatchEntity
from skil_client.models.model_entity import ModelEntity
from skil_client.models.model_feed_back_request import ModelFeedBackRequest
from skil_client.models.model_history_entity import ModelHistoryEntity
from skil_client.models.model_instance_entity import ModelInstanceEntity
from skil_client.models.model_response import ModelResponse
from skil_client.models.model_status import ModelStatus
from skil_client.models.multi_class_classification_result import MultiClassClassificationResult
from skil_client.models.multi_predict_request import MultiPredictRequest
from skil_client.models.multi_predict_response import MultiPredictResponse
from skil_client.models.nearest_neighbor_request import NearestNeighborRequest
from skil_client.models.nearest_neighbors_result import NearestNeighborsResult
from skil_client.models.nearest_neighbors_results import NearestNeighborsResults
from skil_client.models.new_deployment import NewDeployment
from skil_client.models.prediction import Prediction
from skil_client.models.resource import Resource
from skil_client.models.resource_credentials import ResourceCredentials
from skil_client.models.resource_group import ResourceGroup
from skil_client.models.retraining_status import RetrainingStatus
from skil_client.models.revisions_written import RevisionsWritten
from skil_client.models.role import Role
from skil_client.models.rollback_status import RollbackStatus
from skil_client.models.s3_resource_details import S3ResourceDetails
from skil_client.models.set_state import SetState
from skil_client.models.single_csv_record import SingleCSVRecord
from skil_client.models.single_image_record import SingleImageRecord
from skil_client.models.token import Token
from skil_client.models.token_generate_request import TokenGenerateRequest
from skil_client.models.transform_process import TransformProcess
from skil_client.models.update_best_model import UpdateBestModel
from skil_client.models.user import User
from skil_client.models.yarn_resource_details import YARNResourceDetails
