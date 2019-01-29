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
    Rule,
    Destination,
    DestinationSection,
    Origin,
    OriginSection,
    Stage,
)

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict
    # noinspection PyUnresolvedReferences
    from ..define.type import RuleSet  # noqa
    from ..define.type import Schema  # noqa
    from ..define.type import StageToSections  # noqa
    from ..define.type import MethodNameToStage  # noqa


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
standard_schema = {
    Variant(SpanSide.IN, APIKind.HTTP): http_in_ruleset,
    Variant(SpanSide.OUT, APIKind.HTTP): http_out_ruleset,
    # Variant(SpanSide.IN, APIKind.AMQP): amqp_in,
    Variant(SpanSide.OUT, APIKind.AMQP): amqp_out_ruleset,
    Variant(SpanSide.OUT, APIKind.DB): db_out_ruleset,
}  # type: Schema


####################
# Внутренние настройки разбора и применения правил извлечения

# Наличие данных секций в правиле относит его к начальной (INIT) или
# завершающей (POST) фазе, если стадия в правиле не указана явно. Приоритетом
# обладает завершающая фаза.
# Без указания фазы правило будет работать перед обращением к точке перехвата
# (PRE).
stage_to_sections = {
    Stage.INIT: [
        DestinationSection.REUSE,
    ],
    Stage.POST: [
        OriginSection.POINT_RESULT,
    ],
}  # type: StageToSections

secret_mask_method_name = 'pipe_secret'
