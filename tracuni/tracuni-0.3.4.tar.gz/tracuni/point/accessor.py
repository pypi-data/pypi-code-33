#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль доступа к вызываемой точке

"""
from collections import namedtuple
from copy import copy
from functools import partial
from inspect import signature, Parameter
from typing import (
    NamedTuple,
    Callable,
    Sequence,
    Dict,
    Any,
)

from tracuni.misc.select_coroutine import async_decorator
from tracuni.point.span_general import SpanGeneral
from tracuni.misc.helper import compose_own_call_stack
from tracuni.define.const import (
    PATH_IGNORE_METHODS,
    PATH_IGNORE_PIECE,
    COLLECT_TRACE,
)
from tracuni.define.type import (
    PointContext,
    Stage,
)


class PointAccessor:
    """Доступ к точке вызова и связанным с ней данным

    * Хранит контекст: ссылки на точку, аргументы, сокращённый стек вызовов
    и схему варианта точки
    * Преобразует все аргументы к именованным, основываясь на сигнатуре
    точки и переданным именованным аргументам для упрощения доступа к ним
    * Копирует записываемое в трассер содержимое аргументов перед их
    модификацией
    * Регистрирует сигнал о достижении определённой фазы, вызывает извлечение
    данных этой фазы по схеме варианта
    * Хранит извлеченные данные в определённой структуре, предназначенной
    для записи в трассер и для переиспользования на последующих шагах работы
    экстрактора
    * Модифицирует ограниченное множество аргументов (заголовки HTTP)
    * Вызывает точку с оригинальными и модифицированными аргументами
    """

    def __init__(self,
                 original_args: Sequence,
                 original_kwargs: Dict,
                 point_context: PointContext):
        self._positional_names = []
        self._original_args = original_args
        self._original_kwargs = original_kwargs
        self._applied_point = None
        self._done = False

        point_args = self._compose_kwargs(point_context.point_ref)

        # noinspection PyProtectedMember
        self.context = PointContext(**{
            **point_context._asdict(),
            "point_args": point_args,
        })
        self._span_general = SpanGeneral(
            self.context.engine.schema_feed.variant.span_side,
            self,
        )

    def stack_frames_to_context(self, current_frame):
        point_coro = self.context.point_ref
        stack_frames = (
            # первым элементом - название вызываемого метода
            {
                'full_path': point_coro.__qualname__,
                'short_path': point_coro.__name__,
            },
        )
        if COLLECT_TRACE:
            # собрать данные по стэку вызовов в данной точке
            # inspect.getouterframes(inspect.currentframe())

            frame_list = []
            frame = current_frame
            while frame:
                frame_list.append(frame)
                frame = frame.f_back
            stack_frames = (
                # добавить название вызываемого метода
                *stack_frames,
                *compose_own_call_stack(
                    PATH_IGNORE_METHODS,  # пропустить методы с именами
                    PATH_IGNORE_PIECE,  # пропустить модули по такому пути
                    result_length=5,  # общий размер списка не превышает
                    from_index=1,  # начинать просмотр стэка с позиции
                    look_up_stop_idx=10,  # не просматривать дальше позиции
                    frame_list=frame_list,  # стэк
                )
            )
        # noinspection PyProtectedMember
        self.context = PointContext(**{
            **self.context._asdict(),
            "call_stack": stack_frames,
        })

    def apply_point(self):
        kwargs = copy(self._original_kwargs)
        # noinspection PyProtectedMember
        kwargs.update(self.context.point_args._asdict())
        kwargs.pop('method_arguments_without_names')
        args = list(self._original_args)
        for idx, pos_name in enumerate(
            self._positional_names[:len(self._original_args)]
        ):
            args[idx] = kwargs.pop(pos_name, None)

        self._applied_point = partial(self.context.point_ref, *args, **kwargs)

    @async_decorator
    def run(self):
        # если обертка точки создана вызваем через неё
        result = None
        if self.context.span and self._applied_point:
            result = yield from self._applied_point()
            self._done = True
            self.update_context({"point_result": result})
        return result

    def has_not_been_done(self):
        return not self._done

    @async_decorator
    def register_stage(self, stage: Stage):
        yield from self._span_general.run_stage(stage)

    @async_decorator
    def register_error(self, e):
        yield from self._span_general.register_error(e)

    @async_decorator
    def register_own_error(self, e):
        self._span_general.emergency_exit(e)

    def update_context(self, new_data):
        # noinspection PyProtectedMember
        self.context = PointContext(**{
            **self.context._asdict(),
            **new_data,
        })

    def _compose_kwargs(self, point_ref: Callable) -> NamedTuple:
        sig = signature(point_ref).parameters
        self._positional_names = arg_names = [
            el
            for el in sig
            if el not in ('args', 'kwargs')
        ]
        kwargs = copy(self._original_kwargs)
        args = copy(self._original_args)
        kwargs.update(zip(arg_names, args))

        param_desc = sig
        for param in param_desc:
            pass_value = kwargs.get(param, param_desc.get(param).default)
            if pass_value != Parameter.empty:
                kwargs[param] = pass_value

        kwargs_l = len(kwargs)
        kwargs.update({'method_arguments_without_names': None})
        if kwargs_l < len(args):
            kwargs['method_arguments_without_names'] = args[kwargs_l:]

        point_args = namedtuple(
            'PointArguments',
            kwargs
        )(**kwargs)

        return point_args
