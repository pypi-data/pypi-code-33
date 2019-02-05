from .common import *


def get_latest_woo1(connection, product_id):
    return connection.get("orders?product=" + str(product_id))


def parse_woo1(json_entry, product_id):
    result_list = []
    order_name = json_entry["number"]
    order_id = json_entry["id"]

    for line_item in json_entry["line_items"]:
        if line_item["product_id"] == product_id:

            item_id = line_item["id"]
            product_id = line_item["product_id"]
            product_label = line_item["name"]
            quantity = line_item["quantity"]
            account = None  # FIXME: need to get the account
            external_key = str(order_id) + ":" + str(item_id)
            external_label = str(order_name)

            result_list.append({
                "parser": "WOO1",
                "external_key": external_key,
                "label": external_label,
                "product_key": product_id,
                "product_label": product_label,
                "quantity": quantity,
                "account": account,
                "original_email": "",
                "isconverted": False,
            })

    return result_list


def update_limit_woo1(ssh, credit):

    user, limit, external_bundle = get_limit_objects(credit)

    credit_days = int(external_bundle.time_credit * credit.quantity)
    credit_timedelta = timezone.timedelta(days=credit_days)
    activate_single_limit(ssh, limit, credit_timedelta, None)


def monitor_woo1():
    # make connection objects
    woo_connection = get_woo_connection()
    ssh = get_openvpn_ssh_connection()

    # get product sales and parse the results
    result_list = []
    for product_id in settings.WOO_PRODUCT_LIST:
        latest_woo1_json = get_latest_woo1(woo_connection, product_id).json()
        for json_entry in latest_woo1_json:
            try:
                result_list.extend(parse_woo1(json_entry, product_id))
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
                bundle_key=result["product_key"],
                bundle_label=result["product_label"],
                quantity=result["quantity"],
                account_name=result["account"],
                additional_data=result["original_email"],
                is_converted=False,
            )

            if not is_existing_credit(credit):
                store_credit_and_update_limit(ssh, credit)
                count += 1
            else:
                logger.debug("Skipped existing result " + str(result))
        except Exception as e:
            logger.exception("Skipped bad result " + str(result))

    if count > 0:
        logger.info("Added %i new results." % (count,))

    ssh.close()
