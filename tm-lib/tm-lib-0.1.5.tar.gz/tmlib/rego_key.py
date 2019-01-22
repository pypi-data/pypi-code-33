import logging

from connexion import NoContent

from tmlib.eiutils import get_or_404
from tmlib.models import Customer, Registration
from tmlib.tm_obfuscate import deobfuscate, obfuscate


def _regokey_from_json(minion_name, account_number, broker_name, in_json):
    try:
        rego_key = in_json["licenses"][minion_name]["account_registrations"][str(account_number)]["rego_key"]
    except:
        rego_key = ""
    support_expiry = in_json["licenses"][minion_name]["support_expires"]
    # Make the expire MT4 format
    support_expiry = support_expiry.replace("-", ".")

    if rego_key:
        rego_expiry = deobfuscate(rego_key)
        logging.debug("deobf rego key: " + rego_expiry)
        str_start = rego_expiry.find("--")
        if str_start > 0:
            str_start += 2
            rego_expiry = rego_expiry[str_start: str_start + len("1970.01.01")]
        else:
            rego_expiry = ""
    else:
        rego_key = ""
        rego_expiry = ""

    return {
        "minion_name": minion_name,
        "account_number": account_number,
        "broker_name": broker_name,
        "rego_key": rego_key,
        "rego_expiry": rego_expiry,
        "support_expiry": support_expiry
    }


"""
get_regokey
"""


def get_regokey(account_number, broker_name, minion_name):
    logging.debug("In get_regokey")
    # Setup json for accesslog
    access_log_json = {
        "account_number": account_number,
        "broker_name": broker_name,
        "minion_name": minion_name
    }
    logging.debug("Authenticated: going for data")
    logging.debug("Looking for specific account: " + broker_name + "; " + str(account_number) + ";" + minion_name)
    pipelines = [
        {"$match": {"licenses.minion_name": minion_name,
                    "licenses.account_registrations.account_number": account_number,
                    "licenses.account_registrations.broker": broker_name}},
        {"$unwind": "$licenses"},
        {"$unwind": "$licenses.account_registrations"},
        {"$match": {"licenses.minion_name": minion_name,
                    "licenses.account_registrations.account_number": account_number,
                    "licenses.account_registrations.broker": broker_name}},
        {"$project": {
            "_id": 0,
            "rego_key": "$licenses.account_registrations.rego_key",
            "maximum_lots": {"$ifNull": ["$licenses.account_registrations.maximum_lots", None]},
            "support_expires": "$licenses.support_expires"
        }}
    ]
    results = Customer.objects.aggregate(*pipelines)
    results = list(results)
    logging.debug(str(len(results)) + " results returned.")
    if not results:
        return NoContent, 404

    error_code = 200
    access_log_json.update({"registered": True})
    try:
        rego_key = results[0]["rego_key"]
    except:
        rego_key = ""
    support_expiry = results[0]["support_expires"]
    maximum_lots = results[0]['maximum_lots']
    # Make the expire MT4 format

    if rego_key:
        rego_expiry = deobfuscate(rego_key)
        logging.debug("deobf rego key: " + rego_expiry)
        try:
            _, rego_expiry = rego_expiry.split("--")
            rego_expiry = rego_expiry[:len("1970.01.01")]
        except ValueError:
            rego_expiry = ""
    else:
        rego_key = ""
        rego_expiry = ""

    result_json = {
        "minion_name": minion_name,
        "account_number": account_number,
        "broker_name": broker_name,
        "rego_key": rego_key,
        "rego_expiry": rego_expiry,
        "support_expiry": support_expiry,
        "maximum_lots": maximum_lots
    }
    # Write to the access log
    return result_json, error_code


@get_or_404
def put_regokey(customer_login, minion_name, account_number, broker_name, rego_expiry_string='_NO_EXPIRY_STRING',
                in_rego_key='_NO_REGO_KEY'):
    if in_rego_key != '_NO_REGO_KEY':
        rego_key = in_rego_key
    else:
        if rego_expiry_string != '_NO_EXPIRY_STRING':
            rego_key = obfuscate(str(account_number) + "--" + rego_expiry_string)
        else:
            # No expiry - use 1970.01.01 (never expires)
            rego_key = obfuscate(str(account_number) + "--1970.01.01")

    customer = Customer.objects.get(login=customer_login)
    # get license
    account_registration: Registration = customer.get_account_registration(
        minion_name=minion_name, account_number=account_number,
        broker_name=broker_name
    )
    account_registration.rego_key = rego_key
    customer.save()
    return "Rego key updated.", 200


@get_or_404
def delete_regokey(customer_login, account_number, minion_name, broker_name):
    print("In delete_regokey")
    customer = Customer.objects.get(login=customer_login)
    account_registration: Registration = customer.get_account_registration(
        account_number=account_number, minion_name=minion_name,
        broker_name=broker_name
    )
    account_registration.rego_key = ''
    customer.save()
    return NoContent, 204


"""
eof delete_regokey
"""
