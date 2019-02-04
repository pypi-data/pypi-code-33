# coding=utf-8
from __future__ import print_function
import argparse
import logging
import urllib3
from retry import retry
from outdated import warn_if_outdated
from watson_machine_learning_client import WatsonMachineLearningAPIClient
from ibm_ai_openscale_cli.aios_client import AIOSClient
from ibm_ai_openscale_cli.ml_engines.watson_machine_learning import WatsonMachineLearningEngine
from ibm_ai_openscale_cli.ml_engines.azure_machine_learning import AzureMachineLearningEngine
from ibm_ai_openscale_cli.environments import Environments
from ibm_ai_openscale_cli.setup_classes.setup_services import SetupServices
from ibm_ai_openscale_cli.setup_classes.setup_ibmcloud_services_cli import SetupIBMCloudServicesCli
from ibm_ai_openscale_cli.setup_classes.setup_ibmcloud_services_rest import SetupIBMCloudServicesRest
from ibm_ai_openscale_cli.setup_classes.setup_ibmcloudprivate_services import SetupIBMCloudPrivateServices
from ibm_ai_openscale_cli.setup_classes.setup_azure_services import SetupAzureServices
from ibm_ai_openscale_cli.models.drug_selection_model import DrugSelectionModel
from ibm_ai_openscale_cli.models.german_credit_risk_model import GermanCreditRiskModel
from ibm_ai_openscale_cli.models.scikit_digits_model import ScikitDigitsModel
from ibm_ai_openscale_cli.version import __version__
from ibm_ai_openscale_cli import logging_temp_file, name

logger = logging.getLogger(__name__)

