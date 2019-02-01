#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Обработка участков на каждом этапе
"""
from functools import wraps

from tracuni.misc.select_coroutine import async_decorator
from tracuni.define.type import (
    SpanSide,
    Stage,
)
import tracuni.define.errors as err

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from aiozipkin.span import Span
    from typing import Dict
    from tracuni.define.type import MethodNameToStage


class ProvideSpanForStage:
    """Декоратор для методов этапа
            * Гарантирует наличие экземпляра участка
            * Получает наполнение для текущей стадии
            * Сохранят результат вызова точки

        Parameters
        ----------
        stage
            Привязывает декорированный метод к конкретному этапу. Если таких
            несколько, то привязывается только первый обработанный

        Returns
        -------
            Метод обработки определённого этапа
    """
    # Отношение наименований методов аксессора точки к запускаемым фазам
    # извлечения, отрабатывающим до выполнения этих методов.
    method_to_stage = {
        # 'run_init_stage': Stage.INIT,
        # 'run_pre_stage': Stage.PRE,
        # 'run_post_stage': Stage.POST,
    }  # type: MethodNameToStage

    stage_to_method = {}  # type: Dict[Stage, str]

    def __init__(self, stage: Stage):
        self.stage = stage

    def __call__(self, fn):
        # Сохраняем прямое и обраное отображение этапов на методы обработки
        self.fn_name = fn_name = fn.__name__
        if fn_name and self.stage not in self.method_to_stage:
            self.method_to_stage[fn_name] = self.stage
            self.stage_to_method[self.stage] = fn_name

        @wraps(fn)
        @async_decorator
        def wrapper(span_general_inst):
            self.span_general_inst = span_general_inst
            self.point = span_general_inst.point

            stage_found = self._detect_stage()
            self._stage_operations(stage_found)
            yield from self._run_stage_pipe(stage_found)
            span_instance = self._create_span_inst_if_none()

            fn(
                span_general_inst,
                span_instance,
            )

            return

        return wrapper

###############################################################################
# Area privata

    def _detect_stage(self):
        # Определяем текущий этап
        stage_found = self.method_to_stage.get(self.fn_name)
        if not stage_found:
            raise err.SpanNoStageForMethod

        return stage_found

    def _stage_operations(self, stage_found):
        # Для этапа после вызова точки сохраняем результат её работы
        if stage_found == Stage.POST:
            result = None
            if (
                not result
                and
                hasattr(
                    self.point.context.point_args,
                    'self',
                )
                and
                hasattr(
                    self.point.context.point_args.self,
                    'response_body',
                )
            ):
                result = self.point.context.point_args.self.response_body
            if self.point.context.point_result is None:
                self.point.update_context({"point_result": result})

    @async_decorator
    def _run_stage_pipe(self, stage_found):
        # Вызываем извлечение и обработку данных этапа
        pipe_fn = self.point.context.engine.extract
        point_context = yield from pipe_fn(self.point.context, stage_found)
        self.point.context = point_context

        # отмечаем, если произошла ошибка
        error = point_context.reuse.get('error')
        if error:
            self.span_general_inst.error = str(error)

    def _skip_http(self):
        # обрабатываем выставленный обработчиками флаг пропуска
        if self.point.context.reuse.get('should_not_trace'):
            raise err.HTTPPathSkip

    def _create_span_inst_if_none(self):
        # создаём участок, если он ещё не создан
        span_instance: Span = getattr(
            self.span_general_inst,
            'span_instance',
            None
        )
        if span_instance is None:
            if self.span_general_inst.side == SpanSide.IN:
                span_instance = self.span_general_inst.fab_in_span()
            elif self.span_general_inst.side == SpanSide.OUT:
                span_instance = self.span_general_inst.fab_out_span()

            if span_instance is None:
                raise err.NoSpanException
            self.span_general_inst.span_instance = span_instance

        if not self.point.context.span:
            self.point.update_context({"span": self.span_general_inst})

        return span_instance
