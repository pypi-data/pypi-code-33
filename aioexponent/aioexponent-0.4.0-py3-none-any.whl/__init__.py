# This code has been greatly adaptated by https://github.com/expo/expo-server-sdk-python
from collections import namedtuple
import aiohttp

from .exceptions import (
    PushResponseError,
    DeviceNotRegisteredError,
    MessageTooBigError,
    MessageRateExceededError,
    PushServerError,
)


class PushMessage(
    namedtuple(
        "PushMessage",
        [
            "to",
            "data",
            "title",
            "body",
            "sound",
            "ttl",
            "expiration",
            "priority",
            "badge",
            "channel_id",
        ],
    )
):
    """An object that describes a push notification request.

    You can override this class to provide your own custom validation before
    sending these to the Exponent push servers. You can also override the
    get_payload function itself to take advantage of any hidden or new
    arguments before this library updates upstream.

        Args:
            to: A token of the form ExponentPushToken[xxxxxxx]
            data: A dict of extra data to pass inside of the push notification.
                The total notification payload must be at most 4096 bytes.
            title: The title to display in the notification. On iOS, this is
                displayed only on Apple Watch.
            body: The message to display in the notification.
            sound: A sound to play when the recipient receives this
                notification. Specify "default" to play the device's default
                notification sound, or omit this field to play no sound.
            ttl: The number of seconds for which the message may be kept around
                for redelivery if it hasn't been delivered yet. Defaults to 0.
            expiration: UNIX timestamp for when this message expires. It has
                the same effect as ttl, and is just an absolute timestamp
                instead of a relative one.
            priority: Delivery priority of the message. 'default', 'normal',
                and 'high' are the only valid values.
            badge: An integer representing the unread notification count. This
                currently only affects iOS. Specify 0 to clear the badge count.
            channel_id: ID of the Notification Channel through which to display
                this notification on Android devices.

    """

    def get_payload(self):
        # Sanity check for invalid push token format.
        if not PushClient.is_exponent_push_token(self.to):
            raise ValueError(f"Invalid push token: {self.to}")

        # There is only one required field.
        payload = {"to": self.to}

        # All of these fields are optional.
        if self.data is not None:
            payload["data"] = self.data
        if self.title is not None:
            payload["title"] = self.title
        if self.body is not None:
            payload["body"] = self.body
        if self.sound is not None:
            payload["sound"] = self.sound
        if self.ttl is not None:
            payload["ttl"] = self.ttl
        if self.expiration is not None:
            payload["expiration"] = self.expiration
        if self.priority is not None:
            payload["priority"] = self.priority
        if self.badge is not None:
            payload["badge"] = self.badge
        if self.channel_id is not None:
            payload["channelId"] = self.channel_id
        return payload


# Allow optional arguments for PushMessages since everything but the `to` field
# is optional. Unfortunately namedtuples don't allow for an easy way to create
# a required argument at the contructor level right now.
PushMessage.__new__.__defaults__ = (None,) * len(PushMessage._fields)


class PushResponse(
    namedtuple("PushResponse", ["push_message", "status", "message", "details"])
):
    """Wrapper class for a push notification response.

    A successful single push notification:
        {'status': 'ok'}

    An invalid push token
        {'status': 'error',
         'message': '"adsf" is not a registered push notification recipient'}
    """

    # Known status codes
    ERROR_STATUS = "error"
    SUCCESS_STATUS = "ok"

    # Known error strings
    ERROR_DEVICE_NOT_REGISTERED = "DeviceNotRegistered"
    ERROR_MESSAGE_TOO_BIG = "MessageTooBig"
    ERROR_MESSAGE_RATE_EXCEEDED = "MessageRateExceeded"

    def is_success(self):
        """Returns True if this push notification successfully sent."""
        return self.status == PushResponse.SUCCESS_STATUS

    def validate_response(self):
        """Raises an exception if there was an error. Otherwise, do nothing.

        Clients should handle these errors, since these require custom handling
        to properly resolve.
        """
        if self.is_success():
            return

        # Handle the error if we have any information
        if self.details:
            error = self.details.get("error", None)

            if error == PushResponse.ERROR_DEVICE_NOT_REGISTERED:
                raise DeviceNotRegisteredError(self)
            elif error == PushResponse.ERROR_MESSAGE_TOO_BIG:
                raise MessageTooBigError(self)
            elif error == PushResponse.ERROR_MESSAGE_RATE_EXCEEDED:
                raise MessageRateExceededError(self)

        # No known error information, so let's raise a generic error.
        raise PushResponseError(self)


