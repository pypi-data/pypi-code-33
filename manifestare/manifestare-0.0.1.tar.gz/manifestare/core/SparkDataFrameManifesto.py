from manifestare.core import DataFrameManifesto

class SparkDataFrameManifesto(DataFrameManifesto):

    def doesHaveColumn(self, column):
        assert column in self.df.columns