class SparkDataFrameTestBuilder(object):

    def __init__(self, spark):
        values, columns = [[(0, 1), (1, 0)], ['x', 'y']]
        self.df = spark.createDataFrame(values, columns)

    def buildEmptyDataFrame(self):
        self.df.drop('x', 'y')
        return self.df

    def buildSimpleDataFrame(self):
        return self.df
