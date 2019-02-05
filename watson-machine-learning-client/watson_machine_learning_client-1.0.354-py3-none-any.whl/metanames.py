################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

from __future__ import print_function
from watson_machine_learning_client.libs.repository_v3.mlrepository import MetaNames
from tabulate import tabulate
import copy
from watson_machine_learning_client.wml_resource import WMLResource
from watson_machine_learning_client.utils import STR_TYPE, STR_TYPE_NAME
from watson_machine_learning_client.log_util import get_logger
from watson_machine_learning_client.wml_client_error import WMLClientError

logger = get_logger('watson_machine_learning_client.metanames')


class MetaProp:
    def __init__(self, name, key, prop_type, required, example_value, ignored=False, hidden=False, default_value='', path=None, transform=lambda x, client: x):
        self.key = key
        self.name = name
        self.prop_type = prop_type
        self.required = required
        self.example_value = example_value
        self.ignored = ignored
        self.hidden = hidden
        self.default_value = default_value
        self.path = path if path is not None else '/' + key
        self.transform = transform


class MetaNamesBase:
    def __init__(self, meta_props_definitions):
        self._meta_props_definitions = meta_props_definitions

    def _validate(self, meta_props):
        for meta_prop in self._meta_props_definitions:
            if meta_prop.ignored is False:
                WMLResource._validate_meta_prop(meta_props, meta_prop.key, meta_prop.prop_type, meta_prop.required)
            else:
              if(meta_prop.key in meta_props):
                logger.warning('\'{}\' meta prop is deprecated. It will be ignored.'.format(meta_prop.name))

    def _check_types_only(self, meta_props):
        for meta_prop in self._meta_props_definitions:
            if meta_prop.ignored is False:
                WMLResource._validate_meta_prop(meta_props, meta_prop.key, meta_prop.prop_type, False)
            else:
              if (meta_prop.key in meta_props):
                logger.warning('\'{}\' meta prop is deprecated. It will be ignored.'.format(meta_prop.name))

    def get(self):
        return sorted(list(map(lambda x: x.name, filter(lambda x: not x.ignored and not x.hidden, self._meta_props_definitions))))

    def show(self):
        print(self._generate_table())

    def _generate_doc_table(self):
        return self._generate_table('MetaName', 'Type', 'Required', 'Default value', 'Example value',
                                    show_examples=True, format='grid', values_format='``{}``')

    def _generate_doc(self, resource_name):
        return """
Set of MetaNames for {}.

Available MetaNames:

{}

""".format(resource_name, MetaNamesBase(self._meta_props_definitions)._generate_doc_table())


    def _generate_table(self, name_label='META_PROP NAME', type_label='TYPE',
                       required_label='REQUIRED', default_value_label='DEFAULT_VALUE',
                       example_value_label='EXAMPLE_VALUE', show_examples=False, format='simple', values_format='{}'):

        show_defaults = any(meta_prop.default_value is not '' for meta_prop in filter(lambda x: not x.ignored and not x.hidden, self._meta_props_definitions))

        header = [name_label, type_label, required_label]

        if show_defaults:
            header.append(default_value_label)

        if show_examples:
            header.append(example_value_label)

        table_content = []

        for meta_prop in filter(lambda x: not x.ignored and not x.hidden, self._meta_props_definitions):
            row = [meta_prop.name, meta_prop.prop_type.__name__, u'Y' if meta_prop.required else u'N']

            if show_defaults:
                row.append(values_format.format(meta_prop.default_value) if meta_prop.default_value is not '' else '')

            if show_examples:
                row.append(values_format.format(meta_prop.example_value) if meta_prop.example_value is not '' else '')

            table_content.append(row)

        table = tabulate(
            [header] + table_content,
            tablefmt=format
        )
        return table

    def get_example_values(self):
        return dict((x.key, x.example_value) for x in filter(lambda x: not x.ignored and not x.hidden, self._meta_props_definitions))

    def _generate_resource_metadata(self, meta_props, client=None, with_validation=False, initial_metadata={}):
        if with_validation:
            self._validate(meta_props)

        metadata = copy.deepcopy(initial_metadata)

        def update_map(m, path, el):
            if type(m) is dict:
                if len(path) == 1:
                    m[path[0]] = el
                else:
                    if path[0] not in m:
                        if type(path[1]) is not int:
                            m[path[0]] = {}
                        else:
                            m[path[0]] = []
                    update_map(m[path[0]], path[1:], el)
            elif type(m) is list:
                if len(path) == 1:
                    if len(m) > len(path):
                        m[path[0]] = el
                    else:
                        m.append(el)
                else:
                    if len(m) <= path[0]:
                        m.append({})
                    update_map(m[path[0]], path[1:], el)
            else:
                raise WMLClientError('Unexpected metadata path type: {}'.format(type(m)))


        for meta_prop_def in filter(lambda x: not x.ignored, self._meta_props_definitions):
            if meta_prop_def.key in meta_props:

                path = [int(p) if p.isdigit() else p for p in meta_prop_def.path.split('/')[1:]]

                update_map(
                    metadata,
                    path,
                    meta_prop_def.transform(meta_props[meta_prop_def.key], client)
                )

        return metadata

    def _generate_patch_payload(self, current_metadata, meta_props, client=None, with_validation=False):
        if with_validation:
            self._check_types_only(meta_props)

        updated_metadata = self._generate_resource_metadata(meta_props, client, False, current_metadata)

        patch_payload = []

        def contained_path(metadata, path):
            if path[0] in metadata:
                if len(path) == 1:
                    return [path[0]]
                else:
                    rest_of_path = contained_path(metadata[path[0]], path[1:])
                    if rest_of_path is None:
                        return [path[0]]
                    else:
                        return [path[0]] + rest_of_path
            else:
                return []

        def get_value(metadata, path):
            if len(path) == 1:
                return metadata[path[0]]
            else:
                return get_value(metadata[path[0]], path[1:])

        def already_in_payload(path):
            return any([el['path'] == path for el in patch_payload])

        def update_payload(path):
            existing_path = contained_path(current_metadata, path)

            if len(existing_path) == len(path):
                patch_payload.append({
                    'op': 'replace',
                    'path': '/' + '/'.join(existing_path),
                    'value': get_value(updated_metadata, existing_path)
                })
            else:
                if not already_in_payload(existing_path):
                    patch_payload.append({
                        'op': 'add',
                        'path': '/' + '/'.join(existing_path + [path[len(existing_path)]]),
                        'value': get_value(updated_metadata, existing_path + [path[len(existing_path)]])
                    })

        for meta_prop_def in filter(lambda x: not x.ignored, self._meta_props_definitions):
            if meta_prop_def.key in meta_props:

                path = [int(p) if p.isdigit() else p for p in meta_prop_def.path.split('/')[1:]]

                update_payload(path)

        return patch_payload


