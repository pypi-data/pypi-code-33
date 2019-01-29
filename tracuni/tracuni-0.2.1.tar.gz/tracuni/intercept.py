#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Перехват вызова интересующей точки
    Во время перехвата запускается процесс сбора, обработки и записи данных,
    согласно связаным с перехватчиком набором правил
"""
import time
import inspect
import logging
from functools import wraps
from typing import (
    Optional,
    Callable,
)

from tracuni.adapter import TracerWrapperRef
from tracuni.schema.engine.engine import SchemaEngine
from tracuni.span import (
    SpanGeneral,
)
from tracuni.point_accessor import (
    PointAccessor,
    PointContext,
)
from tracuni.define.const import (
    PATH_IGNORE_METHODS,
    PATH_IGNORE_PIECE,
    UNKNOWN_NAME,
    COLLECT_TRACE,
)
from tracuni.define.type import (
    Variant,
    RuleSet,
    Stage,
)
import tracuni.define.errors as err
from tracuni.misc.helper import (
    async_decorator,
    compose_own_call_stack,
    PostgreSQLError,
)


def tracer_point(
        variant: Variant,
        endpoint_name: str = None,
        point_ruleset: RuleSet = None,
):
    """

    Parameters
    ----------
    variant
        Назначить вариант обработки точки
    endpoint_name
        Здесь можно передать пользовательское имя удаленной точки
        при этом можно использовать и стандартное, указав в строке место
        подстановки с именем standard: 'mine: {standard}'
    point_ruleset
        Здесь можно передать свой вариант настройки извлечения формат такой
        же как значение одного из ключей стандартной настройки она заменит
        стандартную настройку конкретного варианта для данной точки,
        если же последним элементом пользовательской настройки будет строка
        '...', то пользовательская объединится со стандартной с приоритетом
        пользовательской в любом случае далее удут применены менее
        специфичные и менее приоритетные настройки, относящиеся к данной точке

    Returns
    -------
        Декорированный метод, вызов которого будет трассироваться

    """
    # создание экземпляра обработчика
    schema_engine = SchemaEngine(variant, point_ruleset)
    # подписываемся, чтобы знать состояние трассера
    TracerWrapperRef.register_state_observer(schema_engine)

    def wrapper(point_coro):
        @wraps(point_coro)
        @async_decorator.coroutine
        def decorated(*args, **kwargs):
            # сразу запускаем обернутую точку, если трассер выключен,
            # не соединился или не создан
            if schema_engine.is_tracer_disabled():
                result = yield from point_coro(*args, **kwargs)
                return result
            debug_is_on = schema_engine.adapter.config.debug

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
                frame = inspect.currentframe()
                while frame:
                    frame_list.append(frame)
                    frame = frame.f_back
                stack_frames = (
                    # добавить название вызываемого метода
                    *stack_frames,
                    *compose_own_call_stack(
                        PATH_IGNORE_METHODS,  # пропустить методы с именами
                        PATH_IGNORE_PIECE,  # пропустить модули по такому пути
                        name_dummy=UNKNOWN_NAME,  # не найденные имена
                        result_length=5,  # общий размер списка не превышает
                        from_index=1,  # начинать просмотр стэка с позиции
                        look_up_stop_idx=10,  # не просматривать дальше позиции
                        frame_list=frame_list,  # стэк
                    )
                )

            result = {}
            point_fn = None
            this_span: Optional[SpanGeneral] = None

            try:
                point_context = PointContext(
                    point_ref=point_coro,
                    adapter=schema_engine.adapter,
                    engine=schema_engine,
                    call_stack=stack_frames if stack_frames else {},
                )
                point = PointAccessor(
                    args,
                    kwargs,
                    point_context,
                    endpoint_name,
                )
                # создаем спан сконфигрированный по варианту и связанный с
                # ним и точкой
                this_span = point.fab_span_general()
                # если не создан участок переходим к прямому вызову
                if this_span:
                    yield from this_span.get_stage_method(Stage.INIT)()
                    # создаем участок, заполняем его данными доступными до
                    # вызова получаем готовый обернутый метод для вызова точки
                    pre_method = this_span.get_stage_method(Stage.PRE)
                    point_fn = yield from pre_method()  # type: Callable

            except Exception as e:
                # если здесь вылетели, то рабочий участок создать не удалось
                # schema_engine.tracer_wrap.log_debug('Error in tracer: {
                # }'.format(e))
                this_span = None
                if debug_is_on:
                    if not isinstance(
                        e,
                        (err.HTTPPathSkip, err.SpanNoParentException)
                    ):
                        logging.exception(e)
                    else:
                        logging.debug(e)

            finally:
                # в любом случае должны вызвать обернутую точку
                if point_fn and this_span:
                    # если обертка точки создана вызваем через неё
                    try:
                        result = yield from point_fn()
                    except (Exception, PostgreSQLError) as e:
                        # фиксируем данные об исключении
                        # ProgrammingError - ошибки обработки SQL запроса
                        if debug_is_on:
                            logging.exception(e)
                        this_span.register_error(e)
                    finally:
                        # так или иначе пробуем завершить формирование
                        # участка трассера
                        try:
                            result = yield from this_span.get_stage_method(
                                Stage.POST
                            )(
                                result
                            )
                        except Exception as e:
                            if debug_is_on:
                                logging.exception(e)

                else:
                    # если обертки точки нет, трассер не используется,
                    # вызываем напрямую
                    result = yield from point_coro(*args, **kwargs)

            return result

        return decorated

    return wrapper
