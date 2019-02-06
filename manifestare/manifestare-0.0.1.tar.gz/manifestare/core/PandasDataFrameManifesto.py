from manifestare.core import DataFrameManifesto

class PandasDataFrameManifesto(DataFrameManifesto):

    def doesHaveColumn(self, column):
        assert column in self.df.columns