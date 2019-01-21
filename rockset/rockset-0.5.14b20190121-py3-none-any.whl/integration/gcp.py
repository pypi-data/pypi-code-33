"""
Introduction
------------
Integration objects represents a single Rockset integration.
These objects are generally created using a Rockset Client
object using methods such as::

    from rockset import Client

    # connect to Rockset
    rs = Client(api_key=...)

"""

from .integration import Integration

from rockset.swagger_client.api import IntegrationsApi
from rockset.swagger_client.models import (
    GcpServiceAccount, CreateIntegrationRequest
)


class GCPServiceAccountIntegration(Integration):
    @classmethod
    def create(cls, name, json_key, **kwargs):
        if json_key is None:
            raise ValueError(
                'json_key required to create a GCP Service Account integration'
            )

        client = kwargs.pop('client')

        gcp_service_account = GcpServiceAccount(json_key)

        request = CreateIntegrationRequest(
            name=name, gcp_service_account=gcp_service_account, **kwargs
        )

        integration = IntegrationsApi(client).create(body=request).get('data')
        return cls(client, **integration.to_dict())

    def __init__(self, *args, **kwargs):
        kwargs['type'] = Integration.TYPE_GCP_SERVICE_ACCOUNT
        super().__init__(*args, **kwargs)
