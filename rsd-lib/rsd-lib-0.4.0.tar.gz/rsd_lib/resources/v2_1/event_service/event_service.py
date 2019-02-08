# Copyright 2019 Intel, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from sushy.resources import base
from sushy import utils

from rsd_lib.resources.v2_1.event_service import event_subscription
from rsd_lib import utils as rsd_lib_utils


class StatusField(base.CompositeField):
    state = base.Field("State")
    """The state of Status"""

    health = base.Field("Health")
    """The Status health"""

    health_rollup = base.Field('HealthRollup')
    """The Status health_rollup field"""


class EventService(base.ResourceBase):
    identity = base.Field("Id", required=True)
    """The event service identity"""

    name = base.Field("Name")
    """The event service name"""

    description = base.Field("Description")
    """The description of event service"""

    status = StatusField("Status")
    """The event service status"""

    service_enabled = base.Field("ServiceEnabled", adapter=bool)
    """Whether the event service is enabled"""

    delivery_retry_attempts = base.Field("DeliveryRetryAttempts",
                                         adapter=rsd_lib_utils.num_or_none)
    """This is the number of attempts an event posting is retried before the
       subscription is terminated
    """

    delivery_retry_interval_seconds = base.Field(
        "DeliveryRetryIntervalSeconds", adapter=rsd_lib_utils.num_or_none)
    """This represents the number of seconds between retry attempts for
       sending any given Event
    """

    event_types_for_subscription = base.Field("EventTypesForSubscription")
    """These are the types of Events that can be subscribed to. Available
       event types:
           - StatusChange - The status of this resource has changed
           - ResourceUpdated - The value of this resource has been updated
           - ResourceAdded - A resource has been added
           - ResourceRemoved - A resource has been removed
           - Alert - A condition exists which requires attention
    """

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing a EventService

        :param connector: A Connector instance
        :param identity: The identity of the EventService resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(EventService, self).__init__(connector, identity,
                                           redfish_version)

    def _get_subscriptions_collection_path(self):
        """Helper function to find the EventSubscriptionCollection path"""
        return utils.get_sub_resource_path_by(self, 'Subscriptions')

    @property
    @utils.cache_it
    def subscriptions(self):
        """Property to provide reference to `EventSubscriptionCollection`

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return event_subscription.EventSubscriptionCollection(
            self._conn, self._get_subscriptions_collection_path(),
            redfish_version=self.redfish_version)
