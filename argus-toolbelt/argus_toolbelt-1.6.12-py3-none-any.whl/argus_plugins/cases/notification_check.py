from collections import OrderedDict
from datetime import datetime

from argus_api.api.cases.v2.case import advanced_case_search, list_case_history, list_transaction_notifications

from argus_cli.utils.formatting import get_data_formatter, FORMATS
from argus_cli.helpers.log import log
from argus_cli.plugin import register_command
from argus_plugins.cases.utils import get_customer_id


def customer_is_notified(case_id: int, transaction_id: str):
    """Checks if the any of the contacts are NOT a mnemonic email."""
    notifications = list_transaction_notifications(case_id, transaction_id)["data"]

    return any(
        notification["contact"].split("@")[-1] is not "mnemonic.no"
        for notification in notifications
    )


def is_internal_comment(comment: dict):
    try:
        return "INTERNAL" in comment["flags"]
    except KeyError:
        return False


def non_notified_transactions(case):
    """Returns all transactions where the customer wasn't notified and it wasn't an internal comment."""
    transactions = list_case_history(
        case["id"],
        operation=["caseCreate", "addComment", "updateCase"]
    )["data"]

    for transaction in transactions:
        if is_internal_comment(transaction.get("object", {})):
            continue
        elif not customer_is_notified(case["id"], transaction["id"]):
            yield transaction


@register_command(extending="cases")
def notification_check(
        start: datetime, end: datetime,
        exclude_customer: get_customer_id = [],
        format: FORMATS = "csv"
):
    """Outputs all cases where the customer didn't get a notification

    :param start: The start of the search
    :param end:  The end of the search
    :param list exclude_customer: Customer (shortname) to exclude from the search. Mnemonic is automatically excluded
    :param format: How the output will be formatted.
    """
    log.warning("This one-off script is going to be moved after ARGUS-11915 is completed!")

    log.info("Fetching cases...")
    cases = advanced_case_search(
        startTimestamp=int(start.timestamp() * 1000),
        endTimestamp=int(end.timestamp() * 1000),
        subCriteria=[
            {"exclude": True, "customerID": [customer for customer in (exclude_customer + [1])]}
        ],
        limit=0,
    )["data"]
    log.info("Fetched {} cases".format(len(cases)))

    non_notified = []
    for case in cases:
        log.info("Checking case #{}".format(case["id"]))
        for transaction in non_notified_transactions(case):
            non_notified.append({
                "Case ID": case["id"],
                "Customer": case["customer"]["shortName"],
                "Transaction Time": datetime
                    .fromtimestamp(transaction["timestamp"] / 1000)
                    .isoformat(sep=" "),
                "User": transaction["user"]["userName"],
                "Operation": transaction["operation"],
                "Sub-Changes": [change["field"] for change in transaction.get("changes", [])]
            })

    print(get_data_formatter(format)(non_notified))
