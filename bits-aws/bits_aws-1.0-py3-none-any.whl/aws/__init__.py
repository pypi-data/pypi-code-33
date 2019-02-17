"""BITS AWS class file."""

import boto3
import os

from bits.aws.account import Account


class AWS(object):
    """BITS AWS class."""

    def __init__(
        self,
        credentials_file=None,
        root_account=None,
        verbose=False
    ):
        """Initialize a class instance."""
        self.credentials_file = credentials_file
        self.root_account = root_account
        self.verbose = verbose

        # set environment variable
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = credentials_file

        # create resources
        self.iam = boto3.resource('iam')
        self.s3 = boto3.resource('s3')

        # create clients
        self.iam_client = boto3.client('iam')
        self.organizations_client = boto3.client('organizations')
        self.s3_client = boto3.client('s3')
        self.sts_client = boto3.client('sts')

        # classes
        self.account = Account

    def assume_role(self, role_name, resource):
        """Return credentials for an assumed role."""
        assumedRoleObject = self.sts_client.assume_role(
            RoleArn=role_name,
            RoleSessionName="AssumeRoleSession1"
        )
        credentials = assumedRoleObject['Credentials']
        return credentials

    def get_accounts(
        self,
        include_alias=True,
        include_details=False,
        include_summary=False
    ):
        """Return a list of account objects."""
        accounts_list = self.get_organization_accounts()
        accounts = []
        for aws_account in accounts_list:
            # if self.verbose:
            #     print('Retrieving account: %s' % (aws_account['Id']))
            account = self.account().from_aws(
                self,
                aws_account,
                include_alias=True,
                include_details=include_details,
                include_summary=include_summary
            )
            accounts.append(account)
        return(accounts)

    def get_accounts_dict(self):
        """Return a dict of accounts from AWS."""
        accounts_list = self.get_accounts()
        accounts = {}
        for a in accounts_list:
            accounts[a.id] = a
        return(accounts)

    def get_organization_accounts(self):
        """Return a list of accounts from AWS."""
        client = self.organizations_client

        response = client.list_accounts()
        accounts = response.get('Accounts', [])
        next_token = response.get('NextToken')

        while next_token:
            response = client.list_accounts(NextToken=next_token)
            next_token = response.get('NextToken')
            accounts += response.get('Accounts', [])

        return accounts
