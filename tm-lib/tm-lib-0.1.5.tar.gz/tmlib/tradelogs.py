from mongoengine import ValidationError

from tmlib.models import TradeLog


def get_trade_logs(ticket=None):
    """
    Get trade logs by ticket ID;
    Return all the logs if no ticket id is specified
    :param ticket:
    :return:
    """
    mongo_filter = {}
    if ticket:
        mongo_filter['ticket'] = ticket
    trade_logs: TradeLog = TradeLog.objects_without_id(**mongo_filter)
    return [t.to_mongo() for t in trade_logs], 200


def post_trade_logs(tradelogs_body):
    """
    Add a new trade log. Proxy function for the put method
    :param tradelogs_body:
    :return:
    """
    return put_trade_logs(tradelogs_body)


def put_trade_logs(tradelogs_body):
    """
    Add a new trade log.
    :param tradelogs_body:
    :return:
    """
    account = tradelogs_body.get('account')
    ticket = tradelogs_body.get('ticket')
    try:
        trade_log = TradeLog.objects(account=account, ticket=ticket).update(
            upsert=True, full_result=True, **{f'set__{k}': v for k, v in tradelogs_body.items()}
        )
        if trade_log.matched_count == 1:
            status = 200
        else:
            status = 201
        res = TradeLog.objects.get(account=account, ticket=ticket).to_dict()
    except ValidationError as e:
        status = 400
        res = {
            "detail": e.message,
            "status": status,
            "title": "Bad Request",
            "type": "about:blank"
        }
    return res, status
