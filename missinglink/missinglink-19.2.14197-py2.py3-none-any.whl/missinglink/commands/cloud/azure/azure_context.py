import json
import re
import uuid

from azure.common.credentials import get_azure_cli_credentials
from azure.graphrbac import GraphRbacManagementClient
from azure.keyvault import KeyVaultClient
from azure.graphrbac.models import ServicePrincipalCreateParameters
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.authorization.models import RoleAssignmentCreateParameters
from azure.mgmt.msi import ManagedServiceIdentityClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentProperties
from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.storage import StorageManagementClient
from msrestazure.azure_active_directory import MSIAuthentication
import click
from missinglink.crypto import SshIdentity

from missinglink.commands.cloud.aws import BackendContext
from missinglink.commands.cloud.cloud_connector import CloudConnector
from missinglink.commands.utilities import pop_key_or_prompt_if, PathTools

APP_ID = '7eba301b-077d-4d8e-a1dd-a0b70113e6ca'


class AzureContext(BackendContext, CloudConnector):
    def __init__(self, ctx, kwargs):
        super(AzureContext, self).__init__(ctx, kwargs)
        self.location = ctx.obj.azure.location
        self.kwargs = kwargs

    def init_and_authorise_app(self):
        service_principal = self._create_service_principal()
        self._get_and_deploy_template()
        self._setup_default_storage()
        self._assign_role_key_vault_perms()
        self._register_compute_provider()
        self._create_key()
        self._authorize_app(service_principal)
        self._create_cloud_connector()
        self._init_prepare_connector_message(set_ssh=not self.auth_state['ssh_present'], set_ml=not self.auth_state['mali_config'])

    def _create_service_principal(self):
        rbac_client = get_client_from_cli_profile(GraphRbacManagementClient)
        app_sp = list(rbac_client.service_principals.list(filter='appId eq \'%s\'' % APP_ID))
        if not app_sp:
            service_principal = rbac_client.service_principals.create(
                ServicePrincipalCreateParameters(app_id=APP_ID, account_enabled=True))
        else:
            service_principal = app_sp[0]
        self.tenant_id = rbac_client.config.tenant_id
        return service_principal

    def _authorize_app(self, service_principal):
        click.echo('Authorizing MissingLink App to manage virtual machines')
        auth_client = get_client_from_cli_profile(AuthorizationManagementClient)
        scope = '/subscriptions/%s/resourceGroups/%s' % (auth_client.config.subscription_id, self.rg_name)
        role_defs = list(auth_client.role_definitions.list(
            scope,
            filter='roleName eq \'MissingLinkRM-%s\'' % self.org
        ))
        if not role_defs:
            role_id = uuid.uuid4()
        else:
            role_id = role_defs[0].name

        res = auth_client.role_definitions.create_or_update(
            scope,
            role_id,
            {
                "role_name": "MissingLinkRM-" + self.org,
                "description": "Manages instances for running jobs. See MissingLink.ai",
                "permissions": [
                    {
                        "actions": [
                            'Microsoft.Resources/deployments/*',
                            'Microsoft.Compute/virtualMachines/*',
                            'Microsoft.Network/publicIpAddresses/*',
                            'Microsoft.Network/networkInterfaces/*',
                            'Microsoft.Network/virtualNetworks/subnets/join/action',
                            'Microsoft.Compute/disks/*',
                            'Microsoft.Compute/images/*',
                            'Microsoft.ResourceHealth/availabilityStatuses/read',
                            'Microsoft.ManagedIdentity/userAssignedIdentities/assign/action',
                            'Microsoft.Storage/storageAccounts/listKeys/action',
                            'Microsoft.Storage/storageAccounts/read',
                        ],
                        "not_actions": [
                        ],
                    }
                ],

                "assignable_scopes": [
                    scope
                ]
            }
        )
        role_definition_id = res.id
        roles = list(auth_client.role_assignments.list_for_resource_group(self.rg_name, filter='principalId eq \'%s\'' % service_principal.object_id))
        self._create_role_if_missing(auth_client, role_definition_id, roles, service_principal.object_id, scope)
        click.echo('Done')

    def _create_role_if_missing(self, auth_client, role_id, roles, principal_id, scope):
        role = [r for r in roles if r.role_definition_id == role_id]
        if not role:
            auth_client.role_assignments.create(
                scope,
                uuid.uuid4(),
                RoleAssignmentCreateParameters(role_definition_id=role_id, principal_id=principal_id)
            )

    def _get_template(self):
        result = self._handle_api_call('get', '{}/azure/init_template'.format(self.org))
        return json.loads(result['template'])

    def _create_key(self):
        click.echo('Creating a key in the Key Vault')
        credentials, subscription_id = get_azure_cli_credentials(resource='https://vault.azure.net')
        key_vault_client = KeyVaultClient(credentials)
        key_name = 'MissingLinkRM'
        results = list(key_vault_client.get_key_versions(self.key_vault, key_name))
        if not results:
            key_bundle = key_vault_client.create_key(self.key_vault, key_name, 'RSA', key_size=4096)
            self.key_id = key_bundle.key.kid
        else:
            self.key_id = results[0].kid
        click.echo('Done')

    def _get_existing_volumes(self):
        result = self._handle_api_call('get', 'orgs/{}/metadata?only=buckets'.format(self.org))
        buckets = result.get('data', [{'values': []}])[0]['values']
        storages = {self.storage_acc_name}
        for bucket in buckets:
            m = re.match(r'az://(.*)\..*', bucket)
            if m:
                storages.add(m.group(1))
        return storages

    def _assign_role_key_vault_perms(self):
        click.echo('Giving permissions to access Key Vault to worker instances')
        msi_client = get_client_from_cli_profile(ManagedServiceIdentityClient)
        role_identity = msi_client.user_assigned_identities.get(self.rg_name, self.role_name)
        self.role_id = role_identity.id
        key_vault_client = get_client_from_cli_profile(KeyVaultManagementClient)
        policies = {'access_policies': [
            {
                'tenant_id': self.tenant_id,
                'object_id': role_identity.principal_id,
                'permissions': {'keys': ['Decrypt']}
            }
        ]}
        key_vault_client.vaults.update_access_policy(self.rg_name, self.vault_name, 'add', policies)

        used_storages = self._get_existing_volumes()

        storage_client = get_client_from_cli_profile(StorageManagementClient)
        all_storages = storage_client.storage_accounts.list()
        registered_storages = set()
        for storage_account in all_storages:
            if storage_account.name in used_storages:
                registered_storages.add(storage_account.id)
        for storage_id in registered_storages:
            self._grant_access_to_storage(role_identity, storage_id)

        click.echo('Done')

    def _grant_access_to_storage(self, role_identity, storage_id):
        auth_client = get_client_from_cli_profile(AuthorizationManagementClient)
        roles = list(auth_client.role_assignments.list_for_scope(storage_id,
                                                                 filter='principalId eq \'%s\'' % role_identity.principal_id))
        role_id = 'c12c1c16-33a1-487b-954d-41c89c60f349'  # https://docs.microsoft.com/en-us/azure/role-based-access-control/built-in-roles#reader-and-data-access
        role_definition_id = '/subscriptions/%s/providers/Microsoft.Authorization/roleDefinitions/%s' % (auth_client.config.subscription_id, role_id)
        self._create_role_if_missing(auth_client, role_definition_id, roles, role_identity.principal_id, storage_id)

    @property
    def normalized_org(self):
        return re.sub('[^a-z0-9]+', '', self.org.lower())[:20]

    def _get_and_deploy_template(self):
        click.echo('Applying template for Resource Group, Network and Key Vault')
        template = self._get_template()
        rm_client = get_client_from_cli_profile(ResourceManagementClient)
        self.subscription_id = rm_client.config.subscription_id
        rbac_client = get_client_from_cli_profile(GraphRbacManagementClient)
        user = rbac_client.signed_in_user.get()
        params = {
            'rgLocation': self.location,
            'org': self.normalized_org,
            'userObjectId': user.object_id
        }
        params = {k: {'value': v} for k, v in params.items()}
        poller = rm_client.deployments.create_or_update_at_subscription_scope('MissingLink-' + self.org, DeploymentProperties(template=template, mode='Incremental', parameters=params), location=self.location)
        poller.wait()
        result = poller.result()
        self.net_name = result.properties.outputs['netName']['value']
        self.rg_name = result.properties.outputs['groupName']['value']
        self.key_vault = result.properties.outputs['vaultPath']['value']
        self.vault_name = result.properties.outputs['vaultName']['value']
        self.subnet = result.properties.outputs['subnetName']['value']
        self.role_name = result.properties.outputs['roleName']['value']
        self.storage_rg_name = result.properties.outputs['storageRgName']['value']
        self.storage_acc_name = result.properties.outputs['storageAccName']['value']
        self.image_storage_name = result.properties.outputs['imageStorageName']['value']
        click.echo('Done')

    def _setup_default_storage(self):
        click.echo('Setting up default container for artifacts')
        storage_client = get_client_from_cli_profile(StorageManagementClient)
        container_name = 'default'
        containers = storage_client.blob_containers.list(self.storage_rg_name, self.storage_acc_name)
        if not any(container.name == container_name for container in containers.value):
            storage_client.blob_containers.create(self.storage_rg_name, self.storage_acc_name, container_name)
        self.bucket_name = self.storage_acc_name + '.' + container_name

        containers = storage_client.blob_containers.list(self.rg_name, self.image_storage_name)
        if not any(container.name == container_name for container in containers.value):
            storage_client.blob_containers.create(self.rg_name, self.image_storage_name, container_name)

        click.echo('Done')

    def _register_compute_provider(self):
        click.echo('Registering compute service in Azure subscription')
        rm_client = get_client_from_cli_profile(ResourceManagementClient)
        rm_client.providers.register('Microsoft.Compute')
        click.echo('Done')

    def _create_cloud_connector(self):
        click.echo('Saving state to MissingLink servers')
        template = {
            'subscription_id': self.subscription_id,
            'tenant_id': self.tenant_id,
            'key_name': self.key_id,
            'location': self.location,
            'net_data': [{'name': self.net_name, 'region': self.location, 'subnet': self.subnet}],
            'resource_group': self.rg_name,
            'key_vault': self.key_vault,
            'role_name': self.role_name,
            'role_id': self.role_id,
            'az_storage': [{'bucket_name': self.bucket_name}],
            'image_storage': self.image_storage_name,
        }
        url = '{org}/azure/save_connector'.format(org=self.org)
        self.auth_state = self._handle_api_call('post', url, template)

    @classmethod
    def get_cloud_kms(cls, key_id, role_id):
        credentials = MSIAuthentication(
            msi_res_id=role_id,
            resource='https://vault.azure.net'
        )
        return cls.get_kms(key_id, credentials)

    @classmethod
    def get_cli_kms(cls, key_id):
        credentials, subscription_id = get_azure_cli_credentials(resource='https://vault.azure.net')
        return cls.get_kms(key_id, credentials)

    @classmethod
    def get_kms(cls, key_id, credentials):
        from missinglink.crypto import AzureEnvelope

        return AzureEnvelope(credentials, key_id)

    def _init_prepare_connector_message(self, set_ssh, set_ml):
        template, config_data = self.cloud_connector_defaults(self.ctx, cloud_type='azure', kwargs=dict(connector=self.subscription_id))
        kms = self.get_cli_kms(self.key_id)
        if set_ssh:
            ssh_key_path = pop_key_or_prompt_if(self.kwargs, 'ssh_key_path', text='SSH key path [--ssh-key-path]', default=PathTools.get_ssh_path())
            ssh_key = SshIdentity(ssh_key_path)
            ssh_key_priv = ssh_key.export_private_key_bytes()
            ssh_key_pub = ssh_key.export_public_key_bytes().decode('utf-8')
            self._update_org_metadata_ssh_key(ssh_key_pub)
            ssh = self.encrypt(kms, ssh_key_priv)
            template['ssh'] = ssh
        if set_ml:
            mali = self.encrypt(kms, config_data)
            template['mali'] = mali

        template['cloud_data'] = {}
        url = '{org}/cloud_connector/{name}'.format(org=self.org, name=template['name'])
        self._handle_api_call('post', url, template)
        click.echo('Done')
