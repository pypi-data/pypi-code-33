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
    Iterable,
    Callable,
    Optional,
    Sequence,
    Mapping,
    Dict,
    Union,
    Any,
    Tuple,
    Type,
)
from .define.type import (
    PointContext,
    MethodNameToStage,
    Stage,
)
from .misc.helper import async_decorator
from .span import SpanGeneral


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
                 context: PointContext,
                 custom_endpoint_name: str,
                 ):
        self._positional_names = []
        self._original_args = original_args
        self._original_kwargs = original_kwargs

        point_args = self._compose_kwargs(context.point_ref)

        # noinspection PyProtectedMember
        self.context = PointContext(**{
            **context._asdict(),
            "point_args": point_args,
            "client": context.adapter.client,
            "reuse": {
                "custom_remote_endpoint_name": custom_endpoint_name,
                "error": None,
                "should_not_trace": False,
            },
            "headers": {},
            "span_name": {},
            "span_tags": {},
            "span_logs": [],
        })

    def fab_span_general(self):
        return SpanGeneral(
            self.context.engine.schema_feed.variant.span_side,
            self,
        )

    def apply_wrapped_fn(self) -> Callable:
        kwargs = copy(self._original_kwargs)
        kwargs.update(self.context.point_args._asdict())
        kwargs.pop('method_arguments_without_names')
        args = list(self._original_args)
        for idx, pos_name in enumerate(
            self._positional_names[:len(self._original_args)]
        ):
            args[idx] = kwargs.pop(pos_name, None)

        return partial(self.context.point_ref, *args, **kwargs)

    @async_decorator.coroutine
    def register_stage(self, stage_span_method_name: str) -> Any:
        res = yield from self.context.engine.extract(
            self.context,
            stage_span_method_name,
        )
        return res

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

    def __getitem__(self, code):
        # if not self.composed:
        #     raise PointWrapperError("Object should be populated with arguments before use")

        if all([
            isinstance(code, slice),
            *(getattr(code, el) is None for el in ('start', 'stop', 'step')),
        ]):
            return self._kwargs

        kwarg_setup = {}.get(code)
        if kwarg_setup is None:
            raise IndexError

        return self._kwargs.get(*kwarg_setup)
