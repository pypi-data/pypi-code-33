from collections import OrderedDict

from django.utils.translation import ugettext_lazy as _


class Container:
    UNDEFINED = 0

    MAP = OrderedDict([
        (UNDEFINED, _("Undefined"))
    ])

    @classmethod
    def choices(cls):
        choices = []
        for code, name in cls.MAP.items():
            choices.append((code, name))

        return choices

    @classmethod
    def get_name_by_code(cls, code):
        return cls.MAP.get(code, cls.MAP.get(cls.UNDEFINED))


class ServicesContainer(Container):
    # CONSTANTS
    UNDEFINED = 0
    TUNNEL = 1
    COMMUNICATION = 2

    # MAPPING
    MAP = OrderedDict([
        (UNDEFINED, _("Undefined")),
        (TUNNEL, _("Tunnel")),
        (COMMUNICATION, _("Communication")),
    ])


class ParserContainer(Container):
    # CONSTANTS
    UNDEFINED = 0
    WOO_PRODUCT_V1 = 1
    WOO_SUBSCRIPTION_V1 = 2

    # MAPPING
    MAP = OrderedDict([
        (UNDEFINED, _("Undefined")),
        (WOO_PRODUCT_V1, _("WooCommerce Product v1")),
        (WOO_SUBSCRIPTION_V1, _("WooCommerce Subscription v1")),
    ])
