import logging

from connexion import NoContent

from tmlib.eiutils import get_or_404
from tmlib.models import Minion


# Authentication imports


def get_tradingminions():
    return get_tradingminion("_NO_NAME")


@get_or_404
def get_tradingminion(tradingminion_name):
    logging.debug("In get_tradingminion")
    logging.debug("Authenticated: going for data")
    if tradingminion_name != "_NO_NAME":
        logging.debug("Looking for specific trading minion: " + tradingminion_name)
        minion = Minion.objects.get(name=tradingminion_name)
        return minion.to_dict(), 200
    else:
        logging.debug("Getting all trading minions")
        results = Minion.objects()
        return [r.to_dict() for r in results], 200


def put_tradingminion(tradingminion_name, tradingminion_body):
    logging.debug("Name in body: " + tradingminion_body['name'])
    if tradingminion_name != tradingminion_body['name']:
        return "Name in JSON body doesn't match path.", 400
    update_result = Minion.objects(name=tradingminion_name).update(
        upsert=True, full_result=True, **{f'set__{k}': v for k, v in tradingminion_body.items()}
    )
    if update_result.acknowledged:
        if update_result.matched_count == 1:
            return_code = 200
            return_text = "Existing record updated."
        else:
            return_code = 201
            return_text = "New record created."
    else:
        logging.exception("The Upsert was not acknowledged by the server.")
        return "The Upsert was not acknowledged by the server.", 400

    return return_text, return_code  # NoContent, (200 if exists else 201)


def delete_tradingminion(tradingminion_name):
    logging.debug("In delete_tradingminion")
    logging.debug("Deleting " + tradingminion_name)
    result = Minion.objects(name=tradingminion_name).delete()
    if result:
        return NoContent, 204
    else:
        return NoContent, 404
