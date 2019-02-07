from functools import partial

from tracuni.define.type import (
    Rule,
    Destination,
    DestinationSection,
    Origin,
    OriginSection,
    Stage,
)
from tracuni.schema.builtin.pipe import (
    ext_http_in_tornado_request,
    pipe_head,
    pipe_check_skip,
    pipe_sep_string,
    pipe_catch_essential,
    pipe_mask_secret,
    pipe_dump,
    pipe_cut,
)
from tracuni.misc.helper import (
    json_dumps_with_dt,
)


ruleset = (
    Rule(
        description="Получить данные запроса и сохранить"
                    "для переиспользования",
        destination=Destination(DestinationSection.REUSE, 'request'),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(OriginSection.POINT_ARGS, ext_http_in_tornado_request),
        ),
        stage=Stage.INIT,
    ),
    Rule(
        description="Поставить флаг пропуска трассировки, если HTTP путь"
                    "в списке игнорируемых",
        destination=Destination(DestinationSection.REUSE, 'should_not_trace'),
        pipeline=(
            pipe_check_skip,
        ),
        origins=(
            Origin(
                OriginSection.REUSE,
                lambda data: data['request']['url_path'],
            ),
            Origin(OriginSection.ADAPTER, None),
        ),
        stage=Stage.INIT,
    ),
    Rule(
        description="Разместить заголовки контекста трассера там, "
                    "где фабрика участков их ищет",
        destination=Destination(DestinationSection.REUSE, 'tracer_headers'),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(
                OriginSection.REUSE,
                lambda data: data['request']['zipkin_headers'],
            ),
        ),
        stage=Stage.INIT,
    ),
    Rule(
        description="Задать имя участку",
        destination=Destination(
            DestinationSection.SPAN_NAME,
            'name'
        ),
        pipeline=(
            partial(pipe_sep_string, **{'sep': ' '}),
        ),
        origins=(
            Origin(
                OriginSection.REUSE,
                lambda data: data['request']['method'],
            ),
            Origin(
                OriginSection.REUSE,
                lambda data: data['request']['url_path'],
            ),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Задать имя партнёрской точки для участка",
        destination=Destination(
            DestinationSection.SPAN_NAME,
            'remote_endpoint',
          ),
        pipeline=(
            partial(pipe_sep_string, **{'sep': '://'}),
        ),
        origins=(
            Origin(
                OriginSection.ENGINE,
                lambda engine: engine.schema_feed.variant.api_kind.name.lower(),
            ),
            Origin(
                OriginSection.REUSE,
                lambda data: data['request']['remote_ip'],
            ),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Вывести тело запроса в журнал участка "
                    "- получить первый элемент источников"
                    "- выцепить существенные значения для тегов в строки"
                    "- сериализовать"
                    "- обрезать"
                    "- маскировать"
                    "- закавычить/откавычить/экранировать/энкодить",
        destination=Destination(DestinationSection.SPAN_LOGS, 'request_body'),
        pipeline=(
            pipe_head,
            pipe_catch_essential,
            pipe_dump,
            pipe_cut,
            pipe_mask_secret,
        ),
        origins=(
            Origin(OriginSection.REUSE, lambda data: data['request']['body']),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Сохранить информацию об ответе",
        destination=Destination(DestinationSection.REUSE, 'response'),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(OriginSection.POINT_ARGS, 'self'),
        ),
        stage=Stage.POST,
    ),
    Rule(
        description="Вывести тело ответа на запрос",
        destination=Destination(DestinationSection.SPAN_LOGS, 'response_body'),
        pipeline=(
            pipe_head,
            lambda response: getattr(response, 'response_body', {}),
            pipe_catch_essential,
            pipe_dump,
            pipe_cut,
            pipe_mask_secret,
        ),
        origins=(
            Origin(OriginSection.REUSE, 'response'),
        ),
        stage=Stage.POST,
    ),
    Rule(
        description="Запомнить ошибку для вывода",
        destination=Destination(DestinationSection.REUSE, 'error'),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(OriginSection.SPAN, 'error'),
        ),
        stage=Stage.POST,
    ),
    Rule(
        description="Вывести в тэги адрес запроса",
        destination=Destination(DestinationSection.SPAN_TAGS, 'url'),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(OriginSection.REUSE, lambda data: data['request']['url']),
        ),
        stage=Stage.POST,
    ),
    Rule(
        description="Вывести в тэги размер запроса",
        destination=Destination(DestinationSection.SPAN_TAGS, 'http.req.size'),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(
                OriginSection.REUSE,
                lambda data: data['request']['length'],
            ),
        ),
        stage=Stage.POST,
    ),
    Rule(
        description="Вывести в тэги заголовки запроса",
        destination=Destination(
            DestinationSection.SPAN_TAGS,
            'http.req.headers',
        ),
        pipeline=(
            pipe_head,
            pipe_dump,
        ),
        origins=(
            Origin(
                OriginSection.REUSE,
                lambda data: data['request']['headers'],
            ),
        ),
        stage=Stage.POST,
    ),
    Rule(
        description="Вывести в тэги код статуса ответа",
        destination=Destination(DestinationSection.SPAN_TAGS,
                                'http.rsp.status'),
        pipeline=(
            pipe_head,
            lambda response: getattr(response, '_status_code', {}),
        ),
        origins=(
            Origin(OriginSection.REUSE, 'response'),
        ),
        stage=Stage.POST,
    ),
    Rule(
        description="Вывести в тэги размер ответа",
        destination=Destination(DestinationSection.SPAN_TAGS, 'http.rsp.size'),
        pipeline=(
            pipe_head,
            lambda response: len(json_dumps_with_dt(
                getattr(response, 'response_body', '')
            )),
        ),
        origins=(
            Origin(OriginSection.REUSE, 'response'),
        ),
        stage=Stage.POST,
    ),
    Rule(
        description="Вывести в тэги заголовки ответа",
        destination=Destination(
            DestinationSection.SPAN_TAGS,
            'http.rsp.headers',
        ),
        pipeline=(
            pipe_head,
            lambda response: getattr(response, '_headers', {}),
            lambda headers: dict(headers) if headers else None,
            pipe_dump,
        ),
        origins=(
            Origin(OriginSection.REUSE, 'response'),
        ),
        stage=Stage.POST,
    ),
)
