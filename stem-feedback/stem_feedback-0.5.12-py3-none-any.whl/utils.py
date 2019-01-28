import json


def get_json_event(feed_back_type, subject, message, customer_id, customer_erp_id,
                   customer_name, user_id, user_name, email):
    json_str = dict()
    json_str['type'] = str(feed_back_type)
    json_str['subject'] = str(subject)
    json_str['message'] = str(message)
    cust = {"customer_id": customer_id, "customer_erp_id": customer_erp_id, "customer_name": customer_name}
    usr = {"user_id": user_id, "user_name": user_name, "email": email, "customer": cust}
    json_str['user'] = usr
    return str(json_str)


def get_json_notification(feed_back_type, payment_type, subject, message, sum, currency_iso_id, currency_abbr,
                          customer_id, customer_erp_id, customer_name, user_id, user_name, email):
    json_str = dict()
    json_str['type'] = str(feed_back_type)
    json_str['subject'] = str(subject)
    json_str['message'] = str(message)
    cust = {"customer_id": customer_id, "customer_erp_id": customer_erp_id, "customer_name": customer_name}
    usr = {"user_id": user_id, "user_name": user_name, "email": email, "customer": cust}
    json_str['user'] = usr
    cur = {
            'iso_id': currency_iso_id.encode("utf-8"),
            'abbr': currency_abbr,
        }
    json_str['doc'] = {
        'payment_for': payment_type,
        'sum': sum,
        'currency': cur}
    return str(json_str)


def get_json_moneyback(feed_back_type, subject, message, doc_number, doc_date,
                       customer_id, customer_erp_id, customer_name, user_id, user_name, email,
                       reason_for_the_return, ship, tracking_number, orders, attachments):
    json_str = dict()
    json_str['type'] = feed_back_type
    json_str['subject'] = str(subject)
    json_str['message'] = str(message)
    cust = {"customer_id": customer_id, "customer_erp_id": customer_erp_id, "customer_name": customer_name}
    usr = {"user_id": user_id, "user_name": user_name, "email": email, "customer": cust}
    json_str['user'] = usr
    json_str['doc'] = {
        'type': 'РН',
        'number': doc_number,
        'date': doc_date
        },

    json_str['reason'] = reason_for_the_return,
    json_str['ship'] = str(ship),
    json_str['tracking_number'] = str(tracking_number)
    json_str['attachments'] = attachments
    json_str['products'] = str(orders)

    return str(json_str)
