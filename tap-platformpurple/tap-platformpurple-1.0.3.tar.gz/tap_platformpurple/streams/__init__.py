from .events import EventsStream
from .transactions import TransactionsStream
from .products import ProductsStream

AVAILABLE_STREAMS = [
    EventsStream,
    TransactionsStream,
    ProductsStream,
]
