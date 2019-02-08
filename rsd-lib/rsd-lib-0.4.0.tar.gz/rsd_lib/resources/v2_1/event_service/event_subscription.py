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

from jsonschema import validate
import logging

from sushy.resources import base

from rsd_lib.resources.v2_1.event_service import schemas as \
    event_service_schemas


LOG = logging.getLogger(__name__)


class OemField(base.CompositeField):
    pass


class EventSubscription(base.ResourceBase):
    identity = base.Field("Id")
    """The Event Subscription id"""

    name = base.Field("Name")
    """The Event Subscription name"""

    description = base.Field("Description")
    """The Event Subscription description"""

    oem = OemField("Oem")
    """The Event Subscription oem"""

    destination = base.Field("Destination")
    """The URI of the destination Event Service"""

    event_types = base.Field("EventTypes")
    """These are the types of Events that can be subscribed to. Available
       event types:
           - StatusChange - The status of this resource has changed
           - ResourceUpdated - The value of this resource has been updated.
           - ResourceAdded - A resource has been added
           - ResourceRemoved - A resource has been removed
           - Alert - A condition exists which requires attention
    """

    context = base.Field("Context")
    """A client-supplied string that is stored with the event destination
       subscription
    """

    protocol = base.Field("Protocol")
    """The protocol type of the event connection. Available protocols:
           - "Redfish" - event type shall adhere to that defined in the
                         Redfish specification.
    """

    http_headers = base.Field("HttpHeaders")
    """This property shall contain an object consisting of the names and values
       of of HTTP header to be included with every event POST to the Event
       Destination
    """

    origin_resources = base.Field("OriginResources")
    """A list of resources for which the service will send events specified in
       EventTypes array. Empty array or NULL is interpreted as subscription for
       all resources and assets in subsystem.
    """

    message_ids = base.Field("MessageIds")
    """A list of MessageIds that the service will send"""

    def delete(self):
        """Delete this event subscription"""
        self._conn.delete(self._path)


class EventSubscriptionCollection(base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return EventSubscription

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a Event Subscription Collection

        :param connector: A Connector instance
        :param path: The canonical path to the Event Subscription collection
        resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(EventSubscriptionCollection, self).__init__(connector, path,
                                                          redfish_version)

    def create_event_subscription(self, event_subscription_req):
        """Create a new event subscription

        :param event_subscription_req: JSON for event subscription
        :returns: The uri of the new event subscription
        """
        target_uri = self._path

        validate(event_subscription_req,
                 event_service_schemas.event_subscription_req_schema)

        resp = self._conn.post(target_uri, data=event_subscription_req)
        event_subscription_url = resp.headers['Location']
        LOG.info("event subscription created at %s", event_subscription_url)

        return event_subscription_url[event_subscription_url.find(self._path):]
