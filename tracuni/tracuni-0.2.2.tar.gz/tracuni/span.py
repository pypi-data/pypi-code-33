import inspect
import re
from functools import wraps

from aiozipkin.span import Span
import aiozipkin as az

from typing import (
    TYPE_CHECKING,
    Callable,
)

from tracuni.misc.helper import async_decorator
from tracuni.define.type import (
    SpanSide,
    UNKNOWN_NAME,
    Stage,
)
import tracuni.define.errors as err

if TYPE_CHECKING:
    from tracuni.point_accessor import PointAccessor
    from tracuni.point_accessor import MethodNameToStage
    from typing import Dict


# Отношение наименований методов аксессора точки к запускаемым фазам
# извлечения, отрабатывающим до выполнения этих методов.
method_to_stage = {
    # 'run_init_stage': Stage.INIT,
    # 'run_pre_stage': Stage.PRE,
    # 'run_post_stage': Stage.POST,
}  # type: MethodNameToStage

stage_to_method = {
}  # type: Dict[Stage, str]


def provide_span(stage: Stage, *args, **kwargs):
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
    def wrapper(fn):
        method_name = fn.__name__
        if method_name and stage not in method_to_stage:
            method_to_stage[method_name] = stage
            stage_to_method[stage] = method_name
        # Сохраняем прямое и обраное отображение этапов на методы обработки
        @wraps(fn)
        @async_decorator.coroutine
        def decorated(self, *args, **kwargs):
            # Определяем текущий этап
            stage_found = method_to_stage.get(method_name)
            if not stage_found:
                raise err.SpanNoStageForMethod

            # Для этапа после вызова точки сохраняем результат её работы
            if stage_found == Stage.POST:
                result = None
                if len(args):
                    result = args[0]
                if (
                    not result
                    and
                    hasattr(self.point.context.point_args, 'self')
                    and
                    hasattr(self.point.context.point_args.self,
                            'response_body')
                ):
                    result = self.point.context.point_args.self.response_body
                self.point.update_context({"point_result": result})

            # Вызываем извлечение и обработку данных этапа
            point_context = yield from self.point.register_stage(stage_found)
            self.point.context = point_context

            # отмечаем, если произошла ошибка
            error = point_context.reuse.get('error')
            if error:
                self.error = str(error)


            # обрабатываем выставленный обработчиками флаг пропуска
            if point_context.reuse.get('should_not_trace'):
                raise err.HTTPPathSkip

            # создаём участок, если он ещё не создан
            span_inst: Span = getattr(self, 'span_instance', None)
            if span_inst is None:
                if self.side == SpanSide.IN:
                    self.span_instance = self._fab_in_span()
                elif self.side == SpanSide.OUT:
                    self.span_instance = self._fab_out_span()
                span_inst = getattr(self, 'span_instance', None)
            if span_inst is None:
                raise err.NoSpanException

            if not self.point.context.span:
                self.point.update_context({"span": self})

            res = fn(self, span_inst, *args, **kwargs)
            return res

        return decorated

    return wrapper


class SpanGeneral:
    """Общая функциональность передачи данных на трассер

        * Реализует логику создания разных вариантов участков:
            * Входящий / Исходящий
            * С родительским контекстом / Без него
        * Записывает подготовленные данные в участок
            * В наименование
            * В заголовок
            * В аннотации

    """
    def __init__(self, side: SpanSide, point: 'PointAccessor'):
        self.span_instance = None
        self.side = side
        self.point = point
        self.tracer: az.Tracer = point.context.adapter.tracer
        self.error = None
        self.has_been_started = False

###############################################################################
# Создание участков для каждого из двух направлений
# Задействуются декоратором provide_span

    def _fab_in_span(self):
        # если в перехватываемых данных есть загловки трасера,
        # создаем дочерний входящий участок,
        # иначе создаем корневой входящий участок
        headers = self.point.context.headers
        context = az.make_context(headers)
        span_instance: Span = (
            self.tracer.new_trace()
            if context is None else
            self.tracer.new_child(context)
        )
        span_instance.kind(az.SERVER)
        # сохраняем идентификаторы входящего участка
        # все исходящие участки в данном дереве асинхронных вызовов
        # будут использовать его в качестве родительского контекста
        self.point.context.adapter.keep_context.set(
            'span',
            span_instance.context.make_headers(),
        )

        return span_instance

    def _fab_out_span(self):
        # если в контексте нет входящего участка,
        # то исходящая точка вызывается вне сценария трассровки,
        # возвращаемся в перехватчик и делаем прямой вызов без трассировки
        in_span_context = self.point.context.adapter.keep_context.get('span')
        if in_span_context is None:
            raise err.SpanNoParentException
        # исходящий участок всегда создаётся как дочерний к входящему
        in_span_context = az.make_context(in_span_context)
        span_instance = self.tracer.new_child(in_span_context)
        span_instance.kind(az.CLIENT)

        return span_instance

###############################################################################
# Методы прохождения по этапу

    @provide_span(Stage.INIT)
    def run_init_stage(self, span: Span):
        self.has_been_started = True
        span.start()
        self._load()

    @provide_span(Stage.PRE)
    def run_pre_stage(self, _: Span) -> Callable:
        if not self.has_been_started:
            raise err.SpanIsNotStartedException
        self._load()

        return self.point.apply_wrapped_fn()

    @provide_span(Stage.POST)
    def run_post_stage(self, span: Span, result):
        if not self.has_been_started:
            raise err.SpanIsNotStartedException
        self._load()
        span.finish(exception=self.error)

        return result

    def get_stage_method(self, stage: Stage):
        return getattr(self, stage_to_method.get(stage), lambda _: None)

    def register_error(self, e: Exception):
        self.error = e

    def enrich_headers(self, headers: dict, prefix_key=None):
        tracer_headers = self.span_instance.context.make_headers()
        if prefix_key:
            tracer_headers = {
                prefix_key: tracer_headers
            }
        headers.update(tracer_headers)
        return headers

###############################################################################
# Area privata
    def _load(self):
        span = self.span_instance
        span_name = self.point.context.span_name
        span_tags = self.point.context.span_tags
        span_logs = self.point.context.span_logs

        span.name(span_name.get('name', UNKNOWN_NAME))
        custom_remote = self.point.context.reuse['custom_remote_endpoint_name']
        standard_remote = span_name.get('remote_endpoint', UNKNOWN_NAME)
        remote = (
            custom_remote.format(**{'standard': standard_remote})
            if custom_remote else
            standard_remote
        )
        span.remote_endpoint(remote)

        if span_logs is None:
            span_logs = []
        if span_tags is None:
            span_tags = {}

        for log_item in span_logs:
            if log_item:
                self.span_instance.annotate(log_item)
        self.point.update_context({"span_logs": []})
        for tag_name, tag_value in span_tags.items():
            if tag_value:
                self.span_instance.tag(tag_name, tag_value)
