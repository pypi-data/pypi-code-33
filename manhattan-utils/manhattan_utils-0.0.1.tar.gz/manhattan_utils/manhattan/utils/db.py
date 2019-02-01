
import mongoframes
from pymongo import ReturnDocument

__all__ = ['auto_inc']


def auto_inc(counter='app'):
    """Return an auto incremented value for the given counter"""

    doc = mongoframes.Frame.get_db().Counter.find_one_and_update(
        {'_id': counter},
        update={
            '$inc': {'count': 1},
            '$set': {'_id': counter}
        },
        upsert=True,
        return_document=ReturnDocument.AFTER
    )

    return doc['count']