class TrainingConfigurationMetaNames(MetaNamesBase):
    _COMPUTE_CONFIGURATION_DEFAULT = 'k80'
    NAME = "name"
    DESCRIPTION = "description"
    AUTHOR_NAME = "author_name"
    AUTHOR_EMAIL = "author_email"
    TRAINING_DATA_REFERENCE = "training_data"
    TRAINING_RESULTS_REFERENCE = "training_results"
    EXECUTION_COMMAND = "command"
    COMPUTE_CONFIGURATION = "compute_configuration_name"

    _meta_props_definitions = [
        MetaProp('NAME',                        NAME,                                  STR_TYPE,   True,   u'Hand-written Digit Recognition'),
        MetaProp('DESCRIPTION',                 DESCRIPTION,                           STR_TYPE,   False,  u'Hand-written Digit Recognition training'),
        MetaProp('AUTHOR_NAME',                 AUTHOR_NAME,                           STR_TYPE,   False,  u'John Smith'),
        MetaProp('AUTHOR_EMAIL',                AUTHOR_EMAIL,                          STR_TYPE,   False,  u'john.smith@x.com', ignored=True),
        MetaProp('TRAINING_DATA_REFERENCE',     TRAINING_DATA_REFERENCE,               dict,       True,   {u'connection': {u'endpoint_url': u'https://s3-api.us-geo.objectstorage.softlayer.net',u'access_key_id': u'***',u'secret_access_key': u'***'},u'source': {u'bucket': u'train-data'},u'type': u's3'}),
        MetaProp('TRAINING_RESULTS_REFERENCE',  TRAINING_RESULTS_REFERENCE,            dict,       True,   {u'connection': {u'endpoint_url': u'https://s3-api.us-geo.objectstorage.softlayer.net',u'access_key_id': u'***',u'secret_access_key': u'***'},u'target': {u'bucket': u'train-data'},u'type': u's3'}),
        MetaProp('EXECUTION_COMMAND',           EXECUTION_COMMAND,                     STR_TYPE,   False,  u'python3 tensorflow_mnist_softmax.py --trainingIters 20', default_value='<value from model definition>'),
        MetaProp('COMPUTE_CONFIGURATION',       COMPUTE_CONFIGURATION,                 dict,       False,  {u'name': _COMPUTE_CONFIGURATION_DEFAULT}, default_value={u'name': _COMPUTE_CONFIGURATION_DEFAULT})
    ]

    __doc__ = MetaNamesBase(_meta_props_definitions)._generate_doc('trainings')

    def __init__(self):
        MetaNamesBase.__init__(self, self._meta_props_definitions)


