import sys
from operator import add

from pyspark.sql import SparkSession

# word count up some words
def word_count(input_file):
    spark = SparkSession\
        .builder\
        .appName("PythonSort")\
        .getOrCreate()

    lines = spark.read.text(input_file).rdd.map(lambda r: r[0])

    counts = lines.flatMap(lambda x: x.split(' ')) \
        .map(lambda x: (x, 1)) \
        .reduceByKey(add)
    
    output = counts.collect()

    spark.stop()

    return output


