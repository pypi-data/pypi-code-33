"""Base class for Integration objects
"""

from rockset.swagger_client.api import IntegrationsApi


class Integration(object):
    TYPE_AWS = 'AWS'
    TYPE_AWS_EXTERNAL_ID = 'AWSExternalId'
    TYPE_GCP_SERVICE_ACCOUNT = 'GCPServiceAccount'

    @classmethod
    def list(cls, **kwargs):
        if 'client' not in kwargs:
            raise ValueError(
                'incorrect API usage. '
                'use rockset.Client().Integration.list() instead.'
            )
        client = kwargs.pop('client')

        integrations = IntegrationsApi(client).list().get('data')

        list = []
        for i in integrations:
            type = cls.TYPE_AWS
            list.append(cls(client=client, type=type, **i.to_dict()))
        return list

    @classmethod
    def retrieve(cls, **kwargs):
        """Retrieves a single integration

        Args:
            name (str): Name of the integration to be retrieved

        Returns:
            Integration: Integration object
        """

        if 'client' not in kwargs:
            raise ValueError(
                'incorrect API usage. '
                'use rockset.Client().Integration.retrieve() instead.'
            )

        client = kwargs.pop('client')
        name = kwargs.pop('name')
        integration = IntegrationsApi(client).get(integration=name).get('data')
        type = "UNKOWN"
        if integration.aws is not None:
            type = cls.TYPE_AWS
        elif integration.aws_external_id is not None:
            type = cls.TYPE_AWS_EXTERNAL_ID
        elif integration.gcp_service_account is not None:
            type = cls.TYPE_GCP_SERVICE_ACCOUNT
        return cls(client=client, type=type, **integration.to_dict())

    # instance_methods
    def __init__(self, client, name, type, **kwargs):
        """Represents a single Integration"""
        self.client = client
        self.name = name
        self.type = type
        for key in kwargs:
            setattr(self, key, kwargs[key])
        return

    def __str__(self):
        """Converts the collection into a user friendly printable string"""
        return str(vars(self))

    def asdict(self):
        d = vars(self)
        d.pop('client')
        return d

    def drop(self):
        IntegrationsApi(self.client).delete(integration=self.name)
        return
