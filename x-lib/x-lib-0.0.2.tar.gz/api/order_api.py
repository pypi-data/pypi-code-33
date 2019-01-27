from flask import Blueprint, request
from slerp.logger import logging

from service.order_service import OrderService

log = logging.getLogger(__name__)

order_api_blue_print = Blueprint('order_api_blue_print', __name__)
api = order_api_blue_print
order_service = OrderService()