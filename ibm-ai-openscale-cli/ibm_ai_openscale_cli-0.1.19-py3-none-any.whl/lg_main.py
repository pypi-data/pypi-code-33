# coding=utf-8
from __future__ import print_function
import argparse
import logging
import urllib3
from retry import retry
from outdated import warn_if_outdated
from watson_machine_learning_client import WatsonMachineLearningAPIClient
from ibm_ai_openscale_cli.lg_aios_client import AIOSClientLG
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
from ibm_ai_openscale_cli.main import disable_ssl_warnings_icp, get_aios_and_mlengine_credentials, get_database_credentials, get_modeldata_instance

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
    parser.add_argument('--organization', help='Cloud Foundry Organization to use', required=False)
    parser.add_argument('--space', help='Cloud Foundry Space to use', required=False)
    parser.add_argument('--postgres', help='Path to postgres credentials file. If not specified, then the internal AIOS database is used')
    parser.add_argument('--icd', help='Path to IBM Cloud Database credentials file. If not specified, then the internal AIOS database is used')
    parser.add_argument('--db2', help='Path to IBM DB2 credentials file')
    parser.add_argument('--wml', help='Path to IBM WML credentials file')
    parser.add_argument('--azure', help='Path to Microsoft Azure credentials file')
    parser.add_argument('--azure-deployment-name', help='Name of the deployment to use from Microsoft Azure ML Studio')
    parser.add_argument('--username', help='ICP username. Required if "icp" environment is chosen')
    parser.add_argument('--password', help='ICP password. Required if "icp" environment is chosen')
    parser.add_argument('--url', help='ICP url. Required if "icp" environment is chosen')
    parser.add_argument('--datamart-name', default='aiosfastpath', help='Specify data mart name, default is "aiosfastpath"')
    parser.add_argument('--history', default=0, help=argparse.SUPPRESS)
    parser.add_argument('--verbose', action='store_true', help='verbose flag')
    parser.add_argument('--version', action='version', version='%(prog)s {version}'.format(version=__version__))
    parser.add_argument('--bx', action='store_true', help=argparse.SUPPRESS)
    parser._action_groups.append(optionalArgs)

    # Optional parameters for LoadGenerator support
    lgArgs = parser._action_groups.pop()
    parser.add_argument('--lg_model', default='DrugSelectionModel', help='Default "DrugSelectionModel"', choices=['DrugSelectionModel','GermanCreditRiskModel','ScikitDigitsModel'])
    parser.add_argument('--lg_model_instance_num', default=1, help='Model instance number (default = 1)', type=int)
    parser.add_argument('--lg_score_requests', default=0, help='Number of score requests (default = 0)', type=int)
    parser.add_argument('--lg_scores_per_request', default=1, help='Number of scores per score request (default = 1)', type=int)
    parser.add_argument('--lg_explain_requests', default=0, help='Number of explain requests (default = 0)', type=int)
    parser.add_argument('--lg_max_explain_candidates', default=1000, help='Maximum number of candidate scores for explain (default = 1000)', type=int)
    parser.add_argument('--lg_explain_sync', action='store_true', help='User input initiates sending explain requests')
    parser.add_argument('--lg_pause', default=0.0, help='Pause in seconds between requests (default = 0.0)', type=float)
    parser.add_argument('--lg_verbose', action='store_true', help='Display individual request response times')
    parser.add_argument('--lg_checks', action='store_true', help='Trigger final fairness and quality checks')
    parser._action_groups.append(lgArgs)

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

    warn_if_outdated(name, __version__)

    return args

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
    wml_modelnames = ['DrugSelectionModel', 'GermanCreditRiskModel', 'ScikitDigitsModel']
    azure_modelnames = ['GermanCreditRiskModel']

    if args.ml_engine_type == 'azureml' and args.lg_model not in azure_modelnames:
        logger.error('Invalid model name specified. Only the following models are supported on Azure: {}'.format(azure_modelnames))
        exit(1)

    # Instantiate ML Client, setup and deploy models
    modeldata = get_modeldata_instance(args.lg_model, args, target_environment, args.lg_model_instance_num)
    aios_client = AIOSClientLG(aios_credentials, args.datamart_name, True, target_environment, modeldata, args.ml_engine_type)

    ml_engine = None
    if args.ml_engine_type == 'wml':
        ml_engine = WatsonMachineLearningEngine(ml_engine_credentials, target_environment, modeldata)
    elif args.ml_engine_type == 'azureml':
        ml_engine = AzureMachineLearningEngine(aios_client.get_azure_deployment_details(args.lg_azure_deployment_name))

    # AI Openscale operations
    aios_client.use_existing_binding(ml_engine_credentials)
    aios_client.use_existing_subscription(ml_engine)
    aios_client.generate_scoring_requests(args, ml_engine)
    aios_client.generate_explain_requests(args)
    aios_client.trigger_checks(args)

    logger.info('Process completed')
    logger.info('The AI OpenScale dashboard can be accessed at: {}/aiopenscale'.format(target_environment['aios_url']))
