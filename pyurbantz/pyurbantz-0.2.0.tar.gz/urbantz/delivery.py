from datetime import datetime, timedelta
from urbantz.base import JSONSerializable, Coordinates
from urbantz.utils import DictObject
from urbantz.items import LogEntry, Item
from urbantz.exceptions import APIError
import requests

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


class Location(DictObject):
    """
    A delivery destination.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'location' not in self:
            return
        point = self.pop('location')['geometry']
        self['coordinates'] = Coordinates.fromJSON(point)


class Delivery(JSONSerializable):
    """
    A UrbanTZ delivery with a unique ID.
    """

    def __init__(self, tracking_code=None):
        """
        :param tracking_code: A delivery public tracking code.
        :type tracking_code: str or None
        """
        self.tracking_code = tracking_code
        """
        The delivery public tracking code.

        :type: str or None
        """

        self.last_updated = None
        """
        Last API update date/time. Is None if data has never been fetched
        from the API.

        :type: datetime or None
        """

        self.payload = None
        """
        Latest parsed JSON payload from the API. Is None if data has never
        been fetched from the API or loaded via :meth:`Delivery.use`.

        :type: dict or None
        """

        self.id = None
        """
        Identifier for this delivery.

        :type: str or None
        """

        self.date = None
        """
        Date of the delivery.

        :type: date or None
        """

        self.task_id = None
        """
        Task identifier for this delivery.

        :type: str or None
        """

        self.platform_id = None
        """
        Platform identifier for this delivery.

        :type: str or None
        """

        self.driver_id = None
        """
        Driver identifier for this delivery.

        :type: str or None
        """

        self.round_id = None
        """
        Driver round identifier for this delivery.

        :type: str or None
        """

        self.instructions = None
        """
        Delivery instructions given to the driver.

        :type: str or None
        """

        self.progress = None
        """
        The delivery order progress.

        :type: str or None
        """

        self.status = None
        """
        The delivery status.

        :type: str or None
        """

        self.arrival_time = None
        """
        Estimated or actual arrival time.

        :type: datetime or None
        """

        self.eta_margin = None
        """
        Margin, in minutes, for the estimated time of arrival.

        :type: int or None
        """

        self.eta_rounding = None
        """
        Rounding, in minutes, for the estimated time of arrival.

        :type: int or None
        """

        self.time_window = None
        """
        Planned delivery time window (start and end datetimes)

        :type: list(datetime) or None
        """

        self.position = None
        """
        Coordinates of the delivery truck's position.

        :type: urbantz.base.Coordinates or None
        """

        self.destination = None
        """
        The delivery's destination.

        :type: urbantz.delivery.Location or None
        """

        self.recipient = None
        """
        Informations about the recipient (name, language, phone number, etc.)
        Does not contain the destination location information.

        :type: urbantz.utils.DictObject or None
        """

        self.features = None
        """
        Dictionary of booleans indicating which features of the UrbanTZ
        tracking software are enabled on this delivery.
        For example, ``consumerModifyInstructions`` will indicate whether
        the client is allowed to update the delivery instructions after the
        driver departs for its round.

        :type: urbantz.utils.DictObject or None
        """

        self.items = None
        """
        List of delivery items.

        :type: list(urbantz.items.Item)
        """

        self.logs = None
        """
        List of status update logs for the delivery.

        :type: list(urbantz.items.LogEntry)
        """

        self.theme = None
        """
        Front-end theming information for the delivery tracking page.

        :type: urbantz.utils.DictObject or None
        """

        self.template = None
        """
        Front-end template information for the delivery tracking page.

        :type: urbantz.utils.DictObject or None
        """

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__, repr(self.tracking_code))

    @property
    def api_url(self):
        """
        URL pointing to the API endpoint to use for the specific delivery.

        :type: str
        """
        return 'https://backend.urbantz.com/public/task/tracking/{}'.format(
            self.tracking_code)

    @property
    def eta(self):
        """
        Estimated time of arrival: start and end datetimes, computed from the
        arrival time and rounding settings

        :type: list(datetime) or None
        """
        if not (self.eta_margin and self.eta_rounding and self.arrival_time):
            return
        start = self.arrival_time - timedelta(minutes=self.eta_margin / 2)
        start -= timedelta(
            minutes=start.minute % self.eta_rounding,
            seconds=start.second,
            microseconds=start.microsecond,
        )
        end = start + timedelta(minutes=self.eta_margin)
        return [start, end]

    def update(self):
        """
        Fetch the latest delivery information from the API.

        :raises urbantz.exceptions.APIError: If the API returned a JSON error.
        :raises requests.exceptions.HTTPError: If the response has an
           HTTP 4xx or 5xx code, or an empty payload.
        """
        resp = requests.get(self.api_url)
        data = {}
        try:
            data = resp.json()
        except Exception:
            pass

        if 'error' in data:
            raise APIError(data['error'])

        resp.raise_for_status()
        if not data:
            # If requests does not raise anything and there is no data,
            # raise our own error
            raise APIError({'message': 'API returned an empty payload'})

        self.use(data)

        # TODO: See if the payload holds a last update value
        self.last_updated = datetime.now()

    def use(self, payload):
        """
        Use a parsed JSON payload to update the properties.

        :param dict payload: A parsed JSON payload from the API.
        """
        self.payload = payload
        self.id = self.payload['_id']
        self.date = datetime.strptime(
            self.payload['date'][:10], "%Y-%m-%d").date()
        self.task_id = self.payload['taskId']
        self.platform_id = self.payload['platform']
        self.driver_id = self.payload['driver']
        self.round_id = self.payload['round']
        self.by = self.payload['by']
        self.instructions = self.payload['instructions']
        self.progress = self.payload['progress']
        self.status = self.payload['status']

        self.arrival_time = datetime.strptime(
            self.payload['arriveTime'], DATE_FORMAT)
        self.eta_margin = self.payload['eta']['margin']
        self.eta_rounding = self.payload['eta']['rounding']
        self.time_window = [
            datetime.strptime(
                self.payload['timeWindow']['start'],
                DATE_FORMAT,
            ),
            datetime.strptime(
                self.payload['timeWindow']['stop'],
                DATE_FORMAT,
            ),
        ]

        self.position = Coordinates.fromJSON(self.payload['position'])
        self.destination = Location.fromJSON(self.payload['location'])
        self.recipient = DictObject(self.payload['contact'])
        self.features = DictObject(self.payload['features'])
        self.template = DictObject(self.payload['template'])
        self.theme = DictObject(self.payload['theme'])
        self.logs = list(map(LogEntry.fromJSON, self.payload['log']))
        self.items = list(map(Item.fromJSON, self.payload['items']))

    @classmethod
    def fromJSON(cls, payload):
        """
        Create a Delivery instance from an existing payload.

        :param payload: A parsed JSON payload.
        :type payload: dict
        """
        instance = cls()
        instance.use(payload)
        return instance

    def toJSON(self):
        return self.payload
