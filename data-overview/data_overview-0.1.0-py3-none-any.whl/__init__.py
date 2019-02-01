"""
数据概览工具封装
"""

import pandas as pd
import sys
import codecs
from data_overview import templates
from data_overview.formatter import format_percent, format_bytesize
from data_overview.plot import histogram
from data_overview.report import build_html

name = "data_overview"

# 公共变量定义
TYPE_BOOL = 'bool'  # 布尔类型 or (numeric and count distinct = 2）
TYPE_NUMERIC = 'numeric'  # 数值类型
TYPE_DATE = 'date'  # 日期类型

TYPE_CONSTANT = 'constant'  # count distinct = 1
TYPE_UNIQUE = 'unique'  # count distinct = count
TYPE_CATEGORICAL = 'categorical'  # 其他归为该类
TYPE_NULL = 'null'  # 全部为空值
TYPE_UNSUPPORTED = 'unsupported'  # 识别异常时
TYPE_LIST = [TYPE_BOOL, TYPE_NUMERIC, TYPE_DATE, TYPE_CONSTANT, TYPE_UNIQUE, TYPE_CATEGORICAL, TYPE_UNSUPPORTED]


class DataOverview(object):

    def __init__(self, df):
        """初始化方法"""
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input type need to be pandas.DataFrame！")

        self.df = df
        self.data_basic = self._get_data_basic()
        self.column_basic = self._get_column_basic()
        self.column_type = self._get_column_type()
        self.column_concat = pd.concat([self.column_basic, self.column_type], axis=1)
        self._build_html()

    def to_html(self, file_name):
        """将结果导出为html格式文档"""
        with codecs.open(file_name, 'w+b', encoding = 'utf8') as self.file:
            html = templates.template('wrapper').render(content=self.html)
            self.file.write(html)

    def _build_html(self):
        """构造html内容"""
        self._data_overview()
        self._merge_data()
        self.html = build_html(self.merged_data)
        return

    @property
    def column_types(self):
        """字段类型"""
        column_types = {k: 0 for k in TYPE_LIST}
        column_types.update(dict(self.column_type['type'].value_counts()))
        return column_types

    def _data_overview(self):
        """数据表概览：columns, rows, memory"""
        # 对memory的格式做处理
        self.data_basic['memory'] = format_bytesize(self.data_basic['memory'])
        self.data_basic_dict = pd.DataFrame.from_dict(self.data_basic,orient='index')[0]

    @property
    def data_overview(self):
        return self.data_basic_dict

    @property
    def column_describe(self):
        """数据字段描述，包括："""
        # 对unique_percentage的格式做处理
        self.column_concat['null_count_percentage_str'] = \
            self.column_concat['null_count_percentage'].map(format_percent)
        # df.transpose会将df字段类型改为object，若要保留原始类型，使用df.astype(object).tranpose
        df = self.column_concat.astype(object).transpose()
        index_dict = {'count': '总个数',
                      'unique': '去重后个数',
                      'null_count': '缺失个数',
                      'null_count_percentage_str': '缺失率(%)',
                      'type': '数据类型'}
        df = df.loc[list(index_dict.keys())] # 数据字段描述仅展示部分行
        df = df.rename(index=index_dict)
        return df

    def _get_data_basic(self):
        """数据表概览信息计算：columns, rows, memory"""
        columns = self.df.shape[1]
        rows = self.df.shape[0]
        memory = sys.getsizeof(self.df)  # byte为单位

        return {'columns': columns, 'rows': rows, 'memory': memory}

    def _get_column_basic(self):
        """基于pandas对data frame的基础统计：count, unique, null_count, null_count_percentage, type"""
        count = self.df.count()
        count.name = 'count'

        unique = self.df.nunique()
        unique.name = 'unique'

        unique_percentage = unique / self.data_basic['rows']
        unique_percentage.name = 'unique_percentage'  # 去重后个数占比

        mean = self.df.mean()
        mean.name = 'mean'

        null_count = self.data_basic['rows'] - count
        null_count.name = 'null_count'

        null_count_percentage = null_count / self.data_basic['rows']
        null_count_percentage.name = 'null_count_percentage'

        min = self.df.min()
        min.name = 'min'

        max = self.df.max()
        max.name = 'max'

        quantile_5 = self.df.quantile(0.05)
        quantile_5.name = 'quantile_5'

        quantile_25 = self.df.quantile(0.25)
        quantile_25.name = 'quantile_25'

        quantile_50 = self.df.quantile(0.50)
        quantile_50.name = 'quantile_50'

        quantile_75 = self.df.quantile(0.75)
        quantile_75.name = 'quantile_75'

        quantile_95 = self.df.quantile(0.95)
        quantile_95.name = 'quantile_95'

        # TODO sum只统计数值型
        sum = self.df.sum()
        sum.name = 'sum'

        zero = (self.df == 0).astype(int).sum()
        zero_count_percentage = zero / self.data_basic['rows']
        zero_count_percentage.name = 'zero_count_precentage'

        std = self.df.std()
        std.name = 'std'

        df = pd.concat([count,
                        unique,
                        unique_percentage,
                        mean,
                        null_count,
                        null_count_percentage,
                        min,
                        max,
                        zero_count_percentage,
                        quantile_5,
                        quantile_25,
                        quantile_50,
                        quantile_75,
                        quantile_95,
                        sum,
                        std], axis=1)

        df['count'] = df['count'].astype(int)
        df['unique'] = df['unique'].astype(int)
        df['null_count'] = df['null_count'].astype(int)

        return df

    def _get_column_type(self):
        """计算字段类型"""
        column_type = {}

        for column, series in self.df.iteritems():
            try:
                unique = self.column_basic['unique'].loc[column]

                if unique == 1:
                    var_type = TYPE_CONSTANT  # 常量
                elif unique == 1:
                    var_type = TYPE_NULL  # 空值
                elif pd.api.types.is_bool_dtype(series) or (unique == 2 and pd.api.types.is_numeric_dtype(series)):
                    var_type = TYPE_BOOL  # 布尔类型
                elif pd.api.types.is_numeric_dtype(series):
                    var_type = TYPE_NUMERIC  # 数值类型
                elif pd.api.types.is_datetime64_dtype(series):
                    var_type = TYPE_DATE  # 日期类型
                elif unique == self.column_basic['count'].loc[column]:
                    var_type = TYPE_UNIQUE  # 没有重复数据
                else:
                    var_type = TYPE_CATEGORICAL  # 类别型
            except Exception as e:
                print(str(e))
                var_type = TYPE_UNSUPPORTED

            column_type[column] = var_type

        column_type = pd.DataFrame.from_dict(column_type, orient='index')
        column_type = column_type.rename(columns={0: 'type'})
        return column_type

    def _merge_data(self):
        """合并所有数据，供html渲染使用"""
        # TODO
        # 构造column_concat，即字段概览的显示内容
        var_group_count = {k: self.df.groupby(k)[k].count() for k in self.df.columns}
        # data_overview_data = pd.concat([self.data_overview, self.column_types])

        # 对于日期和数值类型，准备直方图数据
        numeric_histogram_data = {}
        for column, series in self.df.iteritems():
            type = self.column_type.loc[column]['type']
            if type == TYPE_NUMERIC or type == TYPE_DATE:
                numeric_histogram_data[column] = histogram(series, type)

        self.merged_data = {"data_overview": self.data_overview,
                            "column_types": self.column_types,
                            "column_overview": self.column_describe,
                            "column_detail": self.column_concat,
                            "var_group_count": var_group_count,
                            "numeric_histogram_data": numeric_histogram_data}
        return


if __name__ == '__main__':
    df = pd.read_csv("./data/test_data.csv", encoding='gb18030')
    dfo = DataOverview(df)
    print(dfo.data_overview)
    dfo.to_html("./data/report.html")