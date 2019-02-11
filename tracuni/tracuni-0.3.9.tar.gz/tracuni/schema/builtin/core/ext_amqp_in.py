import json
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
    ext_tracer_out_point,
    pipe_head,
    pipe_sep_string,
    pipe_catch_essential,
    pipe_mask_secret,
    pipe_dump,
    pipe_cut,
    ext_api_kind,
)


ruleset = (
    Rule(
        description="Сохранить тело сообщения",
        destination=Destination(DestinationSection.REUSE, 'message'),
        pipeline=(
            pipe_head,
            lambda data: json.loads(data.decode()),
        ),
        origins=(
            Origin(
                OriginSection.POINT_ARGS, "body",
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
            pipe_head,
            lambda v: v.exchange_name,
        ),
        origins=(
            Origin(OriginSection.POINT_ARGS, 'envelope'),
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
                partial(ext_tracer_out_point, **{"shift": 0}),
            ),
        ),
        stage=Stage.INIT,
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
        description="Вывести тело сообщения в аннотации",
        destination=Destination(DestinationSection.SPAN_LOGS, 'message'),
        pipeline=(
            pipe_head,
            pipe_catch_essential,
            pipe_dump,
            pipe_cut,
            pipe_mask_secret,
        ),
        origins=(
            Origin(
                OriginSection.REUSE, "message",
            ),
        ),
        stage=Stage.PRE,
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
