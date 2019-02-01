from botocore.exceptions import ClientError
from more_itertools import first
from probator import get_aws_session, AWS_REGIONS, ProbatorError
from probator.config import dbconfig
from probator.constants import ConfigOption
from probator.database import db
from probator.log import auditlog
from probator.plugins import BaseAuditor
from probator.plugins.types.accounts import AWSAccount
from probator.plugins.types.resources import VPC
from probator.utils import get_template, get_resource_id
from probator.wrappers import retry


class VPCFlowLogsAuditor(BaseAuditor):
    name = 'VPC Flow Log Compliance'
    ns = 'auditor_vpc_flow_logs'
    interval = dbconfig.get('interval', ns, 60)
    role_name = dbconfig.get('role_name', ns, 'VpcFlowLogsRole')
    start_delay = 0
    options = (
        ConfigOption(name='enabled', default_value=False, type='bool', description='Enable the VPC Flow Logs auditor'),
        ConfigOption(name='interval', default_value=60, type='int', description='Run frequency in minutes'),
        ConfigOption(
            name='delivery_method',
            default_value={
                'enabled': ['s3'],
                'available': ['s3', 'cloudwatch-logs'],
                'max_items': 1,
                'min_items': 1
            },
            type='choice',
            description='Log delivery method'
        ),
        ConfigOption(
            name='traffic_type',
            default_value={
                'enabled': ['ALL'],
                'available': ['ALL', 'ACCEPT', 'REJECT'],
                'max_items': 1,
                'min_items': 1,
            },
            type='choice',
            description='Type of traffic to log'
        ),
        ConfigOption(name='bucket_name', default_value='', type='string', description='Name of S3 bucket to deliver logs to'),
        ConfigOption(name='role_name', default_value='VpcFlowLogsRole', type='str', description='IAM Role to use with CloudWatch Logs'),
    )

    def __init__(self):
        super().__init__()

        self.delivery_method = first(dbconfig.get(key='delivery_method', namespace=self.ns).get('enabled'))
        self.bucket_name = dbconfig.get(key='bucket_name', namespace=self.ns)
        self.role_name = dbconfig.get(key='role_name', namespace=self.ns)
        self.traffic_type = first(dbconfig.get(key='traffic_type', namespace=self.ns).get('enabled'))

    def run(self):
        """Main entry point for the auditor worker.

        Returns:
            `None`
        """
        accounts = list(AWSAccount.get_all(include_disabled=False).values())
        for account in accounts:
            self.manage_flow_logs(account)

    @retry
    def manage_flow_logs(self, account):
        self.log.debug(f'Updating VPC Flow Logs for {account.account_name}')

        session = get_aws_session(account)
        role_arn = self.confirm_iam_role(session, account) if self.delivery_method == 'cloud-watch-logs' else None

        for region in AWS_REGIONS:
            vpcs = VPC.get_all(account=account, location=region).values()

            for vpc in vpcs:
                self.create_vpc_flow_logs(account, region, vpc.id, role_arn)

        db.session.commit()

    @retry
    def create_vpc_flow_logs(self, account, region, vpc_id, iam_role_arn):
        """Create a new VPC Flow log

        Args:
            account (`AWSAccount`): Account to create the flow in
            region (`str`): Region to create the flow in
            vpc_id (`str`): ID of the VPC to create the flow for
            iam_role_arn (`str`): ARN of the IAM role used to post logs to the log group

        Returns:
            `None`
        """
        session = get_aws_session(account)
        ec2 = session.client('ec2', region)
        token = get_resource_id('flow-log-token', vpc_id)
        existing_flows = self.get_current_flow_logs(account, region, vpc_id)
        res = None

        if self.delivery_method == 's3':
            if not self.bucket_name:
                raise ProbatorError('You must provide a bucket name for S3 log delivery')

            bucket_arn = f'arn:aws:s3:::{self.bucket_name}/{account.account_name}/{region}/{vpc_id}'
            flow_key = '-'.join(['s3', self.traffic_type, bucket_arn])
            if flow_key in existing_flows:
                self.log.debug(f'Flow {flow_key} already exists')
                return

            res = ec2.create_flow_logs(
                ResourceIds=[vpc_id],
                ResourceType='VPC',
                TrafficType=self.traffic_type,
                LogDestinationType='s3',
                ClientToken=token,
                LogDestination=bucket_arn
            )

        elif self.delivery_method == 'cloudwatch-logs':
            flow_key = '-'.join(['cloud-watch-logs', self.traffic_type, vpc_id])
            if flow_key in existing_flows:
                self.log.debug(f'Flow {flow_key} already exists')
                return

            self.create_cloudwatch_log_group(account, region, vpc_id)
            res = ec2.create_flow_logs(
                ResourceIds=[vpc_id],
                ResourceType='VPC',
                TrafficType=self.traffic_type,
                LogDestinationType='cloud-watch-logs',
                LogGroupName=vpc_id,
                DeliverLogsPermissionArn=iam_role_arn,
                ClientToken=token,
            )

        if 'Unsuccessful' in res and len(res['Unsuccessful']):
            errors = ', '.join(error['Error']['Message'] for error in res['Unsuccessful'])
            self.log.warning(f'Failed created log flow for {account.account_name}/{region}/{vpc_id}: {errors}')
            return

        vpc = VPC.get(vpc_id)
        if vpc.update_resource(properties={'flow_logs_status': 'ACTIVE'}):
            db.session.add(vpc.resource)
            db.session.commit()
            self.log.info(f'Enabled VPC Logging {vpc}')

        auditlog(
            event='vpc_flow_logs.create_vpc_flow',
            actor=self.ns,
            data={
                'account': account.account_name,
                'region': region,
                'vpcId': vpc_id,
                'arn': iam_role_arn,
            }
        )

    @retry
    def get_current_flow_logs(self, account, region, vpc_id):
        """Return list of currently configured log flows for a given VPC

        Args:
            account (`AWSAccount`): AWSAccount object
            region (`str`): Region name
            vpc_id (`str`): VPC Id

        Returns:
            `list`
        """
        session = get_aws_session(account)
        ec2 = session.client('ec2', region_name=region)

        res = ec2.describe_flow_logs(
            Filters=[
                {
                    'Name': 'resource-id',
                    'Values': [vpc_id]
                }
            ]
        )

        flows = []
        for flow in res.get('FlowLogs', []):
            flow_type = flow['LogDestinationType']
            traffic_type = flow['TrafficType']
            destination = flow['LogDestination'] if 'LogDestination' in flow else flow['LogGroupName']

            flows.append('-'.join([flow_type, traffic_type, destination]))

        return flows

    @retry
    def confirm_iam_role(self, account):
        """Return the ARN of the IAM Role in the provided account

        Args:
            account (`AWSAccount`): AWS Account for role to be checked for / created in

        Returns:
            `str`
        """
        try:
            session = get_aws_session(account)
            iam = session.resource('iam')
            return iam.Role(self.role_name).arn

        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                return self.create_iam_role(account)
            else:
                raise

        except Exception as e:
            self.log.exception(f'Failed validating IAM role for VPC Flow Log Auditing for {e}')

    @retry
    def create_iam_role(self, account):
        """Create a new IAM role. Returns the ARN of the newly created role

        Args:
            account (:obj:`Account`): Account where to create the IAM role

        Returns:
            `str`
        """
        session = get_aws_session(account)
        iam = session.client('iam')
        trust = get_template('vpc_flow_logs_iam_role_trust.json').render()
        policy = get_template('vpc_flow_logs_role_policy.json').render()

        newrole = iam.create_role(
            Path='/',
            RoleName=self.role_name,
            AssumeRolePolicyDocument=trust
        )

        # Attach an inline policy to the role to avoid conflicts or hitting the Managed Policy Limit
        iam.put_role_policy(
            RoleName=self.role_name,
            PolicyName='VpcFlowPolicy',
            PolicyDocument=policy
        )

        self.log.debug(f'Created VPC Flow Logs role & policy for {account.account_name}')
        auditlog(
            event='vpc_flow_logs.create_iam_role',
            actor=self.ns,
            data={
                'account': account.account_name,
                'roleName': self.role_name,
                'trustRelationship': trust,
                'inlinePolicy': policy
            }
        )

        return newrole['Role']['Arn']

    @retry
    def create_cloudwatch_log_group(self, account, region, vpc_id):
        """Create a new CloudWatch log group based on the VPC Name if required

        Args:
            account (`AWSAccount`): Account to create the log group in
            region (`str`): Region to create the log group in
            vpc_id (`str`): VPC Id

        Returns:
            `bool`
        """
        session = get_aws_session(account)
        cw = session.client('logs', region)
        token = None
        log_groups = []

        while True:
            result = cw.describe_log_groups() if not token else cw.describe_log_groups(nextToken=token)
            token = result.get('nextToken')
            log_groups.extend([x['logGroupName'] for x in result.get('logGroups', [])])

            if not token:
                break

        if vpc_id not in log_groups:
            cw.create_log_group(logGroupName=vpc_id)

            vpc = VPC.get(vpc_id)
            vpc.set_property('vpc_flow_logs_log_group', vpc_id)

            self.log.info(f'Created log group {vpc}')
            auditlog(
                event='vpc_flow_logs.create_cw_log_group',
                actor=self.ns,
                data={
                    'account': account.account_name,
                    'region': region,
                    'log_group_name': vpc_id,
                    'vpc': vpc_id
                }
            )
        return True