class ExperimentMetaNames(MetaNamesBase):
    NAME = "name"
    DESCRIPTION = "description"
    TAGS = "tags"
    AUTHOR_NAME = "author_name"
    AUTHOR_EMAIL = "author_email"
    EVALUATION_METHOD = "evaluation_method"
    EVALUATION_METRICS = "evaluation_metrics"
    TRAINING_REFERENCES = "training_references"
    TRAINING_DATA_REFERENCE = "training_data_reference"
    TRAINING_RESULTS_REFERENCE = "training_results_reference"

    _meta_props_definitions = [
        MetaProp('NAME',                        NAME,                        STR_TYPE,   True,     u'Hand-written Digit Recognitionu', path="/settings/name"),
        MetaProp('DESCRIPTION',                 DESCRIPTION,                 STR_TYPE,   False,    u'Hand-written Digit Recognition training', path="/settings/description"),
        MetaProp('TAGS',                        TAGS,                        list,       False,    [{u'value': 'dsx-project.<project-guid>',u'description': 'DSX project guid'}]),
        MetaProp('AUTHOR_NAME',                 AUTHOR_NAME,                 STR_TYPE,   False,    u'John Smith', path="/settings/author/name"),
        MetaProp('AUTHOR_EMAIL',                AUTHOR_EMAIL,                STR_TYPE,   False,    u'john.smith@x.com', ignored=True),
        MetaProp('EVALUATION_METHOD',           EVALUATION_METHOD,           STR_TYPE,   False,    u'multiclass', path="/settings/evaluation_definition/method"),
        MetaProp('EVALUATION_METRICS',          EVALUATION_METRICS,          list,       False,    [u'accuracy'], path="/settings/evaluation_definition/metrics", transform=lambda m, client: [{u'name': x} for x in m]),
        MetaProp('TRAINING_REFERENCES',         TRAINING_REFERENCES,         list,       True,     [{u'training_definition_url': u'https://ibm-watson-ml.mybluemix.net/v3/ml_assets/training_definitions/12345',u'compute_configuration': {u'name': TrainingConfigurationMetaNames._COMPUTE_CONFIGURATION_DEFAULT}},{u'training_definition_url': u'https://ibm-watson-ml.mybluemix.net/v3/ml_assets/training_definitions/67890'}]),
        MetaProp('TRAINING_DATA_REFERENCE',     TRAINING_DATA_REFERENCE,     dict,       True,     {u'connection': {u'endpoint_url': u'https://s3-api.us-geo.objectstorage.softlayer.net',u'access_key_id': u'***',u'secret_access_key': u'***'},u'source': {u'bucket': u'train-data'},u'type': u's3'}),
        MetaProp('TRAINING_RESULTS_REFERENCE',  TRAINING_RESULTS_REFERENCE,  dict,       True,     {u'connection': {u'endpoint_url': u'https://s3-api.us-geo.objectstorage.softlayer.net',u'access_key_id': u'***',u'secret_access_key': u'***'},u'target': {u'bucket': u'result-data'},u'type': 's3'})
    ]

    __doc__ = MetaNamesBase(_meta_props_definitions)._generate_doc('experiments')

    def __init__(self):
        MetaNamesBase.__init__(self, self._meta_props_definitions)


