"""BITS AWS Account class file."""

import boto3
import json


class Account(object):
    """BITS AWS Account class."""

    def __init__(self):
        """Initialize an AWS Account instance."""
        self.aws = None
        self.verbose = False

        # basic aws account attributes
        self.arn = None
        self.email = None
        self.id = None
        self.joined_method = None
        self.joined_timestamp = None
        self.name = None
        self.status = None
        self.suspended = False

        # aws organization (parent)
        self.organization_id = None

        # additional account attributes
        self.alias = None
        self.details = None
        self.summary = None

        # additional aws data
        self.groups = []
        self.policies = []
        self.roles = []
        self.users = []

        # bitsdb data
        self.admins = []
        # self.approvers = []
        # self.saml_users = []
        # self.owners = []

        # bitsdb budget data
        self.budget_start = None
        self.budget_end = None
        self.cost_object = None
        self.monthly_budget = None
        self.total_budget = None

        # authentication credentials
        self.credentials = None

        # clients
        self.s3_client = None
        self.iam_client = None
        self.sts_client = None

        # resources
        self.iam = None

    def __repr__(self):
        """Return a human-reable representation of the instance."""
        account = '<AWS Account - %s: %s [%s]>' % (
            self.id,
            self.name,
            self.alias,
        )
        return account

    #
    # Create from an AWS Account record
    #
    def from_aws(
        self,
        aws,
        account,
        include_alias=False,
        include_details=False,
        include_summary=False,
    ):
        """Return an account based off AWS data."""
        self.aws = aws
        self.verbose = aws.verbose

        # set account details
        self.arn = account.get('Arn')
        self.email = account.get('Email')
        self.id = account.get('Id')
        self.joined_method = account.get('JoinedMethod')
        self.joined_timestamp = account.get('JoinedTimestamp')
        self.name = account.get('Name')
        self.status = account.get('Status')

        # set organization_id (parent)
        if self.id != self.aws.root_account:
            self.organization_id = self.aws.root_account

        # check status
        if self.status == 'SUSPENDED':
            self.suspended = True
            return self

        # get account credentials
        self.credentials = self.get_credentials()

        # create clients
        self.iam_client = boto3.client(
            'iam',
            aws_access_key_id=self.credentials['AccessKeyId'],
            aws_secret_access_key=self.credentials['SecretAccessKey'],
            aws_session_token=self.credentials['SessionToken'],
        )

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.credentials['AccessKeyId'],
            aws_secret_access_key=self.credentials['SecretAccessKey'],
            aws_session_token=self.credentials['SessionToken'],
        )

        self.sts_client = boto3.client(
            'sts',
            aws_access_key_id=self.credentials['AccessKeyId'],
            aws_secret_access_key=self.credentials['SecretAccessKey'],
            aws_session_token=self.credentials['SessionToken'],
        )

        # create resources
        self.iam = boto3.resource(
            'iam',
            aws_access_key_id=self.credentials['AccessKeyId'],
            aws_secret_access_key=self.credentials['SecretAccessKey'],
            aws_session_token=self.credentials['SessionToken'],
        )

        # get account alias from aws
        if include_alias:
            self.refresh_alias()

        # get account details
        if include_details:
            self.refresh_details()

        # get account summary
        if include_summary:
            self.refresh_summary()

        return self

    def from_bitsdb(
        self,
        aws,
        account,
        include_alias=True,
        include_details=False,
        include_summary=False,
    ):
        """Return an account based off a BITSdb record."""
        self.aws = aws
        self.verbose = aws.verbose

        # set account details
        self.arn = account.get('arn')
        self.admins = account.get('admins')

        self.email = account.get('email')
        self.id = account.get('id')
        # self.joined_method = account.get('joined_method')
        # self.joined_timestamp = account.get('joined_timestamp')
        self.organization_id = account.get('organization_id')
        self.name = account.get('name')
        self.status = account.get('status')

        # set organization_id (parent)
        if self.id != self.aws.root_account:
            self.organization_id = self.aws.root_account

        # check status
        if self.status == 'SUSPENDED':
            self.suspended = True
            return self

        # get account credentials
        self.credentials = self.get_credentials()

        # create clients
        self.iam_client = boto3.client(
            'iam',
            aws_access_key_id=self.credentials['AccessKeyId'],
            aws_secret_access_key=self.credentials['SecretAccessKey'],
            aws_session_token=self.credentials['SessionToken'],
        )

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.credentials['AccessKeyId'],
            aws_secret_access_key=self.credentials['SecretAccessKey'],
            aws_session_token=self.credentials['SessionToken'],
        )

        self.sts_client = boto3.client(
            'sts',
            aws_access_key_id=self.credentials['AccessKeyId'],
            aws_secret_access_key=self.credentials['SecretAccessKey'],
            aws_session_token=self.credentials['SessionToken'],
        )

        # create resources
        self.iam = boto3.resource(
            'iam',
            aws_access_key_id=self.credentials['AccessKeyId'],
            aws_secret_access_key=self.credentials['SecretAccessKey'],
            aws_session_token=self.credentials['SessionToken'],
        )

        # set account alias
        self.alias = account.get('alias')

        # get account details
        if include_details:
            self.refresh_details()

        # get account summary
        if include_summary:
            self.refresh_summary()

        return self

    #
    # Output record for BITSdb API
    #
    def to_bitsdb(self):
        """Return a BITSDB AwsAccount record."""
        account = {
            'kind': 'aws#account',
            'id': self.id,
            'account_id': self.id,
            'alias': self.alias,
            'arn': self.arn,
            'email': self.email,
            'name': self.name,
            'organization_id': self.organization_id,
            'status': self.status,
            'admins': self.admins,
        }
        return account

    #
    # Account ID
    #
    def get_account_id(self):
        """Return the email address for the account."""
        return self.get_caller_identity().get('Account')

    #
    # Caller Identity
    #
    def get_caller_identity(self):
        """Return the identity of the caller."""
        return self.sts_client.get_caller_identity()

    #
    # Credentials
    #
    def get_credentials(self):
        """Return credentials for this account."""
        role_name = 'role/OrganizationAccountAccessRole'
        role = 'arn:aws:iam::%s:%s' % (
            self.id,
            role_name,
        )
        return self.aws.assume_role(role, 'iam')

    #
    # Account Authorization Details
    #
    def get_details(self):
        """Return details for this account."""
        # get auth details
        details = self.iam_client.get_account_authorization_details(
            MaxItems=1000
        )

        # retrieve additional pages of details
        while details['IsTruncated']:

            # get next page of results
            more = self.iam_client.get_account_authorization_details(
                Marker=details['Marker'],
                MaxItems=1000,
            )

            # merge lists
            for key in sorted(more):
                if key in [
                        'GroupDetailList',
                        'Policies',
                        'RoleDetailList',
                        'UserDetailList',
                ]:
                    more[key] += details[key]

            details = more

        return details

    def refresh_alias(self):
        """Refresh alias from AWS."""
        self.alias = self.get_alias()

    def refresh_details(self):
        """Refresh account details from AWS."""
        self.details = self.get_details()
        self.groups = self.details['GroupDetailList']
        self.policies = self.details['Policies']
        self.roles = self.details['RoleDetailList']
        self.users = self.details['UserDetailList']

    def refresh_summary(self):
        """Refresh the account summary from AWS."""
        self.summary = self.get_summary()

    #
    # Account Summary
    #
    def get_summary(self):
        """Return the summary information for this account."""
        summary = self.iam.AccountSummary()
        return summary.summary_map

    #
    # Access Keys
    #
    def delete_access_key(self, username, key_id):
        """Delete an access key."""
        self.iam_client.delete_access_key(
            UserName=username,
            AccessKeyId=key_id,
        )

    def list_access_keys(self, username):
        """List access keys."""
        return self.iam_client.list_access_keys(
            UserName=username
        )

    #
    # Account Alias
    #
    def create_alias(self, alias):
        """Create account alias."""
        return self.iam_client.create_account_alias(
            AccountAlias=alias,
        )

    def delete_alias(self, alias):
        """Delete account alias."""
        return self.iam_client.delete_account_alias(
            AccountAlias=alias,
        )

    def get_alias(self):
        """Return the alias for this account."""
        aliases = self.list_aliases()
        if aliases:
            return aliases[0]

    def list_aliases(self):
        """Return the alias for this account."""
        return self.iam_client.list_account_aliases().get('AccountAliases', [])

    #
    # Account Password Policy
    #
    def get_account_password_policy(self):
        """Return the password policy for this account."""
        response = self.iam_client.get_account_password_policy()
        return response.get('PasswordPolicy')

    def update_account_password_policy(self, policy):
        """Update the password policy for this account."""
        return self.iam_client.update_account_password_policy(**policy)

    #
    # Buckets
    #
    def list_buckets(self):
        """Return a list of buckets."""
        return self.s3_client.list_buckets().get('Buckets', [])

    #
    # Groups
    #
    def create_group(self, groupname, policy):
        """Create a group."""
        return self.iam_client.create_group(
            GroupName=groupname,
        )

    def list_groups(self):
        """Return a list of groups."""
        return self.iam_client.get_groups().get('Groups', [])

    #
    # Group Policies
    #
    def attach_group_policy(self, groupname, arn):
        """Attach a group policy."""
        return self.iam_client.attach_group_policy(
            GroupName=groupname,
            PolicyArn=arn,
        )

    #
    # Policies
    #
    def delete_policy(self, arn):
        """Delete a policy."""
        return self.iam_client.delete_policy(
            PolicyArn=arn
        )

    def list_policies(self):
        """Return a list of policies."""
        return self.iam_client.list_policies(
            Scope='Local'
        ).get('Policies', [])

    #
    # Policy Versions
    #
    def create_policy_version(self, arn, document):
        """Create a policy version."""
        return self.iam_client.create_policy_version(
            PolicyArn=arn,
            PolicyDocument=document,
            SetAsDefault=True,
        )

    def list_policy_version(self, arn, document):
        """List policy versions."""
        return self.iam_client.list_policy_versions(
            PolicyArn=arn,
        )

    def delete_policy_version(self, arn, version):
        """Delete a policy version."""
        return self.iam_client.create_policy_version(
            PolicyArn=arn,
            VersionId=version,
        )

    #
    # Role Policies
    #
    def attach_role_policy(self, rolename, arn):
        """Attach a role policy."""
        return self.iam_client.attach_role_policy(
            RoleName=rolename,
            PolicyArn=arn,
        )

    #
    # Roles
    #
    def create_role(self, rolename, policy):
        """Create a role."""
        return self.iam_client.create_role(
            RoleName=rolename,
            AssumeRolePolicyDocument=policy,
        )

    def list_roles(self):
        """Return a list of roles."""
        return self.iam_client.list_roles().get('Roles', [])

    #
    # SAML Providers
    #
    def create_saml_provider(self, name, metadata):
        """Create SAML provider."""
        return self.iam_client.create_saml_provider(
            Name=name,
            SAMLMetadataDocument=metadata,
        )

    def list_saml_providers(self):
        """Return a list of SAML providers."""
        return self.iam_client.list_saml_providers().get('SAMLProviderList', [])

    def saml_metadata_document(self, arn):
        """Return the SAML metadata document."""
        self.iam.SamlProvider(arn).saml_metadata_document

    #
    # User Policies
    #
    def detach_user_policy(self, username, arn):
        """Detach a user policy."""
        return self.iam_client.detach_user_policy(
            UserName=username,
            PolicyArn=arn,
        )

    def put_user_policy(self, username, policy, document):
        """Put a user policy."""
        return self.iam_client.put_user_policy(
            UserName=username,
            PolicyName=policy,
            PolicyDocument=document,
        )

    #
    # Users
    #
    def create_user(self, username):
        """Create a user."""
        return self.iam_client.create_user(
            UserName=username,
        )

    def delete_user(self, username):
        """Delete a user."""
        return self.iam_client.delete_user(
            UserName=username,
        )

    def list_users(self):
        """List users."""
        return self.iam_client.list_users().get('Users', [])

    #
    # Display Functions
    #
    def display(self):
        """Display information about this account."""
        print('%s: %s [%s] - %s' % (
            self.alias,
            self.name,
            self.id,
            self.status
        ))
        if self.status == 'SUSPENDED':
            return

        self.display_groups()
        self.display_policies()
        self.display_roles()
        self.display_users()

    def display_groups(self):
        """Display groups."""
        if self.groups:
            print('   * Groups: %s' % (len(self.groups)))
        if self.verbose:
            for group in sorted(self.groups, key=lambda x: x['GroupName']):
                print('      * %s' % (group['GroupName']))

    def display_policies(self):
        """Display policies."""
        if self.policies:
            print('   * Policies: %s' % (len(self.policies)))
        if self.verbose:
            for policy in sorted(self.policies, key=lambda x: x['PolicyName']):
                print('      * %s' % (policy['PolicyName']))

    def display_roles(self):
        """Display roles."""
        if self.roles:
            print('   * Roles: %s' % (len(self.roles)))
        if self.verbose:
            for role in sorted(self.roles, key=lambda x: x['RoleName']):
                print('      * %s' % (role['RoleName']))

    def display_users(self):
        """Display users."""
        if self.users:
            print('   * Users: %s' % (len(self.users)))
        if self.verbose:
            for user in sorted(self.users, key=lambda x: x['UserName']):
                print('      * %s' % (user['UserName']))
