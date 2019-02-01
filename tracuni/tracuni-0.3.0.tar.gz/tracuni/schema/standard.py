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

from tracuni.schema.builtin import http_in_ruleset
from tracuni.schema.builtin import http_out_ruleset
from tracuni.schema.builtin import db_out_ruleset
from tracuni.schema.builtin import amqp_out_ruleset

from tracuni.define.type import (
    Variant,
    SpanSide,
    APIKind,
)

from typing import TYPE_CHECKING
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
standard_schema = {
    Variant(SpanSide.IN, APIKind.HTTP): http_in_ruleset,
    Variant(SpanSide.OUT, APIKind.HTTP): http_out_ruleset,
    Variant(SpanSide.IN, APIKind.AMQP): amqp_in_ruleset,
    Variant(SpanSide.OUT, APIKind.AMQP): amqp_out_ruleset,
    Variant(SpanSide.OUT, APIKind.DB): db_out_ruleset,
}  # type: Schema