class PushClient(object):
    """Exponent push client

    See full API docs at
    https://docs.expo.io/versions/latest/guides/push-notifications.html#http2-api
    """

    DEFAULT_HOST = "https://exp.host"
    DEFAULT_BASE_API_URL = "/--/api/v2"

    def __init__(self, host=None, api_url=None):
        """Construct a new PushClient object.

        Args:
            host: The server protocol, hostname, and port.
            api_url: The api url at the host.
        """
        self.host = host
        if not self.host:
            self.host = PushClient.DEFAULT_HOST

        self.api_url = api_url
        if not self.api_url:
            self.api_url = PushClient.DEFAULT_BASE_API_URL

    @classmethod
    def is_exponent_push_token(cls, token):
        """Returns `True` if the token is an Exponent push token"""
        return isinstance(token, str) and token.startswith("ExponentPushToken")

    async def _publish_internal(self, push_messages):
        """Send push notifications

        The server will validate any type of syntax errors and the client will
        raise the proper exceptions for the user to handle.

        Each notification is of the form:
        {
          'to': 'ExponentPushToken[xxx]',
          'body': 'This text gets display in the notification',
          'badge': 1,
          'data': {'any': 'json object'},
        }

        Args:
            push_messages: An array of PushMessage objects.
        """
        if not isinstance(push_messages, list) or len(push_messages) > 100:
            raise ValueError("push_messages should be an array of up to 100 messages")

        async with aiohttp.ClientSession() as client:
            async with client.post(
                f"{self.host}{self.api_url}/push/send",
                json=[pm.get_payload() for pm in push_messages],
                headers={
                    "accept": "application/json",
                    "accept-encoding": "gzip, deflate",
                    "content-type": "application/json",
                },
            ) as response:

                # Let's validate the response format first.
                try:
                    response_data = await response.json()
                except ValueError:
                    # The response isn't json. First, let's attempt to raise a normal
                    # http error. If it's a 200, then we'll raise our own error.
                    response.raise_for_status()
                    raise PushServerError("Invalid server response", response)

                # If there are errors with the entire request, raise an error now.
                if "errors" in response_data:
                    raise PushServerError(
                        "Request failed",
                        response,
                        response_data=response_data,
                        errors=response_data["errors"],
                    )

                # We expect the response to have a 'data' field with the responses.
                if "data" not in response_data:
                    raise PushServerError(
                        "Invalid server response", response, response_data=response_data
                    )

                # Use the requests library's built-in exceptions for any remaining 4xx
                # and 5xx errors.
                response.raise_for_status()

                # Sanity check the response
                if len(push_messages) != len(response_data["data"]):
                    s = "s" if len(push_messages) > 1 else ""
                    raise PushServerError(
                        f"Mismatched response length. Expected {len(push_messages)} "
                        f"receipt{s} but only received {len(response_data['data'])}",
                        response,
                        response_data=response_data,
                    )

                # At this point, we know it's a 200 and the response format is correct.
                # Now let's parse the responses per push notification.
                receipts = []
                for i, receipt in enumerate(response_data["data"]):
                    receipts.append(
                        PushResponse(
                            push_message=push_messages[i],
                            # If there is no status, assume error.
                            status=receipt.get("status", PushResponse.ERROR_STATUS),
                            message=receipt.get("message", ""),
                            details=receipt.get("details", None),
                        )
                    )

                return receipts

    async def publish(self, push_message):
        """Sends a single push notification

        Args:
            push_message: A single PushMessage object.

        Returns:
           A PushResponse object which contains the results.
        """
        return await self.publish_multiple([push_message])[0]

    async def publish_multiple(self, push_messages):
        """Sends multiple push notifications at once

        Args:
            push_messages: An array of PushMessage objects.

        Returns:
           An array of PushResponse objects which contains the results.
        """
        return await self._publish_internal(push_messages)
