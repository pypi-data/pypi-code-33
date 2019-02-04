################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

from __future__ import print_function
from repository_v3.mlrepositoryartifact import MLRepositoryArtifact
from repository_v3.mlrepository import MetaProps, MetaNames
import requests
from watson_machine_learning_client.utils import MODEL_DETAILS_TYPE, INSTANCE_DETAILS_TYPE, load_model_from_directory, STR_TYPE, STR_TYPE_NAME, docstring_parameter, meta_props_str_conv, str_type_conv
from watson_machine_learning_client.metanames import ModelMetaNames
import os
import copy
import json
from watson_machine_learning_client.wml_client_error import WMLClientError
from watson_machine_learning_client.wml_resource import WMLResource
import re

_DEFAULT_LIST_LENGTH = 50


class Models(WMLResource):
    """
    Store and manage your models.
    """
    ConfigurationMetaNames = ModelMetaNames()
    """MetaNames for models creation."""

    def __init__(self, client):
        WMLResource.__init__(self, __name__, client)
        if not client.ICP:
            Models._validate_type(client.service_instance.details, u'instance_details', dict, True)
            Models._validate_type_of_details(client.service_instance.details, INSTANCE_DETAILS_TYPE)
        self._ICP = client.ICP

    def _publish_from_object(self, model, meta_props, training_data=None, training_target=None, pipeline=None):
        """
        Store model from object in memory into Watson Machine Learning repository on Cloud
        """
        self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.NAME, STR_TYPE, True)

        try:
            meta_data = MetaProps(self._client.repository._meta_props_to_repository_v3_style(meta_props))

            if 'pyspark.ml.pipeline.PipelineModel' in str(type(model)):
                pipeline_artifact = MLRepositoryArtifact(pipeline, name=str(meta_props[self.ConfigurationMetaNames.NAME]))
                model_artifact = MLRepositoryArtifact(model, name=str(meta_props[self.ConfigurationMetaNames.NAME]), meta_props=meta_data, training_data=training_data, pipeline_artifact=pipeline_artifact)
            else:
                model_artifact = MLRepositoryArtifact(model, name=str(meta_props[self.ConfigurationMetaNames.NAME]), meta_props=meta_data, training_data=training_data, training_target=training_target)

            saved_model = self._client.repository._ml_repository_client.models.save(model_artifact)
        except Exception as e:
            raise WMLClientError(u'Publishing model failed.', e)
        else:
            return self.get_details(u'{}'.format(saved_model.uid))

    def _publish_from_training(self, model_uid, meta_props, training_data=None, training_target=None,version=False,artifactId=None):
        """
        Store trained model from object storage into Watson Machine Learning repository on IBM Cloud
        """
        self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.NAME, STR_TYPE, True)

        if not self._ICP:
            details_response = requests.get(
                self._href_definitions.get_repo_model_href(model_uid),
                headers=self._client._get_headers()
            )
        else:
            details_response = requests.get(
                self._href_definitions.get_repo_model_href(model_uid),
                headers=self._client._get_headers(),
                verify=False
            )
        details = self._handle_response(200, u'getting trained model details', details_response)

        if not self._ICP:
            definition_details_response = requests.get(
                details['entity']['model_definition']['definition_href'],
                headers=self._client._get_headers()
            )
        else:
            definition_details_response = requests.get(
                details['entity']['model_definition']['definition_href'],
                headers=self._client._get_headers(),
                verify=False
            )

        definition_details = self._handle_response(200, u'getting training definition details', definition_details_response)

        model_definition = details['entity']['model_definition']
        secret_access_key = details['entity']['training_results_reference']['connection']['secret_access_key']
        access_key_id = details['entity']['training_results_reference']['connection']['access_key_id']
        endpoint_url = details['entity']['training_results_reference']['connection']['endpoint_url']
        bucket_name = details['entity']['training_results_reference']['location']['bucket']

        if re.match('^model-[0-9a-zA-Z_-]{8}$', model_uid) or re.match('^training-[0-9a-zA-Z_-]{9}$', model_uid)is not None:
            prefix = model_uid
        else:
            res = re.search('^(model-[0-9a-zA-Z_-]{8})_([0-9]+)$', model_uid)
            if res is not None:
                prefix = res.group(1) + '/learner-1/' + res.group(2)
            else:
                res_training = re.search('^(training-[0-9a-zA-Z_-]{9})_([0-9]+)$', model_uid)
                if res_training is not None:
                    prefix = res_training.group(1) + '/learner-1/' + res_training.group(2)
                else:
                    raise WMLClientError('Trained model uid is in invalid format: {}.'.format(model_uid))

        model_meta = self.ConfigurationMetaNames._generate_resource_metadata(
            meta_props,
            client=self._client,
            initial_metadata=model_definition
        )

        model_meta['content_location'] = {
            "connection": {
                "access_key_id": access_key_id,
                "secret_access_key": secret_access_key,
                "endpoint_url": endpoint_url
            },
            "source": {
                "bucket": bucket_name,
                "path": prefix
            },
            "type": "s3"
        }

        if 'training_data_reference' not in model_meta:
            model_meta['training_data_reference'] = [{
                "name": "data_reference",
                "connection": details['entity']['training_data_reference']['connection'],
                "source": {
                    "bucket": details['entity']['training_data_reference']['location']['bucket']
                },
                "type": "s3"
            }]

        if 'training_definition_url' not in model_meta:
            model_meta['training_definition_url'] = definition_details['entity']['training_definition_version']['url']

        if version==True:
            Models._validate_type(str_type_conv(artifactId), 'model_uid', STR_TYPE, True)

            if not self._ICP:
                creation_response = requests.post(
                   self._wml_credentials['url'] + '/v3/ml_assets/models/'+str_type_conv(artifactId),
                   headers=self._client._get_headers(),
                   json=model_meta
                )
            else:
                creation_response = requests.post(
                    self._wml_credentials['url'] + '/v3/ml_assets/models/'+str_type_conv(artifactId),
                    headers=self._client._get_headers(),
                    json=model_meta,
                    verify=False
                )

            model_details = self._handle_response(202, u'creating new model version', creation_response)
            model_uid = model_details['metadata']['guid']
            return self._client.repository.get_details(artifactId+ "/versions/"+model_uid)
        else:
            if not self._ICP:
                creation_response = requests.post(
                       self._wml_credentials['url'] + '/v3/ml_assets/models',
                       headers=self._client._get_headers(),
                       json=model_meta
                )
            else:
                creation_response = requests.post(
                    self._wml_credentials['url'] + '/v3/ml_assets/models',
                    headers=self._client._get_headers(),
                    json=model_meta,
                    verify=False
                )
            model_details = self._handle_response(202, u'creating new model', creation_response)
            model_uid = model_details['metadata']['guid']
            return self.get_details(model_uid)

    def _publish_from_file(self, model, meta_props=None, training_data=None, training_target=None,ver=False,artifactid=None):
        """
        Store saved model into Watson Machine Learning repository on IBM Cloud
        """
        if(ver==True):
            #check if artifactid is passed
            Models._validate_type(str_type_conv(artifactid), 'model_uid', STR_TYPE, True)
            return self._publish_from_archive(model, meta_props,version=ver,artifactid=artifactid)
        def is_xml(model_filepath):
            return os.path.splitext(os.path.basename(model_filepath))[-1] == '.xml'

        self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.NAME, STR_TYPE, True)
        self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.FRAMEWORK_NAME, STR_TYPE, True)

        import tarfile
        import zipfile

        model_filepath = model
        if os.path.isdir(model):
            # TODO this part is ugly, but will work. In final solution this will be removed
            if meta_props[self.ConfigurationMetaNames.FRAMEWORK_NAME] == u'tensorflow':
                # TODO currently tar.gz is required for tensorflow - the same ext should be supported for all frameworks
                if os.path.basename(model) == '':
                    model = os.path.dirname(model)
                filename = os.path.basename(model) + '.tar.gz'
                current_dir = os.getcwd()
                os.chdir(model)
                target_path = os.path.dirname(model)

                with tarfile.open(os.path.join('..', filename), mode='w:gz') as tar:
                    tar.add('.')

                os.chdir(current_dir)
                model_filepath = os.path.join(target_path, filename)
                if tarfile.is_tarfile(model_filepath) or zipfile.is_zipfile(model_filepath) or is_xml(model_filepath):
                    try:
                        model_artifact = MLRepositoryArtifact(str(model_filepath), name=str(meta_props[self.ConfigurationMetaNames.NAME]),
                                                              meta_props=MetaProps(self._client.repository._meta_props_to_repository_v3_style(meta_props)))
                        saved_model = self._client.repository._ml_repository_client.models.save(model_artifact)
                    except Exception as e:
                        raise WMLClientError(u'Publishing model failed.', e)
                    else:
                        return self.get_details(saved_model.uid)
            else:
                self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.FRAMEWORK_NAME, STR_TYPE, True)

                loaded_model = load_model_from_directory(meta_props[self.ConfigurationMetaNames.FRAMEWORK_NAME], model)

                saved_model = self._publish_from_object(loaded_model, meta_props, training_data, training_target)

                return saved_model

        elif is_xml(model_filepath):
            try:
                model_artifact = MLRepositoryArtifact(str(model_filepath), name=str(meta_props[self.ConfigurationMetaNames.NAME]), meta_props=MetaProps(self._client.repository._meta_props_to_repository_v3_style(meta_props)))
                saved_model = self._client.repository._ml_repository_client.models.save(model_artifact)
            except Exception as e:
                raise WMLClientError(u'Publishing model failed.', e)
            else:
                return self.get_details(saved_model.uid)
        elif tarfile.is_tarfile(model_filepath) or zipfile.is_zipfile(model_filepath):
            return self._publish_from_archive(model, meta_props)
        else:
            raise WMLClientError(u'Saving trained model in repository failed. \'{}\' file does not have valid format'.format(model_filepath))

    # TODO make this way when all frameworks will be supported
    # def _publish_from_archive(self, path_to_archive, meta_props=None):
    #     self._validate_meta_prop(meta_props, self.ModelMetaNames.FRAMEWORK_NAME, STR_TYPE, True)
    #     self._validate_meta_prop(meta_props, self.ModelMetaNames.FRAMEWORK_VERSION, STR_TYPE, True)
    #     self._validate_meta_prop(meta_props, self.ModelMetaNames.NAME, STR_TYPE, True)
    #
    #     try:
    #         meta_data = MetaProps(Repository._meta_props_to_repository_v3_style(meta_props))
    #
    #         model_artifact = MLRepositoryArtifact(path_to_archive, name=str(meta_props[self.ModelMetaNames.NAME]), meta_props=meta_data)
    #
    #         saved_model = self._ml_repository_client.models.save(model_artifact)
    #     except Exception as e:
    #         raise WMLClientError(u'Publishing model failed.', e)
    #     else:
    #         return self.get_details(u'{}'.format(saved_model.uid))

    def _publish_from_archive(self, path_to_archive, meta_props=None,version=False,artifactid=None):
        self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.FRAMEWORK_NAME, STR_TYPE, True)
        self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.FRAMEWORK_VERSION, STR_TYPE, True)
        self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.NAME, STR_TYPE, True)
        def is_xml(model_filepath):
            return os.path.splitext(os.path.basename(model_filepath))[-1] == '.xml'

        url = self._client.wml_credentials['url'] + '/v3/ml_assets/models'
        payload = {
            "framework": {
                "name": meta_props[self.ConfigurationMetaNames.FRAMEWORK_NAME],
                "version": meta_props[self.ConfigurationMetaNames.FRAMEWORK_VERSION]
            },
            "name": meta_props[self.ConfigurationMetaNames.NAME],
            "author": {
            }
        }

        if self.ConfigurationMetaNames.RUNTIME_NAME in meta_props and self.ConfigurationMetaNames.RUNTIME_VERSION in meta_props:
            payload['framework'].update({
                "runtimes": [
                    {
                        "name": meta_props[self.ConfigurationMetaNames.RUNTIME_NAME],
                        "version": meta_props[self.ConfigurationMetaNames.RUNTIME_VERSION]
                    }
                ]
            })

        if self.ConfigurationMetaNames.FRAMEWORK_LIBRARIES in meta_props:
            payload['framework'].update({"libraries": meta_props[self.ConfigurationMetaNames.FRAMEWORK_LIBRARIES]})

        if self.ConfigurationMetaNames.TRAINING_DATA_SCHEMA in meta_props:
            payload.update({'training_data_schema': json.loads(meta_props[self.ConfigurationMetaNames.TRAINING_DATA_SCHEMA])})

        if self.ConfigurationMetaNames.TRAINING_DATA_REFERENCE in meta_props:
            payload.update({'training_data_reference': [json.loads(meta_props[self.ConfigurationMetaNames.TRAINING_DATA_REFERENCE])]})

        if self.ConfigurationMetaNames.TRAINING_DEFINITION_URL in meta_props:
            payload.update({'training_definition_url': json.loads(meta_props[self.ConfigurationMetaNames.TRAINING_DEFINITION_URL])})

        if self.ConfigurationMetaNames.OUTPUT_DATA_SCHEMA in meta_props:
            payload.update({'output_data_schema': json.loads(meta_props[self.ConfigurationMetaNames.OUTPUT_DATA_SCHEMA])})

        if self.ConfigurationMetaNames.INPUT_DATA_SCHEMA in meta_props:
            payload.update({'input_data_schema': json.loads(meta_props[self.ConfigurationMetaNames.INPUT_DATA_SCHEMA])})

        if self.ConfigurationMetaNames.DESCRIPTION in meta_props:
            payload.update({'description': meta_props[self.ConfigurationMetaNames.DESCRIPTION]})

        if self.ConfigurationMetaNames.AUTHOR_NAME in meta_props:
            payload['author'].update({'name': meta_props[self.ConfigurationMetaNames.AUTHOR_NAME]})

        if self.ConfigurationMetaNames.LABEL_FIELD in meta_props:
            payload.update({'label_column': json.loads(meta_props[self.ConfigurationMetaNames.LABEL_FIELD])})

        if self.ConfigurationMetaNames.EVALUATION_METHOD in meta_props and self.ConfigurationMetaNames.EVALUATION_METRICS in meta_props:
            payload.update({'evaluation': {
                    "method": meta_props[self.ConfigurationMetaNames.EVALUATION_METHOD],
                    "metrics": json.loads(meta_props[self.ConfigurationMetaNames.EVALUATION_METRICS])
                }
            })

        if self.ConfigurationMetaNames.RUNTIME_UID in meta_props:
            payload['runtime_url'] = self._href_definitions.get_runtime_href(meta_props[self.ConfigurationMetaNames.RUNTIME_UID])
        if(version==True):
            if not self._ICP:
                response = requests.post(
                    url+"/"+str_type_conv(artifactid),
                    json=payload,
                    headers=self._client._get_headers()
                )
            else:
                response = requests.post(
                    url+"/"+str_type_conv(artifactid),
                    json=payload,
                    headers=self._client._get_headers(),
                    verify=False
                )

            result = self._handle_response(201, u'creating model version', response)
        else:
            if not self._ICP:
                response = requests.post(
                    url,
                    json=payload,
                    headers=self._client._get_headers()
                )
            else:
                response = requests.post(
                    url,
                    json=payload,
                    headers=self._client._get_headers(),
                    verify=False
                )

        result = self._handle_response(201, u'creating model', response)
        model_uid = self._get_required_element_from_dict(result, 'model_details', ['metadata', 'guid'])
        url = self._get_required_element_from_dict(result, 'model_details',
                                                       ['entity', 'model_version', 'content_url'])
        with open(path_to_archive, 'rb') as f:
            if is_xml(path_to_archive):
                if not self._ICP:
                    response = requests.put(
                       url,
                       data=f,
                       headers=self._client._get_headers(content_type='application/xml')
                    )
                else:
                    response = requests.put(
                        url,
                        data=f,
                        headers=self._client._get_headers(content_type='application/xml'),
                        verify=False
                    )
            else:
                if not self._ICP:
                    response = requests.put(
                        url,
                        data=f,
                        headers=self._client._get_headers(content_type='application/octet-stream')
                    )
                else:
                    response = requests.put(
                        url,
                        data=f,
                        headers=self._client._get_headers(content_type='application/octet-stream'),
                        verify=False
                    )

            self._handle_response(200, u'uploading model content', response, False)
            if(version==True):
                return self._client.repository.get_details(artifactid+"/versions/"+model_uid)
            return self.get_details(model_uid)
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def store(self, model, meta_props=None, training_data=None, training_target=None, pipeline=None,version=False,artifactid=None):
        """
        Store trained model into Watson Machine Learning repository on Cloud.

        :param model:  The train model object (e.g: spark PipelineModel), or path to saved model in format .tar.gz/.str/.xml or directory containing model file(s), or trained model guid
        :type model: object/{str_type}

        :param meta_props: meta data of the training definition. To see available meta names use:

            >>> client.models.ConfigurationMetaNames.get()

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

        >>> stored_model_details = client.models.store(model, name)

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

        >>> stored_model_details = client.models.store(path_to_tar_gz, meta_props=metadata, training_data=None)

        A way you might use me with local directory containing model file(s):

        >>> stored_model_details = client.models.store(path_to_model_directory, meta_props=metadata, training_data=None)

        A way you might use me with trained model guid:

        >>> stored_model_details = client.models.store(trained_model_guid, meta_props=metadata, training_data=None)
        """
        model = str_type_conv(model)
        Models._validate_type(model, u'model', object, True)
        meta_props = copy.deepcopy(meta_props)
        meta_props = str_type_conv(meta_props)  # meta_props may be str, in this situation for py2 it will be converted to unicode
        Models._validate_type(meta_props, u'meta_props', [dict, STR_TYPE], True)
        # Repository._validate_type(training_data, 'training_data', object, False)
        # Repository._validate_type(training_target, 'training_target', list, False)
        meta_props_str_conv(meta_props)

        if type(meta_props) is STR_TYPE:
            meta_props = {
                self.ConfigurationMetaNames.NAME: meta_props
            }

        self.ConfigurationMetaNames._validate(meta_props)

        if ("frameworkName" in meta_props):
         framework_name = meta_props["frameworkName"].lower()
         if version == True and (framework_name == "mllib" or framework_name == "wml"):
            raise WMLClientError(u'Unsupported framework name: \'{}\' for creating a model version'.format(framework_name))

        if self.ConfigurationMetaNames.RUNTIME_NAME in meta_props and self.ConfigurationMetaNames.RUNTIME_VERSION in meta_props:
            meta_props[MetaNames.FRAMEWORK_RUNTIMES] = json.dumps([{u'name': meta_props[self.ConfigurationMetaNames.RUNTIME_NAME], u'version': meta_props[self.ConfigurationMetaNames.RUNTIME_VERSION]}])

        if self.ConfigurationMetaNames.TRAINING_DATA_REFERENCE in meta_props:
            meta_props[MetaNames.TRAINING_DATA_REFERENCE] = json.dumps(meta_props[self.ConfigurationMetaNames.TRAINING_DATA_REFERENCE])

        if self.ConfigurationMetaNames.TRAINING_DATA_SCHEMA in meta_props:
            meta_props[MetaNames.TRAINING_DATA_SCHEMA] = json.dumps(meta_props[self.ConfigurationMetaNames.TRAINING_DATA_SCHEMA])

        if self.ConfigurationMetaNames.TRAINING_DEFINITION_URL in meta_props:
            meta_props[MetaNames.TRAINING_DEFINITION_URL] = json.dumps(meta_props[self.ConfigurationMetaNames.TRAINING_DEFINITION_URL])

        if self.ConfigurationMetaNames.INPUT_DATA_SCHEMA in meta_props:
            meta_props[MetaNames.INPUT_DATA_SCHEMA] = json.dumps(meta_props[self.ConfigurationMetaNames.INPUT_DATA_SCHEMA])

        if self.ConfigurationMetaNames.OUTPUT_DATA_SCHEMA in meta_props:
            meta_props[MetaNames.OUTPUT_DATA_SCHEMA] = json.dumps(meta_props[self.ConfigurationMetaNames.OUTPUT_DATA_SCHEMA])

        if self.ConfigurationMetaNames.EVALUATION_METRICS in meta_props:
            meta_props[MetaNames.EVALUATION_METRICS] = json.dumps(meta_props[self.ConfigurationMetaNames.EVALUATION_METRICS])

        if self.ConfigurationMetaNames.LABEL_FIELD in meta_props:
            meta_props[MetaNames.LABEL_FIELD] = json.dumps(meta_props[self.ConfigurationMetaNames.LABEL_FIELD])

        if self.ConfigurationMetaNames.RUNTIME_UID in meta_props:
            # TODO workaround for Jihyoung MetaNames.RUNTIMES.URL
            meta_props["runtimesUrl"] = self._href_definitions.get_runtime_href(meta_props[self.ConfigurationMetaNames.RUNTIME_UID])

        if not isinstance(model, STR_TYPE):
            if(version==True):
                raise WMLClientError(u'Unsupported type: object for param model. Supported types: path to saved model, training ID')
            else:
                saved_model = self._publish_from_object(model=model, meta_props=meta_props, training_data=training_data, training_target=training_target, pipeline=pipeline)
        else:
            if (os.path.sep in model) or os.path.isfile(model) or os.path.isdir(model):
                if not os.path.isfile(model) and not os.path.isdir(model):
                    raise WMLClientError(u'Invalid path: neither file nor directory exists under this path: \'{}\'.'.format(model))
                saved_model = self._publish_from_file(model=model, meta_props=meta_props, training_data=training_data, training_target=training_target,ver=version,artifactid=artifactid)
            else:
                saved_model = self._publish_from_training(model_uid=model, meta_props=meta_props, training_data=training_data, training_target=training_target,version=version,artifactId=artifactid)

        return saved_model

    def update(self, model_uid, content_path=None, meta_props=None):
        """
            Update content of model with new one.

            :param model_uid:  Model UID
            :type model_uid: str
            :param content_path: path to tar.gz with new content of model
            :type content_path: str

            :returns: updated metadata of model
            :rtype: dict

            A way you might use me is:

            >>> model_details = client.models.update(model_uid, content_path)
        """
        Models._validate_type(model_uid, 'model_uid', STR_TYPE, True)
        Models._validate_type(content_path, 'content_path', STR_TYPE, False)

        if not self._ICP:
            response = requests.get(
                self._href_definitions.get_model_last_version_href(model_uid),
                headers=self._client._get_headers(no_content_type=True)
            )
        else:
            response = requests.get(
                self._href_definitions.get_model_last_version_href(model_uid),
                headers=self._client._get_headers(no_content_type=True),
                verify=False
            )
        model_details = self._handle_response(200, 'getting model details', response)

        if meta_props is not None: # TODO
            raise WMLClientError('Meta_props update unsupported.')
            # self._validate_type(meta_props, u'meta_props', dict, True)
            # meta_props_str_conv(meta_props)
            #
            # url = self._get_required_element_from_dict(model_details, 'model_details', ['entity', 'model_version', 'url'])
            #
            # response = requests.get(
            #     url,
            #     headers=self._client._get_headers()
            # )
            # details = response.json()
            #
            # # with validation should be somewhere else, on the begining, but when patch will be possible
            # patch_payload = self.ConfigurationMetaNames._generate_patch_payload(details['entity'], meta_props, with_validation=True)
            #
            # response = requests.patch(url, json=patch_payload, headers=self._client._get_headers())
            # updated_details = self._handle_response(200, u'model version patch', response)
            #
            # return updated_details

        if content_path is not None:
            payload = self._get_required_element_from_dict(model_details, 'model_details', ['entity'])

            #Input payload for POST call to create new model version should contain runtime_url field instead of runtime field
            if 'runtime' in payload:
                runtime_url = self._get_required_element_from_dict(payload, 'payload', ['runtime', 'url'])
                del payload['runtime']
                payload.update(
                    {
                        u'runtime_url': runtime_url
                    }
                )

            # TODO workaround to Lukasz Demo problem
            if 'training_data_reference' in payload and payload['training_data_reference'] is []:
                del payload['training_data_reference']

            if not self._ICP:
                response = requests.post(
                    self._href_definitions.get_model_last_version_href(model_uid),
                    headers=self._client._get_headers(),
                    json = payload
                )
            else:
                response = requests.post(
                    self._href_definitions.get_model_last_version_href(model_uid),
                    headers=self._client._get_headers(),
                    json = payload,
                    verify=False
                )

            # TODO probably should be 202
            new_details = self._handle_response(201, 'creating new model version', response)

            version_url = self._get_required_element_from_dict(new_details, 'model_details', ['entity', 'model_version', 'url'])

            with open(content_path, 'rb') as data:
                if not self._ICP:
                    response = requests.put(
                        version_url + '/content',
                        headers=self._client._get_headers(content_type='application/octet-stream'),
                        data=data
                    )
                else:
                    response = requests.put(
                        version_url + '/content',
                        headers=self._client._get_headers(content_type='application/octet-stream'),
                        data=data,
                        verify=False
                    )

            self._handle_response(200, 'uploading model content', response, False)

        return self.get_details(model_uid)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def load(self, artifact_uid):
        """
        Load model from repository to object in local environment.

        :param artifact_uid:  stored model UID
        :type artifact_uid: {str_type}

        :returns: trained model
        :rtype: object

        A way you might use me is:

        >>> model = client.models.load(model_uid)
        """
        artifact_uid = str_type_conv(artifact_uid)
        Models._validate_type(artifact_uid, u'artifact_uid', STR_TYPE, True)

        try:
            loaded_model = self._client.repository._ml_repository_client.models.get(artifact_uid)
            loaded_model = loaded_model.model_instance()
            self._logger.info(u'Successfully loaded artifact with artifact_uid: {}'.format(artifact_uid))
            return loaded_model
        except Exception as e:
            raise WMLClientError(u'Loading model with artifact_uid: \'{}\' failed.'.format(artifact_uid), e)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def download(self, model_uid, filename='downloaded_model.tar.gz'):
        """
            Download model from repository to local file.

            :param model_uid: stored model UID
            :type model_uid: {str_type}

            :param filename: name of local file to create (optional)
            :type filename: {str_type}

            Side effect:
                save model to file.

            A way you might use me is:

            >>> client.models.download(model_uid, 'my_model.tar.gz')
        """
        if os.path.isfile(filename):
            raise WMLClientError(u'File with name: \'{}\' already exists.'.format(filename))

        model_uid = str_type_conv(model_uid)
        Models._validate_type(model_uid, u'model_uid', STR_TYPE, True)
        filename = str_type_conv(filename)
        Models._validate_type(filename, u'filename', STR_TYPE, True)

        artifact_url = self._href_definitions.get_model_last_version_href(model_uid)

        try:
            artifact_content_url = str(artifact_url + u'/content')
            if not self._ICP:
                r = requests.get(artifact_content_url, headers=self._client._get_headers(), stream=True)
            else:
                r = requests.get(artifact_content_url, headers=self._client._get_headers(), stream=True, verify=False)
            self._handle_response(200, 'downloading model', r, False)

            downloaded_model = r.content
            self._logger.info(u'Successfully downloaded artifact with artifact_url: {}'.format(artifact_url))
        except WMLClientError as e:
            raise e
        except Exception as e:
            raise WMLClientError(u'Downloading model with artifact_url: \'{}\' failed.'.format(artifact_url), e)

        try:
            with open(filename, 'wb') as f:
                f.write(downloaded_model)
            self._logger.info(u'Successfully saved artifact to file: \'{}\''.format(filename))
            return None
        except IOError as e:
            raise WMLClientError(u'Saving model with artifact_url: \'{}\' failed.'.format(filename), e)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def delete(self, model_uid):
        """
            Delete model from repository.

            :param model_uid: stored model UID
            :type model_uid: {str_type}

            A way you might use me is:

            >>> client.models.delete(model_uid)
        """
        model_uid = str_type_conv(model_uid)
        Models._validate_type(model_uid, u'model_uid', STR_TYPE, True)

        try:
            deleted = self._client.repository._ml_repository_client.models.remove(str(model_uid))
            self._logger.info(u'Successfully deleted model with model_uid: \'{}\''.format(model_uid))
            self._logger.debug(u'Return object: {}'.format(deleted))
            return
        except Exception as e:
            raise WMLClientError(u'Model deletion failed.', e)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_details(self, model_uid=None, limit=None):
        """
           Get metadata of stored models. If model uid is not specified returns all models metadata.

           :param model_uid: stored model, definition or pipeline UID (optional)
           :type model_uid: {str_type}

           :param limit: limit number of fetched records (optional)
           :type limit: int

           :returns: stored model(s) metadata
           :rtype: dict

           A way you might use me is:

           >>> model_details = client.models.get_details(model_uid)
           >>> models_details = client.models.get_details()
        """
        model_uid = str_type_conv(model_uid)
        Models._validate_type(model_uid, u'model_uid', STR_TYPE, False)
        Models._validate_type(limit, u'limit', int, False)

        if not self._ICP:
            url = self._client.service_instance.details.get(u'entity').get(u'published_models').get(u'url')
        else:
            url = self._href_definitions.get_published_models_href()
        return self._get_artifact_details(url, model_uid, limit, 'models')

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_url(model_details):
        """
            Get url of stored model.

            :param model_details:  stored model details
            :type model_details: dict

            :returns: url to stored model
            :rtype: {str_type}

            A way you might use me is:

            >>> model_url = client.models.get_url(model_details)
        """
        Models._validate_type(model_details, u'model_details', object, True)
        Models._validate_type_of_details(model_details, MODEL_DETAILS_TYPE)

        try:
            return model_details[u'entity'][u'ml_asset_url']
        except:
            return WMLResource._get_required_element_from_dict(model_details, u'model_details', [u'metadata', u'url'])

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_uid(model_details):
        """
            Get uid of stored model.

            :param model_details:  stored model details
            :type model_details: dict

            :returns: uid of stored model
            :rtype: {str_type}

            A way you might use me is:

            >>> model_uid = client.models.get_uid(model_details)
        """
        Models._validate_type(model_details, u'model_details', object, True)
        Models._validate_type_of_details(model_details, MODEL_DETAILS_TYPE)

        try:
            return model_details[u'entity'][u'ml_asset_guid']
        except:
            return WMLResource._get_required_element_from_dict(model_details, u'model_details', [u'metadata', u'guid'])

    def list(self, limit=None):
        """
           List stored models. If limit is set to None there will be only first 50 records shown.

           :param limit: limit number of fetched records (optional)
           :type limit: int

           A way you might use me is

           >>> client.models.list()
        """

        model_resources = self.get_details(limit=limit)[u'resources']
        model_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at'], m[u'entity'][u'model_type']) for m in model_resources]

        self._list(model_values, [u'GUID', u'NAME', u'CREATED', u'FRAMEWORK'], limit, _DEFAULT_LIST_LENGTH)
