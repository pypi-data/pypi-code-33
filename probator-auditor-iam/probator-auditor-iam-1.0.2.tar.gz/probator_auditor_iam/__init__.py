import copy
import json
import os
import shutil
from tempfile import mkdtemp

from botocore.exceptions import ClientError
from git import Repo
from more_itertools import first
from probator import get_aws_session, get_local_aws_session
from probator.config import dbconfig
from probator.constants import ConfigOption
from probator.exceptions import ProbatorError
from probator.log import auditlog
from probator.plugins import BaseAuditor
from probator.plugins.types.accounts import AWSAccount
from probator.wrappers import retry

DEFAULT_TRUST = {
    'Version': '2012-10-17',
    'Statement': [
        {
            'Effect': 'Allow',
            'Principal': {
                'Service': 'ec2.amazonaws.com'
            },
            'Action': 'sts:AssumeRole'
        }
    ]
}


class IAMAuditor(BaseAuditor):
    """Validate and apply IAM policies for AWS Accounts"""
    name = 'IAM'
    ns = 'auditor_iam'
    interval = dbconfig.get('interval', ns, 30)
    start_delay = 0

    options = (
        ConfigOption(name='enabled', default_value=False, type='bool', description='Enable the IAM roles and policy auditor'),
        ConfigOption(name='interval', default_value=30, type='int', description='How often the auditor executes, in minutes'),
        ConfigOption(name='manage_roles', default_value=True, type='bool', description='Enable management of IAM roles'),
        ConfigOption(
            name='roles',
            default_value={},
            type='json',
            description='JSON document with roles to push to accounts. See documentation for examples'
        ),
        ConfigOption(
            name='delete_inline_policies',
            default_value=False,
            type='bool',
            description='Delete inline policies from existing roles'
        ),
        ConfigOption(name='hostname', default_value='', type='string', description='Git server hostname'),
        ConfigOption(name='repository', default_value='', type='string', description='Path of the Git repository'),
        ConfigOption(name='disable_ssl_verify', default_value=False, type='bool', description='Disable SSL certificate validation'),
        ConfigOption(
            name='max_session_duration',
            default_value=8,
            type='int',
            description='AssumeRole MaxSessionDuration timeout in hours'
        ),
        ConfigOption(
            name='authentication_type',
            default_value={
                'enabled': ['oauth-token'],
                'available': ['oauth-token', 'username-password'],
                'max_items': 1,
                'min_items': 1
            },
            type='choice',
            description='Authentication type'
        ),
        ConfigOption(name='oauth_token', default_value='', type='string', description='OAuth2 authentication token'),
        ConfigOption(name='username', default_value='', type='string', description='Username'),
        ConfigOption(name='password', default_value='', type='string', description='Password'),
    )

    def __init__(self):
        super().__init__()

        self.manage_roles = dbconfig.get('manage_roles', self.ns)
        self.roles = dbconfig.get('roles', self.ns)
        self.delete_inline_policies = dbconfig.get('delete_inline_policies', self.ns)
        self.hostname = dbconfig.get('hostname', self.ns)
        self.repo = dbconfig.get('repository', self.ns)
        self.disable_ssl_verify = dbconfig.get('disable_ssl_verify', self.ns)
        self.max_session_duration = dbconfig.get('max_session_duration', self.ns) * 60 * 60
        self.authentication_type = first(dbconfig.get('authentication_type', self.ns).get('enabled'))
        self.oauth_token = dbconfig.get('oauth_token', self.ns)
        self.username = dbconfig.get('username', self.ns)
        self.password = dbconfig.get('password', self.ns)
        self.git_policies = {}
        self.aws_managed_policies = {}

    def run(self):
        """Iterate through all AWS accounts and apply roles and policies from Github

        Returns:
            `None`
        """
        self.git_policies = self.get_policies_from_git()
        self.manage_policies()

    def manage_policies(self):
        accounts = list(AWSAccount.get_all(include_disabled=False).values())
        self.aws_managed_policies = {
            policy['PolicyName']: policy for policy in self.get_policies_from_aws(get_local_aws_session().client('iam'), 'AWS')
        }

        for account in accounts:
            # List all policies and roles from AWS, and generate a list of policies from Git
            sess = get_aws_session(account)
            iam = sess.client('iam')

            aws_roles = {role['RoleName']: role for role in self.get_roles(iam)}
            aws_policies = {policy['PolicyName']: policy for policy in self.get_policies_from_aws(iam)}
            account_policies = copy.deepcopy(self.git_policies['GLOBAL'])

            if account.account_name in self.git_policies:
                for role in self.git_policies[account.account_name]:
                    account_policies.update(self.git_policies[account.account_name][role])

            aws_policies.update(self.check_policies(account, account_policies, aws_policies))
            self.check_roles(account, aws_policies, aws_roles)

    @retry
    def check_policies(self, account, account_policies, aws_policies):
        """Iterate through the policies of a specific account and create or update the policy if its missing or
        does not match the policy documents from Git. Returns a dict of all the policies added to the account
        (does not include updated policies)

        Args:
            account (:obj:`Account`): Account to check policies for
            account_policies (`dict` of `str`: `dict`): A dictionary containing all the policies for the specific
            account
            aws_policies (`dict` of `str`: `dict`): A dictionary containing the non-AWS managed policies on the account

        Returns:
            :obj:`dict` of `str`: `str`
        """
        self.log.debug(f'Fetching policies for {account.account_name}')
        sess = get_aws_session(account)
        iam = sess.client('iam')
        added = {}

        for policy_name, account_policy in account_policies.items():
            # policies pulled from github a likely bytes and need to be converted
            if isinstance(account_policy, bytes):
                account_policy = account_policy.decode('utf-8')

            # Using re.sub instead of format since format breaks on the curly braces of json
            gitpol = json.loads(account_policy)

            if policy_name in aws_policies:
                pol = aws_policies[policy_name]
                awspol = iam.get_policy_version(
                    PolicyArn=pol['Arn'],
                    VersionId=pol['DefaultVersionId']
                )['PolicyVersion']['Document']

                if awspol != gitpol:
                    self.log.warn(f'IAM Policy {policy_name} on {account.account_name} does not match Git policy documents, updating')
                    self.create_policy(account, iam, json.dumps(gitpol, indent=4), policy_name, arn=pol['Arn'])

            else:
                self.log.warn(f'IAM Policy missing: {policy_name}/{account.account_name}')
                response = self.create_policy(account, iam, json.dumps(gitpol), policy_name)
                added[policy_name] = response['Policy']

        return added

    @retry
    def check_roles(self, account, aws_policies, aws_roles):
        """Iterate through the roles of a specific account and create or update the roles if they're missing or
        does not match the roles from Git.

        Args:
            account (:obj:`Account`): The account to check roles on
            aws_policies (:obj:`dict` of `str`: `dict`): A dictionary containing all the policies for the specific
            account
            aws_roles (:obj:`dict` of `str`: `dict`): A dictionary containing all the roles for the specific account

        Returns:
            `None`
        """
        self.log.debug(f'Checking roles for {account.account_name}')
        sess = get_aws_session(account)
        iam = sess.client('iam')

        # Build a list of default role policies and extra account specific role policies
        account_roles = copy.deepcopy(self.roles)
        if account.account_name in self.git_policies:
            for role in self.git_policies[account.account_name]:
                if role in account_roles:
                    account_roles[role]['policies'] += list(self.git_policies[account.account_name][role].keys())

        for role_name, data in list(account_roles.items()):
            trust_policy = json.dumps(data.get('trust', None), indent=4, sort_keys=True)
            if not trust_policy or trust_policy in ('null', '{}'):
                trust_policy = json.dumps(DEFAULT_TRUST, indent=4, sort_keys=True)

            if role_name not in aws_roles:
                iam.create_role(
                    Path='/',
                    RoleName=role_name,
                    AssumeRolePolicyDocument=trust_policy,
                    MaxSessionDuration=self.max_session_duration
                )
                self.log.info(f'Created role {account.account_name}/{role_name}')
            else:
                try:
                    if aws_roles[role_name]['MaxSessionDuration'] != self.max_session_duration:
                        iam.update_role(
                            RoleName=role_name,
                            MaxSessionDuration=self.max_session_duration
                        )
                        self.log.debug(f'Updated MaxSessionDuration for {account.account_name}/{role_name}')

                    current_trust_policy = json.dumps(aws_roles[role_name]['AssumeRolePolicyDocument'], indent=4, sort_keys=True)
                    if current_trust_policy != trust_policy:
                        iam.update_assume_role_policy(
                            RoleName=role_name,
                            PolicyDocument=trust_policy
                        )
                        self.log.debug(f'Updating assume role trust for {account.account_name}/{role_name}')

                except ClientError:
                    self.log.exception(f'Unable to adjust MaxSessionDuration for {account.account_name} / {role_name}')

            aws_role_policies = [
                x['PolicyName'] for x in iam.list_attached_role_policies(RoleName=role_name).get('AttachedPolicies')
            ]
            aws_role_inline_policies = iam.list_role_policies(RoleName=role_name).get('PolicyNames')
            cfg_role_policies = data['policies']

            missing_policies = list(set(cfg_role_policies) - set(aws_role_policies))
            extra_policies = list(set(aws_role_policies) - set(cfg_role_policies))

            if aws_role_inline_policies:
                self.log.info(
                    f'IAM Role {account.account_name} / {role_name} has extra inline policies: {", ".join(aws_role_inline_policies)}'
                )

                if self.delete_inline_policies and self.manage_roles:
                    for policy in aws_role_inline_policies:
                        iam.delete_role_policy(RoleName=role_name, PolicyName=policy)
                        auditlog(
                            event='iam.check_roles.delete_inline_role_policy',
                            actor=self.ns,
                            data={
                                'account': account.account_name,
                                'roleName': role_name,
                                'policy': policy
                            }
                        )

            if missing_policies:
                self.log.info(f'IAM Role {account.account_name} / {role_name} is missing policies: {", ".join(missing_policies)}')
                if self.manage_roles:
                    for policy in missing_policies:
                        iam.attach_role_policy(RoleName=role_name, PolicyArn=aws_policies[policy]['Arn'])
                        auditlog(
                            event='iam.check_roles.attach_role_policy',
                            actor=self.ns,
                            data={
                                'account': account.account_name,
                                'roleName': role_name,
                                'policyArn': aws_policies[policy]['Arn']
                            }
                        )

            if extra_policies:
                self.log.info(
                    f'IAM Role {account.account_name} / {role_name} has the following extra policies applied: {", ".join(extra_policies)}'
                )

                for policy in extra_policies:
                    if policy in aws_policies:
                        pol_arn = aws_policies[policy]['Arn']

                    elif policy in self.aws_managed_policies:
                        pol_arn = self.aws_managed_policies[policy]['Arn']

                    else:
                        pol_arn = None
                        self.log.info(f'IAM Role {account.account_name} / {role_name} has an unknown policy attached: {policy}')

                    if self.manage_roles and pol_arn:
                        iam.detach_role_policy(RoleName=role_name, PolicyArn=pol_arn)
                        auditlog(
                            event='iam.check_roles.detach_role_policy',
                            actor=self.ns,
                            data={
                                'account': account.account_name,
                                'roleName': role_name,
                                'policyArn': pol_arn
                            }
                        )

    def get_policies_from_git(self):
        """Retrieve policies from the Git repo. Returns a dictionary containing all the roles and policies

        Returns:
            :obj:`dict` of `str`: `dict`
        """
        fldr = mkdtemp()
        try:
            url = self.get_git_url()

            policies = {'GLOBAL': {}}
            if self.disable_ssl_verify:
                os.environ['GIT_SSL_NO_VERIFY'] = '1'

            repo = Repo.clone_from(url, fldr)
            for obj in repo.head.commit.tree:
                name, ext = os.path.splitext(obj.name)

                # Read the standard policies
                if ext == '.json':
                    policies['GLOBAL'][name] = obj.data_stream.read()

                # Read any account role specific policies
                if name == 'roles' and obj.type == 'tree':
                    for account in [x for x in obj.trees]:
                        for role in [x for x in account.trees]:
                            role_policies = {
                                pol.name.replace('.json', ''): pol.data_stream.read() for pol in role.blobs if pol.name.endswith('.json')
                            }

                            if account.name in policies:
                                if role.name in policies[account.name]:
                                    policies[account.name][role.name] += role_policies

                                else:
                                    policies[account.name][role.name] = role_policies
                            else:
                                policies[account.name] = {
                                    role.name: role_policies
                                }

            return policies
        finally:
            if os.path.exists(fldr) and os.path.isdir(fldr):
                shutil.rmtree(fldr)

    @staticmethod
    def get_policies_from_aws(client, scope='Local'):
        """Returns a list of all the policies currently applied to an AWS Account. Returns a list containing all the
        policies for the specified scope

        Args:
            client (:obj:`boto3.session.Session`): A boto3 Session object
            scope (`str`): The policy scope to use. Default: Local

        Returns:
            :obj:`list` of `dict`
        """
        done = False
        marker = None
        policies = []

        while not done:
            if marker:
                response = client.list_policies(Marker=marker, Scope=scope)
            else:
                response = client.list_policies(Scope=scope)

            policies += response.get('Policies', [])

            if response['IsTruncated']:
                marker = response['Marker']
            else:
                done = True

        return policies

    @staticmethod
    def get_roles(client):
        """Returns a list of all the roles for an account. Returns a list containing all the roles for the account.

        Args:
            client (:obj:`boto3.session.Session`): A boto3 Session object

        Returns:
            :obj:`list` of `dict`
        """
        done = False
        marker = None
        roles = []

        while not done:
            if marker:
                response = client.list_roles(Marker=marker)
            else:
                response = client.list_roles()

            roles += response.get('Roles', [])

            if response['IsTruncated']:
                marker = response['Marker']
            else:
                done = True

        return roles

    def create_policy(self, account, client, document, name, arn=None):
        """Create a new IAM policy.

        If the policy already exists, a new version will be added and if needed the oldest policy version not in use
        will be removed. Returns a dictionary containing the policy or version information

        Args:
            account (:obj:`Account`): Account to create the policy on
            client (:obj:`boto3.client`): A boto3 client object
            document (`str`): Policy document
            name (`str`): Name of the policy to create / update
            arn (`str`): Optional ARN for the policy to update

        Returns:
            `dict`
        """
        if not arn and not name:
            raise ValueError('create_policy must be called with either arn or name in the argument list')

        if arn:
            response = client.list_policy_versions(PolicyArn=arn)

            # If we're at the max of the 5 possible versions, remove the oldest version that is not
            # the currently active policy
            if len(response['Versions']) >= 5:
                version = first([
                    ver for ver in sorted(response['Versions'], key=lambda k: k['CreateDate']) if not ver['IsDefaultVersion']
                ])

                self.log.info(f'Deleting oldest IAM Policy version {arn} / {version["VersionId"]}')
                client.delete_policy_version(PolicyArn=arn, VersionId=version['VersionId'])
                auditlog(
                    event='iam.check_roles.delete_policy_version',
                    actor=self.ns,
                    data={
                        'account': account.account_name,
                        'policyName': name,
                        'policyArn': arn,
                        'versionId': version['VersionId']
                    }
                )

            res = client.create_policy_version(
                PolicyArn=arn,
                PolicyDocument=document,
                SetAsDefault=True
            )
        else:
            res = client.create_policy(
                PolicyName=name,
                PolicyDocument=document
            )

        auditlog(
            event='iam.check_roles.create_policy',
            actor=self.ns,
            data={
                'account': account.account_name,
                'policyName': name,
                'policyArn': arn
            }
        )
        return res

    def get_git_url(self):
        if not self.repo:
            raise ProbatorError('Missing repository, unable to continue')

        if self.authentication_type == 'oauth-token':
            if not self.oauth_token:
                raise ProbatorError('Missing oauth_token is required when using oauth-token authentication')

            return f'https://{self.oauth_token}@{self.hostname}/{self.repo}'

        elif self.authentication_type == 'username-password':
            if not (self.username and self.password):
                raise ProbatorError('Missing username and/or password. Required when using username-password authentication')

            return f'https://{self.username}:{self.password}@{self.hostname}/{self.repo}'

        else:
            raise ProbatorError(f'Invalid git authentication type {self.authentication_type}')
