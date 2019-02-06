################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

from __future__ import print_function
import requests
from watson_machine_learning_client.utils import get_url, INSTANCE_DETAILS_TYPE, STR_TYPE, STR_TYPE_NAME, docstring_parameter, str_type_conv, is_python_2
from watson_machine_learning_client.metanames import ModelDefinitionMetaNames, ModelMetaNames, ExperimentMetaNames, FunctionMetaNames
from watson_machine_learning_client.wml_client_error import WMLClientError
from watson_machine_learning_client.wml_resource import WMLResource
from watson_machine_learning_client.models import Models
from watson_machine_learning_client.definitions import Definitions
from watson_machine_learning_client.experiments import Experiments
from watson_machine_learning_client.functions import Functions
from multiprocessing import Pool
from watson_machine_learning_client.libs.repository_v3.mlrepositoryclient import MLRepositoryClient

_DEFAULT_LIST_LENGTH = 50


class Repository(WMLResource):
    """
    Store and manage your models, definitions and experiments using Watson Machine Learning Repository.
    """
    DefinitionMetaNames = ModelDefinitionMetaNames()
    """MetaNames for definitions creation."""
    ModelMetaNames = ModelMetaNames()
    """MetaNames for models creation."""
    ExperimentMetaNames = ExperimentMetaNames()
    """MetaNames for experiments creation."""
    FunctionMetaNames = FunctionMetaNames()
    """
    
    MetaNames for python functions creation.
    """

    def __init__(self, client):
        WMLResource.__init__(self, __name__, client)
        if not client.ICP:
            Repository._validate_type(client.service_instance.details, u'instance_details', dict, True)
            Repository._validate_type_of_details(client.service_instance.details, INSTANCE_DETAILS_TYPE)
        self._ICP = client.ICP
        self._ml_repository_client = None
        self._refresh_repo_client() # regular token is initialized in service_instance

    def _refresh_repo_client(self):
        self._ml_repository_client = MLRepositoryClient(self._wml_credentials[u'url'])

        if self._ICP:
            self._repotoken = self._client._get_icptoken()
            self._ml_repository_token = self._repotoken.replace('Bearer', '')
            self._ml_repository_client.authorize_with_token(self._ml_repository_token)
        else:
            self._ml_repository_client.authorize(self._wml_credentials[u'username'], self._wml_credentials[u'password'])
            self._ml_repository_client._add_header('X-WML-User-Client', 'PythonClient')
            if self._client.project_id is not None:
                self._ml_repository_client._add_header('X-Watson-Project-ID', self._client.project_id)

    def store_experiment(self, meta_props):
        """
           Store experiment into Watson Machine Learning repository on IBM Cloud.

            :param meta_props: meta data of the experiment configuration. To see available meta names use:

               >>> client.repository.ExperimentMetaNames.get()
            :type meta_props: dict

            :returns: stored experiment details
            :rtype: dict

           A way you might use me is:

           >>> metadata = {
           >>>  client.repository.ExperimentMetaNames.NAME: 'my_experiment',
           >>>  client.repository.ExperimentMetaNames.EVALUATION_METRICS: ['accuracy'],
           >>>  client.repository.ExperimentMetaNames.TRAINING_DATA_REFERENCE: {'connection': {'endpoint_url': 'https://s3-api.us-geo.objectstorage.softlayer.net', 'access_key_id': '***', 'secret_access_key': '***'}, 'source': {'bucket': 'train-data'}, 'type': 's3'},
           >>>  client.repository.ExperimentMetaNames.TRAINING_RESULTS_REFERENCE: {'connection': {'endpoint_url': 'https://s3-api.us-geo.objectstorage.softlayer.net', 'access_key_id': '***', 'secret_access_key': '***'}, 'target': {'bucket': 'result-data'}, 'type': 's3'},
           >>>  client.repository.ExperimentMetaNames.TRAINING_REFERENCES: [
           >>>      {
           >>>        'training_definition_url': definition_url_1
           >>>      },
           >>>      {
           >>>        'training_definition_url': definition_url_2
           >>>      },
           >>>   ],
           >>> }
           >>> experiment_details = client.repository.store_experiment(meta_props=metadata)
           >>> experiment_url = client.repository.get_experiment_url(experiment_details)
        """
        if not self._ICP:
            return self._client.experiments._store(meta_props)
        else:
            return {}

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def store_definition(self, training_definition, meta_props):
        """
            Store training definition into Watson Machine Learning repository on IBM Cloud.

            :param training_definition:  path to zipped model_definition
            :type training_definition: {str_type}

            :param meta_props: meta data of the training definition. To see available meta names use:

               >>> client.repository.DefinitionMetaNames.get()
            :type meta_props: dict


            :returns: stored training definition details
            :rtype: dict

            A way you might use me is:

            >>> metadata = {
            >>>  client.repository.DefinitionMetaNames.NAME: 'my_training_definition',
            >>>  client.repository.DefinitionMetaNames.FRAMEWORK_NAME: 'tensorflow',
            >>>  client.repository.DefinitionMetaNames.FRAMEWORK_VERSION: '1.5',
            >>>  client.repository.DefinitionMetaNames.RUNTIME_NAME: 'python',
            >>>  client.repository.DefinitionMetaNames.RUNTIME_VERSION: '3.5',
            >>>  client.repository.DefinitionMetaNames.EXECUTION_COMMAND: 'python3 tensorflow_mnist_softmax.py --trainingIters 20'
            >>> }
            >>> definition_details = client.repository.store_definition(training_definition_filepath, meta_props=metadata)
            >>> definition_url = client.repository.get_definition_url(definition_details)
        """

        return self._client._definitions.store(training_definition, meta_props)

    @staticmethod
    def _meta_props_to_repository_v3_style(meta_props):
        if is_python_2():
            new_meta_props = meta_props.copy()

            for key in new_meta_props:
                if type(new_meta_props[key]) is unicode:
                    new_meta_props[key] = str(new_meta_props[key])

            return new_meta_props
        else:
            return meta_props

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def store_model(self, model, meta_props=None, training_data=None, training_target=None, pipeline=None):
        """
        Store trained model into Watson Machine Learning repository on Cloud.

        :param model:  Can be one of following:

            - The train model object:
                - scikit-learn
                - xgboost
                - spark (PipelineModel)
            - path to saved model in format:
                - keras (.tgz)
                - pmml (.xml)
                - scikit-learn (.tar.gz)
                - xgboost (.tar.gz)
                - tensorflow (.tar.gz)
                - spss (.str)
            - directory containing model file(s):
                - scikit-learn
                - xgboost
                - tensorflow
            - trained model guid
        :type model: object/{str_type}

        :param meta_props: meta data of the training definition. To see available meta names use:

            >>> client.repository.ModelMetaNames.get()

        :type meta_props: dict/{str_type}

        :param training_data:  Spark DataFrame supported for spark models. Pandas dataframe, numpy.ndarray or array supported for scikit-learn models
        :type training_data: spark dataframe, pandas dataframe, numpy.ndarray or array

        :param training_target: array with labels required for scikit-learn models
        :type training_target: array

        :param pipeline: pipeline required for spark mllib models
        :type training_target: object

        :returns: stored model details
        :rtype: dict

        The most simple use is:

        >>> stored_model_details = client.repository.store_model(model, name)

        In more complicated cases you should create proper metadata, similar to this one:

        >>> metadata = {
        >>>        client.repository.ModelMetaNames.NAME: 'customer satisfaction prediction model',
        >>>        client.repository.ModelMetaNames.FRAMEWORK_NAME: 'tensorflow',
        >>>        client.repository.ModelMetaNames.FRAMEWORK_VERSION: '1.5',
        >>>        client.repository.ModelMetaNames.RUNTIME_NAME: 'python',
        >>>        client.repository.ModelMetaNames.RUNTIME_VERSION: '3.5'
        >>>}

        where FRAMEWORK_NAME may be one of following: "spss-modeler", "tensorflow", "xgboost", "scikit-learn", "pmml".

        A way you might use me with local tar.gz containing model:

        >>> stored_model_details = client.repository.store_model(path_to_tar_gz, meta_props=metadata, training_data=None)

        A way you might use me with local directory containing model file(s):

        >>> stored_model_details = client.repository.store_model(path_to_model_directory, meta_props=metadata, training_data=None)

        A way you might use me with trained model guid:

        >>> stored_model_details = client.repository.store_model(trained_model_guid, meta_props=metadata, training_data=None)
        """
        return self._client._models.store(model, meta_props, training_data, training_target, pipeline)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def store_function(self, function, meta_props):
        """

            Store function into Watson Machine Learning repository on Cloud.

            As a 'function' may be used one of the following:
             - filepath to gz file
             - 'score' function reference, where the function is the function which will be deployed
             - generator function, which takes no argument or arguments which all have primitive python default values and as result return 'score' function

            :param meta_props: meta data or name of the function. To see available meta names use:

                >>> client.repository.FunctionMetaNames.get()

            :type meta_props: dict/{str_type}

            :param function: path to file with archived function content or function (as described above)
            :type function: {str_type} or function

            :returns: stored function details
            :rtype: dict

            The most simple use is (using `score` function):

                >>> def score(payload):
                        values = [[row[0]*row[1]] for row in payload['values']]
                        return {'fields': ['multiplication'], 'values': values}
                >>> stored_function_details = client.repository.store_function(score, name)

            Other, more interesting example is using generator function.
            In this situation it is possible to pass some variables:

                >>> wml_creds = {...}
                >>> def gen_function(wml_credentials=wml_creds, x=2):
                        def f(payload):
                            values = [[row[0]*row[1]*x] for row in payload['values']]
                            return {'fields': ['multiplication'], 'values': values}
                        return f
                >>> stored_function_details = client.repository.store_function(gen_function, name)

            In more complicated cases you should create proper metadata, similar to this one:

                >>> metadata = {
                >>>    client.repository.FunctionMetaNames.NAME: "function",
                >>>    client.repository.FunctionMetaNames.DESCRIPTION: "This is ai function",
                >>>    client.repository.FunctionMetaNames.RUNTIME_UID: "53dc4cf1-252f-424b-b52d-5cdd9814987f",
                >>>    client.repository.FunctionMetaNames.INPUT_DATA_SCHEMA: {"fields": [{"metadata": {}, "type": "string", "name": "GENDER", "nullable": True}]},
                >>>    client.repository.FunctionMetaNames.OUTPUT_DATA_SCHEMA: {"fields": [{"metadata": {}, "type": "string", "name": "GENDER", "nullable": True}]},
                >>>    client.repository.FunctionMetaNames.TAGS: [{"value": "ProjectA", "description": "Functions created for ProjectA"}]
                >>> }
                >>> stored_function_details = client.repository.store_function(score, metadata)
            """
        return self._client._functions.store(function, meta_props)

    def create_version(self, model, model_uid, meta_props = None):
        """
        Create a new version for a model.

        .. note::
            Model version creation is not allowed for spark models

        :param model:  Can be one of following:
            - path to saved model in format:
                - keras (.tgz)
                - pmml (.xml)
                - scikit-learn (.tar.gz)
                - xgboost (.tar.gz)
                - tensorflow (.tar.gz)
                - spss (.str)
            - trained model guid
        :type model: {str_type}

        :param meta_props: meta data of the model. To see available meta names use:

            >>> client.repository.ModelMetaNames.get()

        :type meta_props: dict/{str_type}

        :param model_uid:  model ID
        :type model_uid: {str_type}

        :returns: model version details
        :rtype: dict

        Example:

        >>> metadata = {
        >>>        client.repository.ModelMetaNames.NAME: 'SAMPLE NAME',
        >>>        client.repository.ModelMetaNames.DESCRIPTION: 'SAMPLE DESCRIPTION',
        >>>        client.repository.ModelMetaNames.AUTHOR_NAME: 'AUTHOR',
        >>>        client.repository.ModelMetaNames.FRAMEWORK_NAME: 'pmml',
        >>>        client.repository.ModelMetaNames.FRAMEWORK_VERSION: '4.3'
        >>>}

        A way you might use me with local tar.gz containing model:

        >>> stored_model_details = client.repository.create_version(path_to_tar_gz, model_uid="MODELID" ,meta_props=metadata)

        A way you might use me with trained model guid:

        >>> stored_model_details = client.repository.create_version(trained_model_guid, model_uid="MODELID" ,meta_props=metadata)
        """
        return self._client._models.store(model, meta_props, version=True, artifactid=model_uid)

    def update_model(self, model_uid, content_path=None, meta_props=None):
        """
            Update content of model with new one.

            :param model_uid:  Model UID
            :type model_uid: str
            :param content_path: path to tar.gz with new content of model
            :type content_path: str

            :returns: updated metadata of model
            :rtype: dict

            A way you might use me is:

            >>> model_details = client.repository.update_model_content(model_uid, content_path)
        """
        return self._client._models.update(model_uid, content_path, meta_props)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def update_experiment(self, experiment_uid, changes):
        """
        Updates existing experiment metadata.

        :param experiment_uid: UID of experiment which definition should be updated
        :type experiment_uid: {str_type}

        :param changes: elements which should be changed, where keys are ExperimentMetaNames
        :type changes: dict

        :return: metadata of updated experiment
        :rtype: dict
        """
        if not self._ICP:
            return self._client.experiments._update_experiment(experiment_uid, changes)
        else:
            return {}

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def update_function(self, function_uid, changes):
        """

        Updates existing function metadata.

        :param function_uid: UID of function which definition should be updated
        :type function_uid: {str_type}

        :param changes: elements which should be changed, where keys are FunctionMetaNames
        :type changes: dict

        :return: metadata of updated function
        :rtype: dict
        """
        return self._client._functions.update(function_uid, changes)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def load(self, artifact_uid):
        """
        Load model from repository to object in local environment.

        :param artifact_uid:  stored model UID
        :type artifact_uid: {str_type}

        :returns: trained model
        :rtype: object

        A way you might use me is:

        >>> model = client.repository.load(model_uid)
        """
        return self._client._models.load(artifact_uid)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def download(self, artifact_uid, filename='downloaded_artifact.tar.gz'):
        """
        Download artifact (model or function content) from repository to local file.

        :param artifact_uid: stored artifact UID
        :type artifact_uid: {str_type}

        :param filename: name of local file to create (optional)
        :type filename: {str_type}

        Side effect:
            save artifact to file.

        A way you might use me is:

        >>> client.repository.download(model_uid, 'my_model.tar.gz')
        """
        self._validate_type(artifact_uid, 'artifact_uid', STR_TYPE, True)
        self._validate_type(filename, 'filename', STR_TYPE, True)

        res = self._check_artifact_type(artifact_uid)

        if res['model'] is True:
            return self._client._models.download(artifact_uid, filename)
        elif res['function'] is True:
            return self._client._functions.download(artifact_uid, filename)
        elif res['library'] is True:
            return self._client.runtimes.download_library(artifact_uid, filename)
        elif res['runtime'] is True:
            return self._client.runtimes.download_configuration(artifact_uid, filename)
        else:
            raise WMLClientError('Unexpected type of artifact to download: {}'.format(res))

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def delete(self, artifact_uid):
        """
            Delete model, definition, experiment or function from repository.

            :param artifact_uid: stored model, definition, experiment or function UID
            :type artifact_uid: {str_type}

            A way you might use me is:

            >>> client.repository.delete(artifact_uid)
        """
        artifact_uid = str_type_conv(artifact_uid)
        Repository._validate_type(artifact_uid, u'artifact_uid', STR_TYPE, True)

        artifact_type = self._check_artifact_type(artifact_uid)
        self._logger.debug(u'Attempting deletion of artifact with type: \'{}\''.format(str(artifact_type)))

        if not self._ICP:
            if artifact_type[u'model'] is True:
                return self._client._models.delete(artifact_uid)
            elif artifact_type[u'definition'] is True:
                self._client._definitions.delete(artifact_uid)
                return

            elif artifact_type[u'experiment'] is True:
                experiment_endpoint = self._href_definitions.get_experiment_href(artifact_uid)
                self._logger.debug(u'Deletion artifact experiment endpoint: {}'.format(experiment_endpoint))
                response_delete = requests.delete(experiment_endpoint, headers=self._client._get_headers())

                self._handle_response(204, u'experiment deletion', response_delete, False)
                return

            elif artifact_type[u'function'] is True:
                return self._client._functions.delete(artifact_uid)

            elif artifact_type[u'runtime'] is True:
                self._client.runtimes.delete(artifact_uid)
                return

            elif artifact_type[u'library'] is True:
                self._client.runtimes.delete_library(artifact_uid)
                return

            elif artifact_type[u'deployment'] is True:
                deployment_endpoint = self._href_definitions.get_deployment_href(artifact_uid)
                self._logger.debug(u'Deletion artifact deployment endpoint: {}'.format(deployment_endpoint))
                dep_response_delete = requests.delete(deployment_endpoint, headers=self._client._get_headers())

                self._handle_response(204, u'deployment deletion', dep_response_delete, False)
                return

            else:
                raise WMLClientError(u'Artifact with artifact_uid: \'{}\' does not exist.'.format(artifact_uid))

        else:
            if artifact_type[u'model'] is True:
                return self._client._models.delete(artifact_uid)
            elif artifact_type[u'definition'] is True:
                self._client._definitions.delete(artifact_uid)
                return
            elif artifact_type[u'function'] is True:
                return self._client._functions.delete(artifact_uid)
            elif artifact_type[u'runtime'] is True:
                self._client.runtimes.delete(artifact_uid)
                return

            elif artifact_type[u'library'] is True:
                self._client.runtimes.delete_library(artifact_uid)
                return

            elif artifact_type[u'deployment'] is True:
                deployment_endpoint = self._href_definitions.get_deployment_href(artifact_uid)
                self._logger.debug(u'Deletion artifact deployment endpoint: {}'.format(deployment_endpoint))
                dep_response_delete = requests.delete(deployment_endpoint, headers=self._client._get_headers(), verify=False)

                self._handle_response(204, u'deployment deletion', dep_response_delete, False)
                return

            else:
                raise WMLClientError(u'Artifact with artifact_uid: \'{}\' does not exist.'.format(artifact_uid))

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def delete_definition(self, artifact_uid):
        """
            Delete definition from repository.

            :param artifact_uid: stored definition UID
            :type artifact_uid: {str_type}

            A way you might use me is:

            >>> client.repository.delete_definition(artifact_uid)
        """

        self.delete(artifact_uid)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def delete_experiment(self, artifact_uid):
        """
            Delete experiment definition from repository.

            :param artifact_uid: stored experiment UID
            :type artifact_uid: {str_type}

            A way you might use me is:

            >>> client.repository.delete_experiment(artifact_uid)
        """
        if not self._ICP:
            self.delete(artifact_uid)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def delete_function(self, artifact_uid):
        """

            Delete function from repository.

            :param artifact_uid: stored function UID
            :type artifact_uid: {str_type}

            A way you might use me is:

            >>> client.repository.delete_function(artifact_uid)
        """
        self.delete(artifact_uid)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_details(self, artifact_uid=None):
        """
           Get metadata of stored artifacts. If uid is not specified returns all models, definitions, experiment, functions, libraries and runtimes metadata.

           :param artifact_uid:  stored model, definition, experiment, function, library or runtime UID (optional)
           :type artifact_uid: {str_type}

           :returns: stored artifacts metadata
           :rtype: dict

           A way you might use me is:

           >>> details = client.repository.get_details(artifact_uid)
           >>> details = client.repository.get_details()
        """
        artifact_uid = str_type_conv(artifact_uid)
        Repository._validate_type(artifact_uid, u'artifact_uid', STR_TYPE, False)

        if not self._ICP:
            if artifact_uid is None:
                model_details = self._client._models.get_details()
                definition_details = self._client._definitions.get_details()
                experiment_details = self.get_experiment_details()
                library_details = self._client.runtimes.get_library_details()
                runtime_details = self._client.runtimes.get_details()
                function_details = self._client._functions.get_details()
                deployment_details = self._client.deployments.get_details()

                details = {
                    u'models': model_details,
                    u'definitions': definition_details,
                    u'experiments': experiment_details,
                    u'runtimes': runtime_details,
                    u'libraries': library_details,
                    u'deployments': deployment_details
                }
                if function_details is not None:
                    details[u'functions'] = function_details
            else:
                uid_type = self._check_artifact_type(artifact_uid)
                if uid_type[u'model'] is True:
                    details = self._client._models.get_details(artifact_uid)
                elif uid_type[u'definition'] is True:
                    details = self._client._definitions.get_details(artifact_uid)
                elif uid_type[u'experiment'] is True:
                    details = self.get_experiment_details(artifact_uid)
                elif uid_type[u'function'] is True:
                    details = self._client._functions.get_details(artifact_uid)
                elif uid_type[u'runtime'] is True:
                    details = self._client.runtimes.get_details(artifact_uid)
                elif uid_type[u'library'] is True:
                    details = self._client.runtimes.get_library_details(artifact_uid)
                elif uid_type[u'deployment'] is True:
                    details = self._client.deployments.get_details(artifact_uid)
                else:
                    raise WMLClientError(u'Getting artifact details failed. Artifact uid: \'{}\' not found.'.format(artifact_uid))

            return details

        else:
            if artifact_uid is None:
                model_details = self._client._models.get_details()
                definition_details = self._client._definitions.get_details()
                library_details = self._client.runtimes.get_library_details()
                runtime_details = self._client.runtimes.get_details()
                function_details = self._client._functions.get_details()
                deployment_details = self._client.deployments.get_details()

                details = {
                    u'models': model_details,
                    u'definitions': definition_details,
                    # u'experiments': experiment_details,
                    u'runtimes': runtime_details,
                    u'libraries': library_details,
                    u'deployments': deployment_details
                }
                if function_details is not None:
                    details[u'functions'] = function_details

            else:
                uid_type = self._check_artifact_type(artifact_uid)
                if uid_type[u'model'] is True:
                    details = self._client._models.get_details(artifact_uid)
                elif uid_type[u'definition'] is True:
                    details = self._client._definitions.get_details(artifact_uid)
                # elif uid_type[u'experiment'] is True:
                #   details = self.get_experiment_details(artifact_uid)
                elif uid_type[u'function'] is True:
                    details = self._client._functions.get_details(artifact_uid)
                elif uid_type[u'runtime'] is True:
                    details = self._client.runtimes.get_details(artifact_uid)
                elif uid_type[u'library'] is True:
                    details = self._client.runtimes.get_library_details(artifact_uid)
                elif uid_type[u'deployment'] is True:
                    details = self._client.deployments.get_details(artifact_uid)
                else:
                    raise WMLClientError(u'Getting artifact details failed. Artifact uid: \'{}\' not found.'.format(artifact_uid))

            return details


    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_model_details(self, model_uid=None, limit=None):
        """
           Get metadata of stored models. If model uid is not specified returns all models metadata.

           :param model_uid: stored model, definition or pipeline UID (optional)
           :type model_uid: {str_type}

           :param limit: limit number of fetched records (optional)
           :type limit: int

           :returns: stored model(s) metadata
           :rtype: dict

           A way you might use me is:

           >>> model_details = client.repository.get_model_details(model_uid)
           >>> models_details = client.repository.get_model_details()
        """
        return self._client._models.get_details(model_uid, limit)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_definition_details(self, definition_uid=None, limit=None):
        """
            Get metadata of stored definitions. If definition uid is not specified returns all model definitions metadata.

            :param definition_uid:  stored model definition UID (optional)
            :type definition_uid: {str_type}

            :param limit: limit number of fetched records (optional)
            :type limit: int

            :returns: stored definition(s) metadata
            :rtype: dict

            A way you might use me is:

            >>> definition_details = client.repository.get_definition_details(definition_uid)
            >>> definition_details = client.repository.get_definition_details()
         """
        return self._client._definitions.get_details(definition_uid, limit)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_experiment_details(self, experiment_uid=None, limit=None):
        """
            Get metadata of stored experiments. If no experiment uid is specified all experiments metadata is returned.

            :param experiment_uid: stored experiment UID (optional)
            :type experiment_uid: {str_type}

            :param limit: limit number of fetched records (optional)
            :type limit: int

            :returns: stored experiment(s) metadata
            :rtype: dict

            A way you might use me is:

            >>> experiment_details = client.repository.get_experiment_details(experiment_uid)
            >>> experiment_details = client.repository.get_experiment_details()
         """
        if not self._ICP:
            experiment_uid = str_type_conv(experiment_uid)
            Repository._validate_type(experiment_uid, u'experiment_uid', STR_TYPE, False)
            Repository._validate_type(limit, u'limit', int, False)

            url = self._href_definitions.get_experiments_href()

            return self._get_artifact_details(url, experiment_uid, limit, 'experiments')
        else:
            return {}

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_function_details(self, function_uid=None, limit=None):
        """

            Get metadata of function. If no function uid is specified all functions metadata is returned.

            :param function_uid: stored function UID (optional)
            :type function_uid: {str_type}

            :param limit: limit number of fetched records (optional)
            :type limit: int

            :returns: stored function(s) metadata
            :rtype: dict

            A way you might use me is:

            >>> function_details = client.repository.get_function_details(function_uid)
            >>> function_details = client.repository.get_function_details()
         """
        return self._client._functions.get_details(function_uid, limit)

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_model_url(model_details):
        """
            Get url of stored model.

            :param model_details:  stored model details
            :type model_details: dict

            :returns: url to stored model
            :rtype: {str_type}

            A way you might use me is:

            >>> model_url = client.repository.get_model_url(model_details)
        """
        return Models.get_url(model_details)

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_model_uid(model_details):
        """
            Get uid of stored model.

            :param model_details:  stored model details
            :type model_details: dict

            :returns: uid of stored model
            :rtype: {str_type}

            A way you might use me is:

            >>> model_uid = client.repository.get_model_uid(model_details)
        """
        return Models.get_uid(model_details)

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_definition_url(definition_details):
        """
            Get url of stored definition.

            :param definition_details:  stored definition details
            :type definition_details: dict

            :returns: url of stored definition
            :rtype: {str_type}

            A way you might use me is:

            >>> definition_url = client.repository.get_definition_url(definition_details)
        """
        return Definitions.get_url(definition_details)

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def _get_definition_version_url(definition_details):
        """
            Get url of stored definition version.

            :param definition_details:  stored definition details
            :type definition_details: dict

            :returns: url of stored definition version
            :rtype: {str_type}

            A way you might use me is:

            >>> definition_version_url = client.repository.get_definition_version_url(definition_details)
        """
        return Definitions.get_version_url(definition_details)

    @staticmethod
    def get_definition_uid(definition_details):
        """
            Get uid of stored definition.

            :param definition_details: stored definition details
            :type definition_details: dict

            :returns: uid of stored model
            :rtype: str

            A way you might use me is:

            >>> definition_uid = client.repository.get_definition_uid(definition_details)
        """
        return Definitions.get_uid(definition_details)

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_experiment_uid(experiment_details):
        """
            Get uid of stored experiment.

            :param experiment_details: stored experiment details
            :type experiment_details: dict

            :returns: uid of stored experiment
            :rtype: {str_type}

            A way you might use me is:

            >>> experiment_uid = client.repository.get_experiment_uid(experiment_details)
        """
        return Experiments._get_uid(experiment_details)

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_experiment_url(experiment_details):
        """
            Get url of stored experiment.

            :param experiment_details:  stored experiment details
            :type experiment_details: dict

            :returns: url of stored experiment
            :rtype: {str_type}

            A way you might use me is:

            >>> experiment_url = client.repository.get_experiment_url(experiment_details)
        """
        return Experiments._get_url(experiment_details)

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_function_uid(function_details):
        """

            Get uid of stored function.

            :param function_details:  stored function details
            :type function_details: dict

            :returns: uid of stored function
            :rtype: {str_type}

            A way you might use me is:

            >>> function_uid = client.repository.get_function_uid(function_details)
        """
        return Functions.get_uid(function_details)

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_function_url(function_details):
        """

            Get url of stored function.

            :param function_details:  stored function details
            :type function_details: dict

            :returns: url of stored function
            :rtype: {str_type}

            A way you might use me is:

            >>> function_url = client.repository.get_function_url(function_details)
        """
        return Functions.get_url(function_details)

    def list(self):
        """
           List stored models, definitions and experiments. Only first 50 records is shown. For more result use specific list functions.

           A way you might use me is:

           >>> client.repository.list()
        """
        from tabulate import tabulate

        headers = self._client._get_headers()
        params = {u'limit': 1000} # TODO - should be unlimited, if results not sorted

        pool = Pool(processes=4)

        if not self._ICP:
            endpoints = {
                u'model': self._client.service_instance.details.get(u'entity').get(u'published_models').get(u'url'),
                u'definition': self._href_definitions.get_definitions_href(),
                u'experiment': self._href_definitions.get_experiments_href(),
                u'function': self._href_definitions.get_functions_href(),
                u'runtime': self._href_definitions.get_runtimes_href(),
                u'library': self._href_definitions.get_custom_libraries_href(),
                u'deployment': self._href_definitions.get_deployments_href()
            }
            isIcp = self._ICP

            artifact_get = {artifact: pool.apply_async(get_url, (endpoints[artifact], headers, params, isIcp)) for artifact in endpoints}
            resources = {artifact: [] for artifact in endpoints}

            for artifact in endpoints:
                try:
                    response = artifact_get[artifact].get()
                    response_text = self._handle_response(200, u'getting all {}s'.format(artifact), response)
                    resources[artifact] = response_text[u'resources']
                except Exception as e:
                    self._logger.error(e)

            pool.close()

            model_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at'], m[u'entity'][u'model_type'], u'model') for m in resources[u'model']]
            experiment_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'settings'][u'name'], m['metadata']['created_at'], u'-', u'experiment') for m in resources[u'experiment']]
            definition_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at'], m[u'entity'][u'framework'][u'name'], u'definition') for m in resources[u'definition']]
            function_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at'], u'-', m[u'entity'][u'type'] + u' function') for m in resources[u'function']]
            runtime_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at'], u'-', m[u'entity'][u'platform'][u'name'] + u' runtime') for m in resources[u'runtime']]
            library_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at'], u'-', m[u'entity'][u'platform'][u'name'] + u' library') for m in resources[u'library']]
            deployment_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at'], m[u'entity'][u'model_type'], m[u'entity'][u'type'] + u' deployment') for m in resources[u'deployment']]

            values = list(set(model_values + definition_values + experiment_values + function_values + runtime_values + library_values + deployment_values))
            values = sorted(sorted(values, key=lambda x: x[2], reverse=True), key=lambda x: x[4])
            # TODO add intelligent sorting
            table = tabulate([[u'GUID', u'NAME', u'CREATED', u'FRAMEWORK', u'TYPE']] + values[:_DEFAULT_LIST_LENGTH])
            print(table)
            if len(values) > _DEFAULT_LIST_LENGTH:
                print('Note: Only first {} records were displayed. To display more use more specific list functions.'.format(_DEFAULT_LIST_LENGTH))
        else:
            endpoints = {
                #u'model': self._client.service_instance.details.get(u'entity').get(u'published_models').get(u'url'),
                u'model': self._href_definitions.get_published_models_href(),
                u'definition': self._href_definitions.get_definitions_href(),
                # u'experiment': self._href_definitions.get_experiments_href(),
                u'function': self._href_definitions.get_functions_href(),
                u'runtime': self._href_definitions.get_runtimes_href(),
                u'library': self._href_definitions.get_custom_libraries_href(),
                u'deployment': self._href_definitions.get_deployments_href()
            }
            isIcp = self._ICP
            artifact_get = {artifact: pool.apply_async(get_url, (endpoints[artifact], headers, params, isIcp)) for artifact in endpoints}
            resources = {artifact: [] for artifact in endpoints}

            for artifact in endpoints:
                try:
                    response = artifact_get[artifact].get()
                    response_text = self._handle_response(200, u'getting all {}s'.format(artifact), response)
                    resources[artifact] = response_text[u'resources']
                except Exception as e:
                    self._logger.error(e)

            pool.close()

            model_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at'], m[u'entity'][u'model_type'], u'model') for m in resources[u'model']]
            #experiment_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'settings'][u'name'], m['metadata']['created_at'], u'-', u'experiment') for m in resources[u'experiment']]
            definition_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at'], m[u'entity'][u'framework'][u'name'], u'definition') for m in resources[u'definition']]
            function_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at'], u'-', m[u'entity'][u'type'] + u' function') for m in resources[u'function']]
            runtime_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at'], u'-', m[u'entity'][u'platform'][u'name'] + u' runtime') for m in resources[u'runtime']]
            library_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at'], u'-', m[u'entity'][u'platform'][u'name'] + u' library') for m in resources[u'library']]
            deployment_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at'], m[u'entity'][u'model_type'], m[u'entity'][u'type'] + u' deployment') for m in resources[u'deployment']]

            #values = list(set(model_values + definition_values + experiment_values + function_values + runtime_values + library_values))
            values = list(set(model_values + definition_values + function_values + runtime_values + library_values + deployment_values))
            values = sorted(sorted(values, key=lambda x: x[2], reverse=True), key=lambda x: x[4])
            # TODO add intelligent sorting
            table = tabulate([[u'GUID', u'NAME', u'CREATED', u'FRAMEWORK', u'TYPE']] + values[:_DEFAULT_LIST_LENGTH])
            print(table)
            if len(values) > _DEFAULT_LIST_LENGTH:
                print('Note: Only first {} records were displayed. To display more use more specific list functions.'.format(_DEFAULT_LIST_LENGTH))

    def list_models(self, limit=None):
        """
           List stored models. If limit is set to None there will be only first 50 records shown.

           :param limit: limit number of fetched records (optional)
           :type limit: int

           A way you might use me is

           >>> client.repository.list_models()
        """

        self._client._models.list(limit=limit)

    def list_experiments(self, limit=None):
        """
           List stored experiments. If limit is set to None there will be only first 50 records shown.

           :param limit: limit number of fetched records (optional)
           :type limit: int

           A way you might use me is

           >>> client.repository.list_experiments()
        """
        if not self._ICP:
            experiment_resources = self.get_experiment_details(limit=limit)[u'resources']
            experiment_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'settings'][u'name'], m[u'metadata'][u'created_at']) for m in experiment_resources]

            self._list(experiment_values, [u'GUID', u'NAME', u'CREATED'], limit, _DEFAULT_LIST_LENGTH)
        else:
            return {}

    def list_definitions(self, limit=None):
        """
           List stored definitions. If limit is set to None there will be only first 50 records shown.

           :param limit: limit number of fetched records (optional)
           :type limit: int

           A way you might use me is

           >>> client.repository.list_definitions()
        """
        self._client._definitions.list(limit=limit)

    def list_functions(self, limit=None):
        """

            List stored functions. If limit is set to None there will be only first 50 records shown.

            :param limit: limit number of fetched records (optional)
            :type limit: int

            A way you might use me is

            >>> client.repository.list_functions()
        """
        self._client._functions.list(limit=limit)

    def _check_artifact_type(self, artifact_uid):
        artifact_uid = str_type_conv(artifact_uid)
        Repository._validate_type(artifact_uid, u'artifact_uid', STR_TYPE, True)

        def _artifact_exists(response):
            return (response is not None) and (u'status_code' in dir(response)) and (response.status_code == 200)

        pool = Pool(processes=4)
        headers = self._client._get_headers()

        if not self._ICP:
            endpoints = {
                u'definition': self._href_definitions.get_definition_href(artifact_uid),
                u'model': self._client.service_instance.details.get(u'entity').get(u'published_models').get(u'url') + u'/' + artifact_uid,
                u'experiment': self._href_definitions.get_experiment_href(artifact_uid),
                u'function': self._href_definitions.get_function_href(artifact_uid),
                u'runtime': self._href_definitions.get_runtime_href(artifact_uid),
                u'library': self._href_definitions.get_custom_library_href(artifact_uid),
                u'deployment': self._href_definitions.get_deployment_href(artifact_uid)
            }
            isIcp = self._ICP
            future = {artifact: pool.apply_async(get_url, (endpoints[artifact], headers, None, isIcp)) for artifact in endpoints}
            response_get = {artifact: None for artifact in endpoints}

            for artifact in endpoints:
                try:
                    response_get[artifact] = future[artifact].get()
                    self._logger.debug(u'Response({})[{}]: {}'.format(endpoints[artifact], response_get[artifact].status_code, response_get[artifact].text))
                except Exception as e:
                    self._logger.debug(u'Error during checking artifact type: ' + str(e))

            pool.close()

            artifact_type = {artifact: _artifact_exists(response_get[artifact]) for artifact in response_get}

            return artifact_type

        else:
            endpoints = {
                u'definition': self._href_definitions.get_definition_href(artifact_uid),
                #u'model': self._client.service_instance.details.get(u'entity').get(u'published_models').get(u'url') + u'/' + artifact_uid,
                u'model': self._href_definitions.get_published_models_href() + u'/' + artifact_uid,
                # u'experiment': self._href_definitions.get_experiment_href(artifact_uid),
                u'function': self._href_definitions.get_function_href(artifact_uid),
                u'runtime': self._href_definitions.get_runtime_href(artifact_uid),
                u'library': self._href_definitions.get_custom_library_href(artifact_uid)
            }
            isIcp = self._ICP
            #future = {artifact: pool.apply_async(get_url, (endpoints[artifact], headers)) for artifact in endpoints}
            #response_get = {artifact: None for artifact in endpoints}
            response_get = {artifact: get_url(endpoints[artifact], headers, None, isIcp) for artifact in endpoints}

            #for artifact in endpoints:
            #    try:
            #        response_get[artifact] = future[artifact].get()
            #        self._logger.debug(u'Response({})[{}]: {}'.format(endpoints[artifact], response_get[artifact].status_code, response_get[artifact].text))
            #    except Exception as e:
            #        self._logger.debug(u'Error during checking artifact type: ' + str(e))

            pool.close()

            artifact_type = {artifact: _artifact_exists(response_get[artifact]) for artifact in response_get}

            return artifact_type



