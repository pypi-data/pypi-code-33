#!/usr/bin/env python3
import json
import logging

from connexion import NoContent
from mongoengine.errors import ValidationError

# Import utils
from tmlib.models import Customer, License, Registration


def get_customers():
    return get_customer("_NO_NAME")


def get_customer(customer_login):
    logging.debug("In get_customer")
    logging.debug("Authenticated: going for data")

    if customer_login != "_NO_NAME":
        logging.debug("Looking for specific customer: " + customer_login)
        try:
            customer = Customer.objects.get(login=customer_login)
            customer = json.loads(customer.to_json())
            customers = customer
        except Customer.DoesNotExist:
            return NoContent, 404
    else:
        logging.debug("Getting all customers")
        customers = [json.loads(c.to_json()) for c in Customer.objects()]
    return customers


def put_customer(customer_login, given_name, surname):
    try:
        update_result = Customer.objects(login=customer_login).update(
            set__given_name=given_name, set__surname=surname,
            upsert=True, full_result=True
        )

        if update_result.acknowledged:
            if update_result.matched_count == 1:
                return_code = 200
                return_text = "Existing customer updated."
            else:
                return_code = 201
                return_text = "New customer created."
        else:
            logging.exception("The Upsert was not acknowledged by the server.")
            return "The Upsert was not acknowledged by the server.", 400
    except ValidationError as validation_error:
        return_text = validation_error.message
        return_code = 400

    return return_text, return_code


def delete_customer(customer_login):
    logging.debug("In delete_customer")
    logging.debug("Deleting " + customer_login)
    if Customer.objects(login=customer_login).delete():
        return NoContent, 204
    return NoContent, 404


def get_licenses(customer_login):
    logging.debug("In get_licenses")
    logging.debug("Authenticated: going for data")
    try:
        licenses = Customer.objects.get(login=customer_login).licenses
        return [l.to_mongo() for l in licenses], 200
    except Customer.DoesNotExist:
        return [], 404


def get_license(customer_login, minion_name):
    logging.debug("In get_license")
    logging.debug("Authenticated: going for data")
    data, status = {}, 200
    try:
        customer = Customer.objects.get(
            login=customer_login, licenses__minion_name=minion_name
        )
        data = next(l.to_mongo() for l in customer.licenses if l.minion_name == minion_name)
    except (Customer.DoesNotExist, StopIteration):
        status = 404
    return data, status


def put_license(customer_login, wp_membership_id, minion_name,
                minion_license, support_expires):
    # See if the minion already exists
    try:
        customer = Customer.objects.get(login=customer_login)
    except Customer.DoesNotExist:
        return "Customer does not exists", 404
    license: License = next(
        (l for l in customer.licenses if l.minion_name == minion_name),
        None
    )
    if license:
        license.wp_membership_id = wp_membership_id
        license.minion_license = minion_license
        license.support_expires = support_expires
        return_code = 200
        return_text = "Existing customer updated."
    else:
        new_license = License(
            minion_name=minion_name,
            wp_membership_id=wp_membership_id,
            minion_license=minion_license,
            support_expires=support_expires
        )
        customer.licenses.append(new_license)
        return_code = 201
        return_text = "New customer created."
    try:
        customer.save()
    except ValidationError as validation_error:
        return_text = validation_error.message
        return_code = 400
    return return_text, return_code


def get_license_accounts(customer_login, minion_name):
    logging.debug("In get_license_account")
    logging.debug("Authenticated: going for data")
    try:
        Customer.objects.get(login=customer_login)
    except Customer.DoesNotExist:
        return [], 404

    pipeline = [
        {"$match": {"login": customer_login}},
        {"$unwind": "$licenses"},
        {"$match": {"licenses.minion_name": minion_name}},
        {"$unwind": "$licenses.account_registrations"},
        {"$project": {
            "_id": 0,
            "account_number": "$licenses.account_registrations.account_number",
            "broker": "$licenses.account_registrations.broker",
            "maximum_lots": {"$ifNull": ["$licenses.account_registrations.maximum_lots", None]},
            "rego_key": "$licenses.account_registrations.rego_key",
            "checkins": "$licenses.account_registrations.maximum_lots"}}
    ]

    data = Customer.objects.aggregate(*pipeline)
    return list(data), 200


def get_license_account(customer_login, minion_name, account_number):
    logging.debug("In get_license_account")
    logging.debug("Authenticated: going for data")
    try:
        Customer.objects.get(login=customer_login)
    except Customer.DoesNotExist:
        return [], 404

    pipeline = [
        {"$match": {"login": customer_login}},
        {"$unwind": "$licenses"},
        {"$unwind": "$licenses.account_registrations"},
        {"$match": {
            "licenses.minion_name": minion_name,
            "licenses.account_registrations.account_number": account_number
        }},
        {"$project": {
            "_id": 0,
            "account_number": "$licenses.account_registrations.account_number",
            "broker": "$licenses.account_registrations.broker",
            "maximum_lots": {"$ifNull": ["$licenses.account_registrations.maximum_lots", None]},
            "rego_key": "$licenses.account_registrations.rego_key",
            "checkins": "$licenses.account_registrations.checkins"
        }}
    ]

    data = Customer.objects.aggregate(*pipeline)
    data = list(data)
    data = data.pop() if data else {}
    return data, 200


def put_license_account(customer_login, minion_name, account_number,
                        broker_name, maximum_lots=None, in_rego_key=""):
    return_text = ""
    return_code = 200
    try:
        # get customer
        customer = Customer.objects.get(login=customer_login)
        # license by minion_name
        license: License = next(
            (l for l in customer.licenses if l.minion_name == minion_name),
            None
        )
        if license is None:
            raise Customer.DoesNotExist()

        account: Registration = next(
            (a for a in license.account_registrations if a.account_number == account_number),
            None
        )
        if account:
            # update if exists
            account.broker = broker_name
            return_code = 200
            return_text = "Existing customer updated."
        else:
            # create a new account
            account = Registration(broker=broker_name, account_number=account_number)
            license.account_registrations.append(account)
            return_code = 201
            return_text = "New customer created."
        if in_rego_key:
            account.rego_key = in_rego_key
        # save data to mongo
        if maximum_lots:
            account.maximum_lots = maximum_lots
        customer.save()
    except Customer.DoesNotExist:
        return_code = 404
        return_text = "Does not exists"
    except (ValidationError, Exception) as err:
        return_code = 400
        return_text = err.message
    finally:
        return return_text, return_code
