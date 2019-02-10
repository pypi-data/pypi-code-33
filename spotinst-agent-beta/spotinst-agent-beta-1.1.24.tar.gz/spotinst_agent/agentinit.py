# load credentials
import logging
import utils
from utils import safe_read_simple_url, safe_get_json

"""
This is for Elastic group spotinst-agent specific
"""


def getAwsInstanceDetails(config, authentication_token, account_id, log, debug):
    instance_details = None
    if debug:
        # for debug
        log.warning("spotinst-agent is running with mock credentials for debug purposes")
        instance_details = {'cloud_provider': 'AWS', 'instance_id': 'i-1234567890',
                            'spectrum_dimensions': ['instance_id'],
                            'authentication_token': 'DUMMY-TOKEN'}
    locator_url = config['aws_instance_id_locator_url']
    instance_id = getAwsInstanceId(locator_url, log)
    if instance_id and authentication_token:
        instance_details = {'cloud_provider': 'AWS', 'instance_id': instance_id,
                            'authentication_token': authentication_token,
                            'spectrum_dimensions': ['instance_id'],
                            'account_id': account_id}
    return instance_details


def getGcpInstanceDetails(config, authentication_token, account_id, log, debug):
    instance_details = None
    if debug:
        # for debug
        log.warning("spotinst-agent is running with mock credentials for debug purposes")
        instance_details = {'cloud_provider': 'GCP', 'instance_name': 'instance-1',
                            'spectrum_dimensions': ['instance_name'],
                            'authentication_token': 'DUMMY-TOKEN'}

    locator_url = config['gcp_instance_metadata_url']

    instance_name_path_metadata = config['gcp_instance_name']
    instance_name = getGcpInstanceMetadata(locator_url, instance_name_path_metadata, log)

    if instance_name and authentication_token:
        instance_details = {'cloud_provider': 'GCP', 'instance_name': instance_name,
                            'authentication_token': authentication_token,
                            'spectrum_dimensions': ['instance_name'],
                            'account_id': account_id}
    return instance_details


def getAzureInstanceDetails(config, authentication_token, account_id, log, debug):
    instance_details = None
    if debug:
        # for debug
        log.warning("spotinst-agent is running with mock credentials for debug purposes")
        instance_details = {'cloud_provider': 'Azure', 'pool_id': 'dummy_pool_id', 'node_id': 'dummy_node_id',
                            'instance_id': 'dummy_instance_id', 'authentication_token': 'DUMMY-TOKEN',
                            'spectrum_dimensions': ['pool_id', 'node_id']}
    poolIdNodeId = getAzurePoolIdAndNodeId(config, log)
    pool_id = poolIdNodeId[0]
    node_id = poolIdNodeId[1]

    locator_url = config['azure_instance_id_locator_url']
    instance_id = getAzureInstanceId(locator_url, log)

    if pool_id and node_id:
        if authentication_token:
            instance_details = {'cloud_provider': 'Azure', 'pool_id': pool_id, 'node_id': node_id,
                                'instance_id': instance_id, 'authentication_token': authentication_token,
                                'account_id': account_id, 'spectrum_dimensions': ['pool_id', 'node_id']}
        else:
            log.error("Bad authentication_token")
    else:
        log.error("Bad init of Azure linux instance details pool id, node id")
    return instance_details


def init__configuration(config, cloud_provider, debug=False):
    instance_details = None
    log = logging.getLogger('spotinst-agent')

    creds = utils.retrieve_creds()
    authentication_token = creds["token"]
    account_id = creds["account_id"]

    if cloud_provider.lower() == 'azure':
        instance_details = getAzureInstanceDetails(config, authentication_token, account_id, log, debug)
    elif cloud_provider.lower() == 'gcp':
        instance_details = getGcpInstanceDetails(config, authentication_token, account_id, log, debug)
    else:
        instance_details = getAwsInstanceDetails(config, authentication_token, account_id, log, debug)
    return instance_details


def getAwsInstanceId(locator_url, log):
    response = None
    if locator_url:
        if locator_url.startswith("http://"):
            response = safe_read_simple_url(locator_url, log)
            response = str(response)

        else:
            with open(locator_url) as file:
                response = file.read().splitlines()[0]

        log.debug("found instance id - {}".format(response))
        if not response:
            log.error("response is null, can't get instance id")
            return None

    return response


def getGcpInstanceMetadata(locator_url, path_params, log):
    response = None
    if locator_url:
        if locator_url.startswith("http://"):
            response = utils.get_gcp_metadata(locator_url, path_params, log)
            response = str(response)

        log.debug("found instance id - {}".format(response))
        if not response:
            log.error("response is null, can't get instance metadata")
            return None

    return response


def getAzureInstanceId(locator_url, log):
    response = None
    if locator_url:
        if locator_url.startswith("http://"):
            response = utils.get_azure_metadata(locator_url, log)
            response = str(response)

        else:
            with open(locator_url) as file:
                response = file.read().splitlines()[0]

        log.debug("found instance id - {}".format(response))
        if not response:
            log.error("response is null, can't get instance id")

    return response


def getAzurePoolIdAndNodeId(config, log):
    nodeIdFile = None
    poolIdFile = None
    response = (None, None)
    try:
        node_id_path = config['azure_node_id_path']
        pool_id_path = config['azure_pool_id_path']

        nodeIdFile = open(node_id_path, 'r')
        nodeId = nodeIdFile.read().strip('\n')
        nodeIdFile.close()

        poolIdFile = open(pool_id_path, 'r')
        poolId = poolIdFile.read().strip('\n')
        poolIdFile.close()

        response = (poolId, nodeId)
    except IOError:
        if nodeIdFile is not None:
            nodeIdFile.close()
        if poolIdFile is not None:
            poolIdFile.close()
        log.warn("Failed to get pool id and node id from set paths")
    return response