class ModelDefinitionMetaNames(MetaNamesBase):
    NAME = "name"
    DESCRIPTION = "description"
    AUTHOR_NAME = "author_name"
    AUTHOR_EMAIL = "author_email"
    FRAMEWORK_NAME = "framework_name"
    FRAMEWORK_VERSION = "framework_version"
    RUNTIME_NAME = "runtime_name"
    RUNTIME_VERSION = "runtime_version"
    EXECUTION_COMMAND = "command"
    TRAINING_DATA_REFERENCES = "training_data_reference"

    _meta_props_definitions = [
        MetaProp('NAME',                NAME, STR_TYPE, True, u'my_training_definition'),
        MetaProp('DESCRIPTION',         DESCRIPTION, STR_TYPE, False, u'my_description'),
        MetaProp('TRAINING_DATA_REFERENCES', TRAINING_DATA_REFERENCES, list, False, {}, path="/training_data_reference"),
        MetaProp('AUTHOR_NAME',         AUTHOR_NAME, STR_TYPE, False, u'John Smith', path='/author/name'),
        MetaProp('AUTHOR_EMAIL',        AUTHOR_EMAIL, STR_TYPE, False, u'john.smith@x.com', ignored=True),
        MetaProp('FRAMEWORK_NAME',      FRAMEWORK_NAME, STR_TYPE, True, u'tensorflow', path='/framework/name'),
        MetaProp('FRAMEWORK_VERSION',   FRAMEWORK_VERSION, STR_TYPE, True, u'1.5', path='/framework/version'),
        MetaProp('RUNTIME_NAME',        RUNTIME_NAME, STR_TYPE, True, u'python', path='/framework/runtimes/0/name'),
        MetaProp('RUNTIME_VERSION',     RUNTIME_VERSION, STR_TYPE, True, u'3.5', path='/framework/runtimes/0/version'),
        MetaProp('EXECUTION_COMMAND',   EXECUTION_COMMAND, STR_TYPE, False, u'python3 tensorflow_mnist_softmax.py --trainingIters 20')
    ]

    __doc__ = MetaNamesBase(_meta_props_definitions)._generate_doc('definitions')

    def __init__(self):
        MetaNamesBase.__init__(self, self._meta_props_definitions)


