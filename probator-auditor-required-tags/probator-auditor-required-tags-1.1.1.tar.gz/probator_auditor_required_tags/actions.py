import logging
import re
from functools import wraps

from botocore.exceptions import ClientError
from probator import get_aws_session
from probator.plugins.types.accounts import AWSAccount

logger = logging.getLogger(__name__)
RGX_IAM_ERROR = re.compile(r'when calling the (.*?) operation')


def perm_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except ClientError as ex:
            if ex.response['Error']['Code'] == 'UnauthorizedOperation':
                m = RGX_IAM_ERROR.search(str(ex))
                if not m:
                    logger.warning(f'Permission error in {func.__name__}: {ex}')
                else:
                    perm = m.group(1)
                    logger.warning(f'Probator isnt permitted to perform the {perm} action, please add it to the probator IAM role')
    return wrapper


@perm_error
def aws_ec2_instance_stop(instance):
    session = get_aws_session(AWSAccount(instance.account))
    ec2 = session.resource('ec2', region_name=instance.location)

    inst = ec2.Instance(instance.id)
    if inst.state['Code'] not in (32, 48, 64, 80):
        inst.stop()
        logger.debug(f'Stopped EC2 Instance {instance}')
    else:
        logger.debug(f'EC2 Instance already stopped: {instance}')


@perm_error
def aws_ec2_instance_remove(instance):
    session = get_aws_session(AWSAccount(instance.account))
    ec2 = session.resource('ec2', region_name=instance.location)

    inst = ec2.Instance(instance.id)
    attr = inst.describe_attribute(Attribute='disableApiTermination')
    if attr['DisableApiTermination']['Value']:
        inst.modify_attribute(DisableApiTermination={'Value': False})
        logger.debug(f'Disabled instance termination protection for {instance}')

    if inst.state['Code'] != 48:
        inst.terminate()
        logger.debug(f'Terminated EC2 Instance {instance}')
    else:
        logger.debug(f'EC2 Instance already terminated: {instance}')
