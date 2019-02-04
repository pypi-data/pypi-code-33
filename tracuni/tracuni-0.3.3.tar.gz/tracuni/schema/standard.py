#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Привязка наборов правил к вариантам

    variant => ruleset

    ruleset = (
        Rule(
            description='',
            destination=Destination(
                section=DestinationSection.SPAN_TAGS,
                name='some'
            ),
            stage=Stage.PRE,
            origins=(
                Origin(section=OriginSection.REUSE, getter='some'),
            ),
            pipeline=(lambda x: x,),
        ),
    )  # type: RuleSet
"""
from typing import TYPE_CHECKING

from tracuni.misc.select_coroutine import is_tornado_on
from tracuni.define.type import (
    Variant,
    SpanSide,
    APIKind,
)


if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ..define.type import RuleSet  # noqa
    from ..define.type import Schema  # noqa

####################
# Подключение стандартных настроек экстракторов

# для варианта будет использован только один из наборов для определённого
# ключа назначения в зависимости от разновидности ключа экстракторы
# применяются в следующем приоритете сверху вниз (если применяется верхний,
# то нижний уже не применяется)
#  - элементы с конкретным вариантом применяются
# только для этого варианта
#  - элементы привязанные только к направлению применяются ко всем вариантам
#  с этим направлением
#  - элементы привязанные по виду API применяются ко всем вариантам с этим
#  видом
#  - непривязанные к вариантам элементы применяются ко всем вариантам
amqp_in_ruleset = tuple()


def get_standard_schema():
    if is_tornado_on():
        from tracuni.schema.builtin import (
            tornado_http_in_ruleset as http_in_ruleset,
            tornado_http_out_ruleset as http_out_ruleset,
            tornado_db_out_ruleset as db_out_ruleset,
            tornado_amqp_out_ruleset as amqp_out_ruleset,
        )
    else:
        from tracuni.schema.builtin import (
            http_in_ruleset,
            http_out_ruleset,
            db_out_ruleset,
            amqp_out_ruleset,
        )
    standard_schema = {
        Variant(SpanSide.IN, APIKind.HTTP): http_in_ruleset,
        Variant(SpanSide.OUT, APIKind.HTTP): http_out_ruleset,
        Variant(SpanSide.IN, APIKind.AMQP): amqp_in_ruleset,
        Variant(SpanSide.OUT, APIKind.AMQP): amqp_out_ruleset,
        Variant(SpanSide.OUT, APIKind.DB): db_out_ruleset,
    }  # type: Schema
    return standard_schema
