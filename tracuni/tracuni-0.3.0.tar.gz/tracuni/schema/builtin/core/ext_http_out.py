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
    ext_out_headers,
    ext_tracer_out_point,
    ext_http_out_url,
    pipe_inject_headers,
    pipe_head,
    pipe_sep_string,
    pipe_service_name_from_config,
    pipe_catch_essential,
    pipe_mask_secret,
    pipe_dump,
    pipe_cut,
    ext_send_request_args, ext_api_kind)


ruleset = (
    Rule(
        description="Записать заголовки в запрос",
        destination=Destination(DestinationSection.POINT_ARGS, 'headers'),
        pipeline=(
            pipe_inject_headers,
        ),
        origins=(
            Origin(
                OriginSection.SPAN, None,
            ),
            Origin(
                OriginSection.POINT_ARGS, ext_out_headers,
            ),
            Origin(
                OriginSection.ADAPTER,
                lambda adapter: adapter.config.service_name,
            ),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Наименование партнерского сервиса сохранить для "
                    "переиспользования",
        destination=Destination(
            DestinationSection.REUSE,
            'peer_name',
          ),
        pipeline=(
            pipe_service_name_from_config,
        ),
        origins=(
            Origin(OriginSection.ADAPTER, 'url_service_map'),
            Origin(OriginSection.POINT_ARGS, ext_http_out_url),
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
            partial(pipe_sep_string, **{'sep': ("::", " (", ")")}),
        ),
        origins=(
            Origin(
                OriginSection.ENGINE,
                ext_api_kind,
            ),
            Origin(
                OriginSection.REUSE,
                "peer_name",
            ),
            Origin(
                OriginSection.CALL_STACK,
                ext_tracer_out_point,
            ),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Наименование партнерского сервиса записать в участок",
        destination=Destination(
            DestinationSection.SPAN_NAME,
            'remote_endpoint',
          ),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(OriginSection.REUSE, 'peer_name'),
        ),
        stage=Stage.PRE,
    ),
    Rule(
        description="Хост партнерского сервиса",
        destination=Destination(
            DestinationSection.SPAN_TAGS,
            'peer.url',
          ),
        pipeline=(
            pipe_head,
        ),
        origins=(
            Origin(OriginSection.POINT_ARGS, ext_http_out_url),
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
            Origin(
                OriginSection.POINT_ARGS,
                ext_send_request_args,
            ),
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
            Origin(
                OriginSection.POINT_RESULT, None
            ),
        ),
        stage=Stage.POST,
    ),
    Rule(
        description="Вывести тело ответа в аннотацию",
        destination=Destination(DestinationSection.SPAN_LOGS, 'response_body'),
        pipeline=(
            pipe_head,
            lambda v: v.get('response_body'),
        ),
        origins=(
            Origin(
                OriginSection.REUSE, "response"
            ),
        ),
        stage=Stage.POST,
    ),
    Rule(
        description="Вывести код ответа в аннотацию",
        destination=Destination(DestinationSection.SPAN_TAGS,
                                'http.rsp.status'),
        pipeline=(
            pipe_head,
            lambda v: v.get('response_code'),
        ),
        origins=(
            Origin(
                OriginSection.REUSE, "response"
            ),
        ),
        stage=Stage.POST,
    ),
    Rule(
        description="Вывести заголовки ответа в аннотацию",
        destination=Destination(DestinationSection.SPAN_TAGS,
                                'http.rsp.headers'),
        pipeline=(
            pipe_head,
            lambda v: v.get('response_headers'),
            pipe_dump,
        ),
        origins=(
            Origin(
                OriginSection.REUSE, "response"
            ),
        ),
        stage=Stage.POST,
    ),
    Rule(
        description="Вывести размер тела ответа в метки",
        destination=Destination(DestinationSection.SPAN_TAGS,
                                'http.rsp.size'),
        pipeline=(
            pipe_head,
            lambda v: len(v.get('response_body')),
        ),
        origins=(
            Origin(
                OriginSection.REUSE, "response"
            ),
        ),
        stage=Stage.POST,
    ),
    Rule(
        description="Вывести сертификат ответа в метки",
        destination=Destination(DestinationSection.SPAN_TAGS,
                                'http.req.cert'),
        pipeline=(
            pipe_head,
            lambda v: v.get('request_cert'),
        ),
        origins=(
            Origin(
                OriginSection.REUSE, "response"
            ),
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
)
