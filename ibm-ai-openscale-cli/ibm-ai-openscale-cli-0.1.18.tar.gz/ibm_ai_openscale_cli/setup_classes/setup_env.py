# coding=utf-8
from __future__ import print_function
from ibm_ai_openscale_cli.utility_classes.utils import executeCommand
import logging
logger = logging.getLogger(__name__)
def setup_environment(args, env):
    if args.bx:
        logger.debug('Using IBM Cloud CLI to setup IBM Cloud services')
        executeCommand('bx config --check-version=false')
        executeCommand('bx login --apikey "{}" -a "{}"'.format(args.apikey, env['api']))
        logger.debug('Target resource-group "%s"', args.resource_group)
        executeCommand('bx target -g "{}"'.format(args.resource_group))
    elif args.env[:3].lower() == 'icp':
        logger.debug('Targeting ICP environment, SSL Certificate check will be disabled')
    else:
        logger.debug('Using REST API to setup IBM Cloud services')