class ModelMetaNames(MetaNamesBase):
    NAME = "name"
    DESCRIPTION = MetaNames.DESCRIPTION
    AUTHOR_NAME = MetaNames.AUTHOR_NAME
    AUTHOR_EMAIL = "author_email"
    FRAMEWORK_NAME = MetaNames.FRAMEWORK_NAME
    FRAMEWORK_VERSION = MetaNames.FRAMEWORK_VERSION
    FRAMEWORK_LIBRARIES = MetaNames.FRAMEWORK_LIBRARIES
    RUNTIME_NAME = "runtime_name"
    RUNTIME_VERSION = "runtime_version"
    TRAINING_DATA_SCHEMA = MetaNames.TRAINING_DATA_SCHEMA
    TRAINING_DATA_REFERENCE = MetaNames.TRAINING_DATA_REFERENCE
    EVALUATION_METHOD = MetaNames.EVALUATION_METHOD
    EVALUATION_METRICS = MetaNames.EVALUATION_METRICS
    OUTPUT_DATA_SCHEMA = MetaNames.OUTPUT_DATA_SCHEMA
    LABEL_FIELD = MetaNames.LABEL_FIELD
    TRANSFORMED_LABEL_FIELD = MetaNames.TRANSFORMED_LABEL_FIELD
    RUNTIME_UID = "runtime_uid"
    TRAINING_DEFINITION_URL = MetaNames.TRAINING_DEFINITION_URL
    INPUT_DATA_SCHEMA = MetaNames.INPUT_DATA_SCHEMA

    _meta_props_definitions = [
        MetaProp('NAME',                    NAME,                        STR_TYPE,   True,   "my_model"),
        MetaProp('DESCRIPTION',             DESCRIPTION,                 STR_TYPE,   False,  "my_description", path="/description"),
        MetaProp('AUTHOR_NAME',             AUTHOR_NAME,                 STR_TYPE,   False,  u'John Smith', path="/author/name"),
        MetaProp('AUTHOR_EMAIL',            AUTHOR_EMAIL,                STR_TYPE,   False,  u'john.smith@x.com', ignored=True),
        MetaProp('FRAMEWORK_NAME',          FRAMEWORK_NAME,              STR_TYPE,   False,  u'tensorflow', path="/framework/name"),
        MetaProp('FRAMEWORK_VERSION',       FRAMEWORK_VERSION,           STR_TYPE,   False,  u'1.5', path="/framework/version"),
        MetaProp('FRAMEWORK_LIBRARIES',     FRAMEWORK_LIBRARIES,         list,       False,  [{'name': 'keras', 'version': '2.1.3'}], path="/framework/libraries"),
        MetaProp('RUNTIME_NAME',            RUNTIME_NAME,                STR_TYPE,   False,  u'python', path="/framework/runtimes/0/name"),
        MetaProp('RUNTIME_VERSION',         RUNTIME_VERSION,             STR_TYPE,   False,  u'3.5', path="/framework/runtimes/0/version"),
        MetaProp('TRAINING_DATA_SCHEMA',    TRAINING_DATA_SCHEMA,        dict,       False,  {}, path="/training_data_schema"),
        MetaProp('INPUT_DATA_SCHEMA',       INPUT_DATA_SCHEMA,           dict,       False,  {}, path="/input_data_schema"),
        MetaProp('TRAINING_DATA_REFERENCE', TRAINING_DATA_REFERENCE,     dict,       False,  {}, path="/training_data_reference"),
        MetaProp('EVALUATION_METHOD',       EVALUATION_METHOD,           STR_TYPE,   False,  "multiclass", path="/evaluation/method"),
        MetaProp('EVALUATION_METRICS',      EVALUATION_METRICS,          list,       False,  [{"name": "accuracy","value": 0.64,"threshold": 0.8}], path="/evaluation/metrics"),
        MetaProp('OUTPUT_DATA_SCHEMA',      OUTPUT_DATA_SCHEMA,          dict,       False,  {"fields": [{"name": "ID", "metadata": {}, "nullable": True, "type": "integer"}, {"name": "Gender", "metadata": {}, "nullable": True, "type": "string"}, {"name": "Status", "metadata": {}, "nullable": True, "type": "string"}, {"name": "Children", "metadata": {}, "nullable": True, "type": "integer"}, {"name": "Age", "metadata": {}, "nullable": True, "type": "decimal(14,6)"}, {"name": "Customer_Status", "metadata": {}, "nullable": True, "type": "string"}, {"name": "Car_Owner", "metadata": {}, "nullable": True, "type": "string"}, {"name": "Customer_Service", "metadata": {}, "nullable": True, "type": "string"}, {"name": "Satisfaction", "metadata": {}, "nullable": True, "type": "integer" }, {"name": "Business_Area", "metadata": {}, "nullable": True, "type": "string"}, {"name": "prediction", "metadata": {"modeling_role": "prediction"}, "nullable": True, "type": "double"}, {"name": "predictedLabel", "metadata": {"modeling_role": "decoded-target", "values": ["NA", "Free Upgrade", "On-demand pickup location", "Voucher", "Premium features"]}, "nullable": True, "type": "string"}, {"name": "probability", "metadata": {"modeling_role": "probability"}, "nullable": True, "type": {"containsNull": True, "type": "array", "elementType": "double"}}], "type": "struct"}, path="/output_data_schema"),
        MetaProp('LABEL_FIELD',             LABEL_FIELD,                 STR_TYPE,   False,  'PRODUCT_LINE', path="/label_column"),
        MetaProp('TRANSFORMED_LABEL_FIELD', TRANSFORMED_LABEL_FIELD,     STR_TYPE,   False,  'PRODUCT_LINE_IX', path="/transformed_label"),
        MetaProp('RUNTIME_UID',             RUNTIME_UID,                 STR_TYPE,   False,  '53628d69-ced9-4f43-a8cd-9954344039a8', path="/runtime_url", transform=lambda x, client: client.repository._href_definitions.get_runtime_href(x)),
        MetaProp('TRAINING_DEFINITION_URL', TRAINING_DEFINITION_URL,     STR_TYPE,   False,  'https://us-south.ml.cloud.ibm.com/v3/ml_assets/training_definitions/ff24ebec-86af-4f2d-ab4c-2fc9e2a3efbc')
    ]

    __doc__ = MetaNamesBase(_meta_props_definitions)._generate_doc('models')

    def __init__(self):
        MetaNamesBase.__init__(self, self._meta_props_definitions)


