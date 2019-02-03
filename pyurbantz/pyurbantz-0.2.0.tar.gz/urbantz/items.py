from datetime import datetime
from urbantz.base import JSONSerializable
from urbantz.utils import DictObject


class LogEntry(DictObject):
    """
    A log entry for a delivery or a delivery item that logs status changes.

    - ``id`` : Unique identifier of the log entry
    - ``by`` : Unique identifier of the author of the change. Nullable.
    - ``when`` : Date/time of the log entry as a ISO 8601 string
    - ``to`` : Updated status
    """

    @property
    def datetime(self):
        """
        Datetime for the log entry.
        """
        from urbantz.delivery import DATE_FORMAT
        return datetime.strptime(self.when, DATE_FORMAT)


class Item(JSONSerializable):
    """
    Describes a delivery item.
    """

    def __init__(self, payload):
        self.payload = payload
        """
        The original JSON payload for the item.

        :type: dict
        """

        self.id = self.payload['_id']
        """
        Unique identifier of the delivery item.

        :type: str
        """

        self.type = self.payload['type']
        """
        Type of the delivery item. Types vary with each company.

        :type: str
        """

        self.barcode = self.payload['barcode']
        """
        Barcode of the delivery item. See :attr:`Item.barcode_encoding` to
        know the barcode's encoding.
        """

        self.barcode_encoding = self.payload['barcodeEncoding']
        """
        Encoding method of the barcode (EAN 13, UPC, etc.)
        """

        self.damage_confirmed = self.payload['damaged']['confirmed']
        """
        Indicates whether the item has been damaged.

        :type: bool
        """

        self.damage_pictures = self.payload['damaged']['pictures']
        """
        Pictures of the damages.
        """

        self.status = self.payload['status']
        """
        Status of the delivery item.

        :type: str
        """

        self.quantity = self.payload['quantity']
        """
        Quantity of the given item.

        :type: int
        """

        self.labels = self.payload['labels']
        """
        Custom labels given to the item.

        :type: list
        """

        self.skills = self.payload['skills']
        """
        Required skills to handle the delivery item.

        :type: list
        """

        self.dimensions = DictObject(self.payload['dimensions'])
        """
        Dimensions of the item, as custom settings set by the shipment company.

        :type: urbantz.utils.DictObject
        """

        self.metadata = DictObject(self.payload['metadata'])
        """
        Metadata about the delivery that seems to be set by UrbanTZ themselves.

        :type: urbantz.utils.DictObject
        """

        self.logs = list(map(LogEntry.fromJSON, self.payload['log']))
        """
        Status update logs.

        :type: urbantz.items.LogEntry
        """

    def __repr__(self):
        return '<Item {}>'.format(self.id)

    def toJSON(self):
        return self.payload

    @classmethod
    def fromJSON(cls, payload):
        return cls(payload)
