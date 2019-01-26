from cytoolz.curried import curry, dissoc

from gosdk import logger


@curry
def process_transcripts(record, sdk=None):
    record = dissoc(record, "__type__", "build")
    logger.get_logger().debug("get_transcripts", **record)

    results = sdk.call_with_retry(
        sdk.transcripts.get_transcripts, **dissoc(record, "gene")
    )["results"]

    return {**record, "transcripts": results}