class LearningSystemMetaNames(MetaNamesBase):
    _COMPUTE_CONFIGURATION_DEFAULT = 'k80'
    FEEDBACK_DATA_REFERENCE = "feedback_data_reference"
    SPARK_REFERENCE = "spark_instance"
    MIN_FEEDBACK_DATA_SIZE = "min_feedback_data_size"
    AUTO_RETRAIN = "auto_retrain"
    AUTO_REDEPLOY = "auto_redeploy"
    COMPUTE_CONFIGURATION = "compute_configuration"
    TRAINING_RESULTS_REFERENCE = "training_results_reference"

    _meta_props_definitions = [
        MetaProp('FEEDBACK_DATA_REFERENCE', FEEDBACK_DATA_REFERENCE,     dict,       True, {}),
        MetaProp('SPARK_REFERENCE',         SPARK_REFERENCE,             dict,       False, {}),
        MetaProp('MIN_FEEDBACK_DATA_SIZE',  MIN_FEEDBACK_DATA_SIZE,      int,        True, 100),
        MetaProp('AUTO_RETRAIN',            AUTO_RETRAIN,                STR_TYPE,   True, "conditionally"),
        MetaProp('AUTO_REDEPLOY',           AUTO_REDEPLOY,               STR_TYPE,   True, "always"),
        MetaProp('COMPUTE_CONFIGURATION',   COMPUTE_CONFIGURATION,       dict,       False, {u'name': _COMPUTE_CONFIGURATION_DEFAULT}),
        MetaProp('TRAINING_RESULTS_REFERENCE', TRAINING_RESULTS_REFERENCE, dict,        False, {u'connection': {u'endpoint_url': u'https://s3-api.us-geo.objectstorage.softlayer.net', u'access_key_id': u'***', u'secret_access_key': u'***'},u'target': {u'bucket': u'train-data'}, u'type': u's3'}),
    ]

    __doc__ = MetaNamesBase(_meta_props_definitions)._generate_doc('learning system')

    def __init__(self):
        MetaNamesBase.__init__(self, self._meta_props_definitions)


class PayloadLoggingMetaNames(MetaNamesBase):
    PAYLOAD_DATA_REFERENCE = "payload_store"
    LABELS = "labels"
    OUTPUT_DATA_SCHEMA = "output_data_schema"

    _meta_props_definitions = [
        MetaProp('PAYLOAD_DATA_REFERENCE',  PAYLOAD_DATA_REFERENCE,       dict, True,     {}),
        MetaProp('LABELS',                  LABELS,              list, False,    ['a', 'b', 'c']),
        MetaProp('OUTPUT_DATA_SCHEMA',      OUTPUT_DATA_SCHEMA,  dict, False,    {})
    ]

    __doc__ = MetaNamesBase(_meta_props_definitions)._generate_doc('payload logging system')

    def __init__(self):
        MetaNamesBase.__init__(self, self._meta_props_definitions)


