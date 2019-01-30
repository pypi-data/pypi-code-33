import json
import logging
import inspect
import itertools

logger = logging.getLogger(__name__)


def requires_spark(func):
    def func_wrapper(*args, **kwargs):
        try:
            import pyspark as PYSPARK

            # inject the pyspark module as a `kwarg`
            if (
                "PYSPARK" in inspect.getfullargspec(func).args
                or "PYSPARK" in inspect.getfullargspec(func).kwonlyargs
            ):
                kwargs["PYSPARK"] = PYSPARK

            return func(*args, **kwargs)
        except ImportError as e:
            logger.error(
                "In order to use this functionality, you need PySpark installed"
            )

    return func_wrapper


class udf:
    @staticmethod
    @requires_spark
    def signal(PYSPARK):
        """Returns a Spark UDF that converts a Dataframe column to a format ready for use with Primed
        
        ```
        signals = df\  
          .withColumn("signal", piospark.udf.signal()('signal_key'))\  
          .select("signal")
        ```
        """

        def fn(key):
            return json.dumps({"key": str(key)})

        return PYSPARK.sql.functions.udf(fn, PYSPARK.sql.types.StringType())

    @staticmethod
    @requires_spark
    def prediction(PYSPARK):
        def fn(signal_key, target_key, score):
            return json.dumps(
                {"sk": str(signal_key), "tk": str(target_key), "score": float(score)}
            )

        return PYSPARK.sql.functions.udf(fn, PYSPARK.sql.types.StringType())

    @staticmethod
    @requires_spark
    def target(*properties, PYSPARK):
        def fn(key, *values):
            if properties is not None and len(properties) > 0:
                return json.dumps(
                    {
                        "key": str(key),
                        "value": dict(
                            itertools.zip_longest(properties, values, fillvalue=None)
                        ),
                    }
                )
            else:
                return json.dumps({"key": str(key)})

        return PYSPARK.sql.functions.udf(fn, PYSPARK.sql.types.StringType())
