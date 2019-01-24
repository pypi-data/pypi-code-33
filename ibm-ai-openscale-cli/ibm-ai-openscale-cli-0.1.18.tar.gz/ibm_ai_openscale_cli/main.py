# coding=utf-8
from __future__ import print_function
import argparse
import logging
import urllib3
from retry import retry
from outdated import warn_if_outdated

from watson_machine_learning_client import WatsonMachineLearningAPIClient
from ibm_ai_openscale_cli.aios_client import AIOSClient
from ibm_ai_openscale_cli.ml_engines.watson_machine_learning.watson_machine_learning import WatsonMachineLearningEngine
from ibm_ai_openscale_cli.environments import Environments
from ibm_ai_openscale_cli.setup_classes.setup_env import setup_environment
from ibm_ai_openscale_cli.setup_classes.setup_services_cli import SetupIBMCloudServicesCli
from ibm_ai_openscale_cli.setup_classes.setup_services_rest import SetupIBMCloudServicesRest
from ibm_ai_openscale_cli.version import __version__
from ibm_ai_openscale_cli import logging_temp_file, name

from ibm_ai_openscale_cli.ml_engines.watson_machine_learning.models.drug_selection_model import DrugSelectionModel
from ibm_ai_openscale_cli.ml_engines.watson_machine_learning.models.german_credit_risk_model import GermanCreditRiskModel
from ibm_ai_openscale_cli.ml_engines.watson_machine_learning.models.scikit_digits_model import ScikitDigitsModel

logger = logging.getLogger(__name__)

def process_args():
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
    parser.add_argument('--cos', help='Path to IBM Cloud Object Storage credentials file')
    parser.add_argument('--username', help='ICP username. Required if "icp" environment is chosen')
    parser.add_argument('--password', help='ICP password. Required if "icp" environment is chosen')
    parser.add_argument('--url', help='ICP url. Required if "icp" environment is chosen')
    parser.add_argument('--datamart-name', default='aiosfastpath', help='Specify data mart name, default is "aiosfastpath"')
    parser.add_argument('--history', default=7, help='Days of history to preload. Default is 7', type=int)
    parser.add_argument('--verbose', action='store_true', help='verbose flag')
    parser.add_argument('--version', action='version', version='%(prog)s {version}'.format(version=__version__))
    parser.add_argument('--model', default='DrugSelectionModel', help='Model to set up with AIOS (default "DrugSelectionModel")', choices=['all', 'DrugSelectionModel','GermanCreditRiskModel','ScikitDigitsModel'])
    parser.add_argument('--bx', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--extend', action='store_true', help=argparse.SUPPRESS) # if true, do not delete existing datamart and binding
    parser.add_argument('--model-cleanup', action='store_true', help=argparse.SUPPRESS) # if true, only delete specified models and deployments, then exit
    parser.add_argument('--model-first-instance', default=1, help=argparse.SUPPRESS, type=int) # First "instance" (copy) of each model. Default 1 means to start with the base model instance
    parser.add_argument('--model-instances', default=1, help=argparse.SUPPRESS, type=int) # Number of additional instances beyond the first.
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

    warn_if_outdated(name, __version__)

    return args

def main():

    logger.info('ibm-ai-openscale-cli-{}'.format(__version__))
    logger.info('Log file: {0}'.format(logging_temp_file.name))

    args = process_args()

    if args.env == 'icp':
        logger.info('SSL verification is not used for requests against ICP Environment, disabling "InsecureRequestWarning"')
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    target_environment = Environments(args).getEnvironment()

    # setup IBM Cloud services and database
    ibm_cloud_services = None
    setup_environment(args, target_environment)
    if args.bx:
        ibm_cloud_services = SetupIBMCloudServicesCli(args, target_environment)
    else:
        ibm_cloud_services = SetupIBMCloudServicesRest(args, target_environment)
    aios_credentials = ibm_cloud_services.setup_aios()
    wml_credentials = ibm_cloud_services.setup_wml()
    postgres_credentials = ibm_cloud_services.setup_postgres_database()
    icd_credentials = ibm_cloud_services.setup_icd_database()
    db2_credentials = ibm_cloud_services.setup_db2_database()

    database_credentials = None
    if postgres_credentials is not None:
        database_credentials = postgres_credentials
    elif icd_credentials is not None:
        database_credentials = icd_credentials
    elif db2_credentials is not None:
        database_credentials = db2_credentials

    # Instantiate ML Client, setup and deploy models
    modelnames = ['DrugSelectionModel', 'GermanCreditRiskModel', 'ScikitDigitsModel']
    if args.model != 'all':
        modelnames = [args.model]
    model = None
    run_once = True
    if args.extend:
        run_once = False
    for modelname in modelnames:
        logger.info('--------------------------------------------------------------------------------')
        logger.info('Model: {}'.format(modelname))
        logger.info('--------------------------------------------------------------------------------')
        for model_instance_num in range(args.model_first_instance, args.model_first_instance + args.model_instances):
            # Model instance
            if modelname == 'DrugSelectionModel':
                model = DrugSelectionModel(target_environment, args.history, model_instance_num)
            elif modelname == 'GermanCreditRiskModel':
                model = GermanCreditRiskModel(target_environment, args.history, model_instance_num)
                if args.env != 'icp' and not args.model_cleanup:
                    cos_credentials = ibm_cloud_services.setup_cos()
                    model.update_training_metadata(cos_credentials)
            elif modelname == 'ScikitDigitsModel':
                model = ScikitDigitsModel(target_environment, 0, model_instance_num) # temporarily, don't load history

            # WML Operations
            if args.env == 'icp': # reset the wml credentials for icp
                wml_credentials = ibm_cloud_services.setup_wml()
            wml_engine = WatsonMachineLearningEngine(wml_credentials, target_environment, model)
            if args.model_cleanup:
                wml_engine.model_cleanup()
                continue # skip all AIOS datamart operations
            else:
                wml_model_deployment = wml_engine.create_model_and_deploy()

            # AI Openscale operations
            aios_client = AIOSClient(aios_credentials, args.datamart_name, target_environment, model)
            if run_once:
                run_once = False
                aios_client.clean_datamart()
                aios_client.create_datamart(database_credentials)
                ml_binding_guid = aios_client.bind_mlinstance(wml_credentials)
            else:
                ml_binding_guid = aios_client.get_existing_binding(wml_credentials)
            model_subscription = aios_client.subscribe_to_model_deployment(wml_model_deployment)
            aios_client.configure_subscription(wml_model_deployment, model_subscription)
            aios_client.generate_sample_scoring(wml_model_deployment, ml_binding_guid, model_subscription)

    logger.info('Process completed')
    dashboard_url = target_environment['aios_url']
    if dashboard_url.startswith('https://api.'):
        dashboard_url = dashboard_url.replace('https://api.', 'https://')
    logger.info('The AI OpenScale dashboard can be accessed at: {}/aiopenscale'.format(dashboard_url))