def _process_args():
    """Parse the CLI arguments

    Returns:
        dict -- dictionary with the arguments and values
    """
    parser = argparse.ArgumentParser()
    # required parameters
    requiredArgs = parser.add_argument_group('required arguments')
    requiredArgs.add_argument('-a', '--apikey', help='IBM Cloud APIKey', required=True)
    # Optional parameters
    optionalArgs = parser._action_groups.pop()
    parser.add_argument('--env', default='ypprod', help='Environment. Default "ypprod"', choices=['ypprod', 'ypqa', 'ys1dev', 'icp'])
    parser.add_argument('--resource-group', default='default', help='Resource Group to use. If not specified, then "default" group is used')
    parser.add_argument('--postgres', help='Path to postgres credentials file for the datamart database. If --postgres, --icd, and --db2 all are not specified, then the internal AIOS database is used')
    parser.add_argument('--icd', help='Path to IBM Cloud Database credentials file for the datamart database')
    parser.add_argument('--db2', help='Path to IBM DB2 credentials file for the datamart database')
    parser.add_argument('--wml', help='Path to IBM WML credentials file')
    parser.add_argument('--azure', help='Path to Microsoft Azure credentials file')
    parser.add_argument('--azure-deployment-name', help='Name of the deployment to use from Microsoft Azure ML Studio')
    parser.add_argument('--cos', help='Path to IBM Cloud Object Storage credentials file')
    parser.add_argument('--username', help='ICP username. Required if "icp" environment is chosen')
    parser.add_argument('--password', help='ICP password. Required if "icp" environment is chosen')
    parser.add_argument('--url', help='ICP url. Required if "icp" environment is chosen')
    parser.add_argument('--datamart-name', default='aiosfastpath', help='Specify data mart name and schema, default is "aiosfastpath"')
    parser.add_argument('--keep-schema', action='store_true', help='Use pre-existing datamart schema, only dropping all tables. If not specified, datamart schema is dropped and re-created')
    parser.add_argument('--history', default=7, help='Days of history to preload. Default is 7', type=int)
    parser.add_argument('--verbose', action='store_true', help='verbose flag')
    parser.add_argument('--version', action='version', version='%(prog)s {version}'.format(version=__version__))
    parser.add_argument('--model', default='DrugSelectionModel', help='Model to set up with AIOS (default "DrugSelectionModel")', choices=['all', 'DrugSelectionModel','GermanCreditRiskModel'])
    parser.add_argument('--bx', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--extend', action='store_true', help=argparse.SUPPRESS) # Extend existing datamart. If not specified and the datamart already exists, it will be deleted and recreated
    parser.add_argument('--reset', choices=['metrics', 'monitors', 'datamart', 'model'], help='Reset existing datamart then exit')
    parser.add_argument('--model-first-instance', default=1, help=argparse.SUPPRESS, type=int) # First "instance" (copy) of each model. Default 1 means to start with the base model instance
    parser.add_argument('--model-instances', default=1, help=argparse.SUPPRESS, type=int) # Number of additional instances beyond the first.
    parser.add_argument('--organization', help=argparse.SUPPRESS, required=False)
    parser.add_argument('--space', help=argparse.SUPPRESS, required=False)
    parser._action_groups.append(optionalArgs)
    args = parser.parse_args()

    # validate environment
    if 'throw' in args:
        logger.error(args.throw)
        exit(1)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('handle_response').setLevel(logging.DEBUG)
        logging.getLogger('ibm_ai_openscale.utils.client_errors').setLevel(logging.DEBUG)

    if args.azure:
        if not args.azure_deployment_name:
            logger.error('ERROR: A deployment name is required when Microsoft Azure engine is used with AIOS')
            exit(1)
        args.ml_engine_type = 'azureml'
    else:
        args.ml_engine_type = 'wml'

    if (args.postgres and args.icd) or (args.postgres and args.db2) or (args.icd and args.db2):
        logger.error('ERROR: Only one datamart database option can be specified')
        exit(1)

    warn_if_outdated(name, __version__)

    return args

def disable_ssl_warnings_icp(args):
    """
    For requests made against ICP, disable SSL-disabled warnings
    """
    if args.env == 'icp':
        logger.info('SSL verification is not used for requests against ICP Environment, disabling "InsecureRequestWarning"')
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_aios_and_mlengine_credentials(args, target_environment):
    setup_ibm_services = None
    if args.env == 'icp':
        setup_ibm_services = SetupIBMCloudPrivateServices(args, target_environment)
    else: # ypprod, ypqa, ys1dev
        if args.bx:
            setup_ibm_services = SetupIBMCloudServicesCli(args, target_environment)
        else:
            setup_ibm_services = SetupIBMCloudServicesRest(args, target_environment)

    # aios credentials
    aios_credentials = setup_ibm_services.setup_aios()

    # ml engine credentials
    ml_engine_credentials = None
    if args.ml_engine_type == 'azureml':
        ml_engine_credentials = SetupAzureServices(args, target_environment).setup_azureml()
    else:
        ml_engine_credentials = setup_ibm_services.setup_wml()

    return (aios_credentials, ml_engine_credentials)

def get_database_credentials(args, target_environment):
    setup_services = SetupServices(args, target_environment)
    postgres_credentials = setup_services.setup_postgres_database()
    icd_credentials = setup_services.setup_icd_database()
    db2_credentials = setup_services.setup_db2_database()
    database_credentials = None
    if postgres_credentials is not None:
        database_credentials = postgres_credentials
    elif icd_credentials is not None:
        database_credentials = icd_credentials
    elif db2_credentials is not None:
        database_credentials = db2_credentials
    return database_credentials

def get_modeldata_instance(modelname, args, target_environment, model_instance_num):
    model = None
    if modelname == 'DrugSelectionModel':
        model = DrugSelectionModel(target_environment, args.ml_engine_type, args.history, model_instance_num)
    elif modelname == 'GermanCreditRiskModel':
        model = GermanCreditRiskModel(target_environment, args.ml_engine_type, args.history, model_instance_num)
    elif modelname == 'ScikitDigitsModel':
        model = ScikitDigitsModel(target_environment, args.ml_engine_type, 0, model_instance_num) # temporarily, don't load history
    return model

def get_ml_engine_displayname(name):
    return {
        'wml': 'Watson Machine Learning',
        'azureml': 'Azure Machine Learning'
    }.get(name)

def main():

    # preprocessing
    args = _process_args()
    logger.info('ibm-ai-openscale-cli-{}'.format(__version__))
    logger.info('Log file: {0}'.format(logging_temp_file.name))
    disable_ssl_warnings_icp(args)

    target_environment = Environments(args).getEnvironment()

    # aios and ml-engine credentials
    aios_credentials, ml_engine_credentials = get_aios_and_mlengine_credentials(args, target_environment)
    database_credentials = get_database_credentials(args, target_environment)

    # instantiate ml client, setup and deploy models
    wml_modelnames = ['DrugSelectionModel', 'GermanCreditRiskModel'] # suppress ScikitDigitsModel for now
    azure_modelnames = ['GermanCreditRiskModel']

    if args.model != 'all':
        if args.ml_engine_type == 'azureml':
            if args.model not in azure_modelnames:
                logger.error('Invalid model name specified. Only the following models are supported on Azure: {}'.format(azure_modelnames))
                exit(1)
        wml_modelnames = [args.model]

    if args.reset == 'metrics' or args.reset == 'monitors' or args.reset == 'datamart':
        wml_modelnames = [] # --reset options override the --model argument
        aios_client = AIOSClient(aios_credentials, args.datamart_name, args.keep_schema, target_environment)
        if args.reset == 'datamart':
            # "Factory reset" the system to a fresh state as if there was not any configuration.
            logger.info('Reset datamart')
            aios_client.clean_datamart(database_credentials)
            aios_client.create_datamart(database_credentials)
        elif args.reset == 'monitors':
            aios_client.reset_monitors(database_credentials)
        elif args.reset == 'metrics':
            aios_client.reset_metrics(database_credentials)

    modeldata = None
    run_once = False if (args.extend or args.reset == 'model') else True
    for modelname in wml_modelnames:
        logger.info('--------------------------------------------------------------------------------')
        logger.info('Model: {}, Engine: {}'.format(modelname, get_ml_engine_displayname(args.ml_engine_type)))
        logger.info('--------------------------------------------------------------------------------')
        for model_instance_num in range(args.model_first_instance, args.model_first_instance + args.model_instances):

            # model instance
            modeldata = get_modeldata_instance(modelname, args, target_environment, model_instance_num)

            # aios instance
            aios_client = AIOSClient(aios_credentials, args.datamart_name, args.keep_schema, target_environment, modeldata, args.ml_engine_type)
            if run_once:
                run_once = False
                aios_client.clean_datamart(database_credentials)
                aios_client.create_datamart(database_credentials)
                binding_id = aios_client.bind_mlinstance(ml_engine_credentials)

            # ml engine instance
            ml_engine = None
            if args.ml_engine_type == 'wml':
                ml_engine = WatsonMachineLearningEngine(ml_engine_credentials, target_environment, modeldata)
            elif args.ml_engine_type == 'azureml':
                ml_engine = AzureMachineLearningEngine(aios_client.get_azure_deployment_details(args.azure_deployment_name))

            # model cleanup flag specified
            if args.reset == 'model':
                if args.ml_engine_type == 'wml': # for wml only
                    ml_engine.model_cleanup()
                    continue # skip all AIOS datamart operations

            # update model as needed
            if args.env != 'icp' and modelname == 'GermanCreditRiskModel':
                cos_credentials = SetupIBMCloudServicesRest(args, target_environment).setup_cos()
                modeldata.cos_credentials = cos_credentials
                if args.ml_engine_type == 'wml':
                    modeldata.update_training_metadata()
            # create models and deploy
            model_deployment_dict = None
            if args.ml_engine_type == 'wml':
                model_deployment_dict = ml_engine.create_model_and_deploy()
            elif args.ml_engine_type == 'azureml':
                model_deployment_dict = ml_engine.get_deployment_details()

            # ai openscale operations
            aios_client.subscribe_to_model_deployment(model_deployment_dict)
            aios_client.configure_subscription()
            aios_client.payload_logging()
            aios_client.configure_subscription_monitors()
            aios_client.generate_sample_metrics()
            aios_client.generate_sample_scoring(ml_engine)

    logger.info('Process completed')
    dashboard_url = target_environment['aios_url']
    if dashboard_url.startswith('https://api.'):
        dashboard_url = dashboard_url.replace('https://api.', 'https://')
    logger.info('The AI OpenScale dashboard can be accessed at: {}/aiopenscale'.format(dashboard_url))
