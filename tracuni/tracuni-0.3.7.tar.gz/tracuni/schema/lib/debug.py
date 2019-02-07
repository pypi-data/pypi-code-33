import json


def debug_output(point_context, debug_info):
    point_name = point_context.point_ref.__qualname__
    adapter_config = json.dumps(point_context.adapter.config._asdict(), indent=2)
    variant = point_context.engine.schema_feed.variant
    schema = json.dumps(dict(
        (k.name, "{}::{}".format(rule.destination.section.name, rule.destination.name))
        for k, v in point_context.engine.extractors.items()
        for rule in v
    ))
    print(f"{point_name}\n{debug_info}")
    raise RuntimeError("Test debug error")
    # ("span", Optional['SpanGeneral']),
    # ("point_args", Optional[Dict[str, Any]]),
    # ("point_result", Optional[Any]),
    # ("client", Optional[Any]),
    # ("call_stack", Optional[Sequence]),
    # ("reuse", Optional[Dict[str, Any]]),
    # ("headers", Optional[Dict[str, Any]]),
    # ("span_tags", Optional[Dict[str, str]]),
    # ("span_logs", Optional[Sequence[str]]),
    # ("span_name", Optional[Dict[str, str]]),