class FunctionMetaNames(MetaNamesBase):
    NAME = "name"
    DESCRIPTION = "description"
    RUNTIME_UID = "runtime_uid"
    INPUT_DATA_SCHEMA = "input_data_schema"
    OUTPUT_DATA_SCHEMA = "output_data_schema"
    TAGS = "tags"

    _meta_props_definitions = [
        MetaProp('NAME',                NAME,                STR_TYPE,   True,   "ai_function"),
        MetaProp('DESCRIPTION',         DESCRIPTION,         STR_TYPE,   False,  "This is ai function"),
        MetaProp('RUNTIME_UID',         RUNTIME_UID,         STR_TYPE,   False,  '53628d69-ced9-4f43-a8cd-9954344039a8', path="/runtime_url", transform=lambda x, client: client.repository._href_definitions.get_runtime_href(x)),
        MetaProp('INPUT_DATA_SCHEMA',   INPUT_DATA_SCHEMA,   dict,       False,  {"type": "struct", "fields": [{"name": "x", "type": "double", "nullable": False, "metadata": {}}, {"name": "y", "type": "double", "nullable": False, "metadata": {}}]}),
        MetaProp('OUTPUT_DATA_SCHEMA',  OUTPUT_DATA_SCHEMA,  dict,       False,  {"type": "struct", "fields": [{"name": "multiplication", "type": "double", "nullable": False, "metadata": {}}]}),
        MetaProp('TAGS',                TAGS,                list,       False,  [{"value": "ProjectA", "description": "Functions created for ProjectA"}])
    ]

    __doc__ = MetaNamesBase(_meta_props_definitions)._generate_doc('AI functions')

    def __init__(self):
        MetaNamesBase.__init__(self, self._meta_props_definitions)


class RuntimeMetaNames(MetaNamesBase):
    NAME = "name"
    DESCRIPTION = "description"
    PLATFORM = "platform"
    LIBRARIES_UIDS = "libraries_uids"
    LIBRARIES_DEFINITIONS = "libraries_definitions"
    CONFIGURATION_FILEPATH = "configuration_filepath"

    _meta_props_definitions = [
        MetaProp('NAME',                            NAME,                            STR_TYPE,   True,   "runtime_spec_python_3.5"),
        MetaProp('DESCRIPTION',                     DESCRIPTION,                     STR_TYPE,   False,  "py35"),
        MetaProp('PLATFORM',                        PLATFORM,                        dict,       True,   {"name": "python", "version": "3.5"}),
        MetaProp('LIBRARIES_UIDS',                  LIBRARIES_UIDS,                 list, False, ["46dc9cf1-252f-424b-b52d-5cdd9814987f"]),
        MetaProp('LIBRARIES_DEFINITIONS',           LIBRARIES_DEFINITIONS,          list, False, [{"name": "libraries_custom", "description": "custom libraries for scoring", "filepath": "/home/lib.gz", "version": "1.0", "platform": "python", "platform_versions": ["3.5"]}]),
        MetaProp('CONFIGURATION_FILEPATH',          CONFIGURATION_FILEPATH,          STR_TYPE,   False,   "/home/env_config.yaml")
    ]

    __doc__ = MetaNamesBase(_meta_props_definitions)._generate_doc('Runtime Specs')

    def __init__(self):
        MetaNamesBase.__init__(self, self._meta_props_definitions)


class LibraryMetaNames(MetaNamesBase):
    NAME = "name"
    DESCRIPTION = "description"
    FILEPATH = "filepath"
    VERSION = "version"
    PLATFORM = "platform"

    _meta_props_definitions = [
        MetaProp('NAME',            NAME,          STR_TYPE,   True,   "my_lib"),
        MetaProp('DESCRIPTION',     DESCRIPTION,   STR_TYPE,   False,  "my lib"),
        MetaProp('PLATFORM',        PLATFORM,      dict,       True,   {"name": "python", "versions": ["3.5"]}),
        MetaProp('VERSION',         VERSION,       STR_TYPE,   True,   "1.0"),
        MetaProp('FILEPATH',        FILEPATH,      STR_TYPE,   True,  "/home/user/my_lib_1_0.zip")
    ]

    __doc__ = MetaNamesBase(_meta_props_definitions)._generate_doc('Custom Libraries')

    def __init__(self):
        MetaNamesBase.__init__(self, self._meta_props_definitions)