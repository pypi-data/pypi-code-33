import datetime

from .common import *


def parse_woosub1(json_entry):

    subscription_id = str(json_entry["id"])

    # validation

    if len(json_entry["line_items"]) != 1:
        raise Exception("Too many line items in subscription %s" % (id, ))

    line_item = json_entry["line_items"][0]

    quantity = line_item["quantity"]
    if quantity != 1:
        raise Exception("Bad quantity %s in subscription %s" % (quantity, id, ))

    # calculate next renewal date

    next_renewal_naive = datetime.datetime.strptime(json_entry["next_payment_date"], "%Y-%m-%dT%H:%M:%S")
    next_renewal = timezone.make_aware(next_renewal_naive)

    # get account name
    username = get_username_from_woo_customer_id(json_entry["customer_id"])

    # create result

    result = {
        "parser": 2,  # FIXME: this is WOO_SUBSCRIPTION_V1 from purist.limitmonitor
        "external_key": subscription_id,
        "label": json_entry["number"],
        "bundle_key": str(line_item["product_id"]),
        "bundle_label": str(line_item["name"]),
        "quantity": 1,
        "account": username,
        "next_renewal": next_renewal,
    }

    return [result, ]


def monitor_woosub1_new_subscriptions():

    # make connection objects
    woo_connection = get_woo_connection()
    ssh = get_openvpn_ssh_connection()

    # initialise
    result_list = []
    latest_subscription_json = woo_connection.get("subscriptions?orderby=date&order=desc").json()

    # parse recent subscriptions and store results
    for json_entry in latest_subscription_json:
        try:
            product_id = int(json_entry["line_items"][0]["product_id"])
            if product_id in settings.WOOSUB1_PRODUCT_LIST:
                result_list.extend(parse_woosub1(json_entry))
        except Exception as e:
            logger.exception("Skipping JSON entry " + str(json_entry))

    # add new results
    count = 0
    for result in result_list:
        try:

            credit = ExternalCredit(
                parser=result["parser"],
                external_key=result["external_key"],
                label=result["label"],
                bundle_key=result["bundle_key"],
                bundle_label=result["bundle_label"],
                quantity=result["quantity"],
                account_name=result["account"],
                additional_data="None",
                is_converted=False,
            )

            if not is_existing_credit(credit):
                store_credit_and_update_limit(ssh, credit, result["next_renewal"])
                count += 1
            else:
                logger.debug("Skipped existing result " + str(result))
        except Exception as e:
            logger.exception("Skipped bad result " + str(result))

    ssh.close()


def update_limit_woosub1(ssh, credit, renewal_date):

    user, limit, external_bundle = get_limit_objects(credit)
    activate_single_limit(ssh, limit, None, renewal_date)


def monitor_woosub1_renewals():

    # make connection objects
    woo_connection = get_woo_connection()
    ssh = get_openvpn_ssh_connection()

    # get objects due for renewal (one hour grace / buffer)
    now = timezone.now() - datetime.timedelta(hours=1)
    overdue_list = Limit.objects.filter(renewal_date__lte=now,expiry_date=None, is_active=True)

    count = 0
    for limit in overdue_list:

        identity = limit.user.get_identity()
        woosub_bundle_list = ExternalBundle.objects.filter(service=limit.service, parser="WOOSUB1")

        for bundle in woosub_bundle_list:

            woosub_credit = ExternalCredit.objects.get(account_name=identity, bundle_key=bundle.external_key,
                                                       parser="WOOSUB1")

            try:
                subscription_query = "subscriptions/" + woosub_credit.external_key
                woosub_json = woo_connection.get(subscription_query).json()
                result = parse_woosub1(woosub_json)

                # deactivate expired limits
                if not result["active"]:
                    deactivate_single_limit(ssh, limit)
                    woosub_credit.is_converted = False
                    woosub_credit.error_message = "Expired."
                else:
                    store_credit_and_update_limit(ssh, woosub_credit, result["renewal"])
                    woosub_credit.is_converted = True
                    woosub_credit.error_message = ""

                count += 1

            except Exception as e:
                message = "Skipping bad credit %s (%s)." % (woosub_credit.id, woosub_credit.external_code)
                logger.exception(message)
                woosub_credit.is_converted = False
                woosub_credit.error_message = message + repr(e)
            finally:
                woosub_credit.save()

    if count > 0:
        logger.info("Updated %i subscriptions." % (count,))

    ssh.close()
