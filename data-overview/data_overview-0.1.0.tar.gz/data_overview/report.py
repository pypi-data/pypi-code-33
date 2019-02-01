""" 该类用于构造html页面"""
from data_overview import templates
import data_overview as dfo
from data_overview.formatter import format_value, format_percent


def _format_row(freq, label, max_freq, row_template, n, extra_class=''):
    if max_freq != 0:
        width = int(freq / max_freq * 99) + 1
    else:
        width = 1

    if width > 20:
        label_in_bar = freq
        label_after_bar = ""
    else:
        label_in_bar = "&nbsp;"
        label_after_bar = freq

    return row_template.render(label=label,
                               width=width,
                               count=freq,
                               percentage='{:2.1f}'.format(freq / n * 100),
                               extra_class=extra_class,
                               label_in_bar=label_in_bar,
                               label_after_bar=label_after_bar)


def build_bar_chart(var_detail, chart_type, var_group_count_series, table_template, row_template):
    """
    对单个字段的分布情况构造条形图
    :param var_detail: 该字段的统计详情
    :param chart_type: 图表类型，区分在主页面还是扩展页面的展示项
    :param var_group_count_series: 字段的值分布
    :param table_template: 构造的chart，渲染为html的table
    :param row_template: chart中的行，渲染为html table的row
    :return:
    """
    var_group_count_series = var_group_count_series.sort_values(ascending=False)
    var_name = var_group_count_series.name
    rows_html = u''
    value_print_num = templates.bar_diagram_value_num[chart_type]
    table_row_num = templates.main_bar_diagram_row_col[var_detail['type']]
    value_others = 0
    value_print_min = 0

    num = var_detail['count']
    if value_print_num < len(var_group_count_series):
        value_others = sum(var_group_count_series.iloc[value_print_num:])
        value_print_min = var_group_count_series.values[value_print_num]

    value_missing = var_detail['null_count']
    max_freq = max(var_group_count_series.values[0], value_others, value_missing)

    # TODO: Correctly sort missing and other

    for label, count in var_group_count_series.iloc[0:value_print_num].iteritems():
        rows_html += _format_row(count, label, max_freq, row_template, num)

    if value_others > value_print_min:
        rows_html += _format_row(value_others,
                                 "Other values (%s)" % (var_group_count_series.count() - value_print_num),
                                 max_freq, row_template,
                                 num,
                                 extra_class='other')

    if value_missing > value_print_min:
        rows_html += _format_row(value_missing,
                                 "(Missing)",
                                 max_freq,
                                 row_template,
                                 num,
                                 extra_class='missing')

    return table_template.render(rows=rows_html, varid=hash(var_name), nb_col=table_row_num)


def build_extreme_table(var_group_count_series, table_template, row_template, num, ascending = True):
    """
    构造统计极值（极大值，极小值）的数据
    :param var_group_count_series: 数据
    :param table_template: html table
    :param row_template: html table row
    :param num:
    :param ascending: 排序方式
    :return:
    """
    number_to_print = 5
    # If it's mixed between base types (str, int) convert to str. Pure "mixed" types are filtered during type discovery
    if "mixed" in var_group_count_series.index.inferred_type:
        var_group_count_series.index = var_group_count_series.index.astype(str)

    sorted_series = var_group_count_series.sort_index()

    if ascending:
        obs_to_print = sorted_series.iloc[:number_to_print]
    else:
        obs_to_print = sorted_series.iloc[-number_to_print:]

    rows_html = ''
    max_freq = max(obs_to_print.values)

    for label, count in obs_to_print.iteritems():
        rows_html += _format_row(count, label, max_freq, row_template, num)

    return table_template.render(rows=rows_html)


def build_html(merged_data):
    """ 根据data和template组合html页面内容
    :param merged_data: 组合后的数据，用于向构造的html页面传参
    :return: str
        HTML 格式的文档内容
    """
    # TODO

    # 1. 数据表概览
    data_overview_html = templates.template('data_overview').render(values=merged_data['data_overview'],
                                                                    types=merged_data['column_types'])

    # 2. 数据字段描述
    # column_overview
    column_overview_html = templates.template('column_overview').render(\
        column_overview_html=merged_data['column_overview'].to_html(classes='sample'))

    # 3. 字段数据分布
    # column_detail
    # 对字段进行遍历，一一展示。or 按照类型展示，两种方式

    # Variables
    column_detail_html = u""

    # 按照字段的类型顺序展示
    column_detail = merged_data['column_detail'].sort_values(by='type')

    # 遍历字段，一一展示详情
    # TODO 类型和展示的数据项需要review清晰和完毕
    for index, row in column_detail.iterrows():
        values = {}
        # 遍历该字段的信息（如count，unique等），首先进行格式化
        # detail #1 ：字段类型和基本信息
        for key, value in row.iteritems():
            values[key] = format_value(key, value)
        values['var_name'] = index
        values['var_id'] = hash(index)
        row_classes = {}
        for col in set(row.index):
            row_classes[col] = row[col]

        # detail #2 : 字段可视化
        # 1. 对于category和bool类型，绘制Top5条形图
        if values['type'] in {'categorical', 'bool'}:
            values['minifreqtable'] = build_bar_chart(row,
                                                      'mini',
                                                      merged_data['var_group_count'][index],
                                                      templates.template('main_bar_diagram'),
                                                      templates.template('main_bar_diagram_row'))

        # 2. 对于constant类型，提示忽略分析
        # 3. 对于numeric和date类型，绘制直方图
        # 4. 对于unique类型，不绘制图
        # 5. unsupported类型，不做处理

        # detail #3 : 下拉扩展信息展示
        if values['type'] in {dfo.TYPE_CATEGORICAL, dfo.TYPE_BOOL, dfo.TYPE_NUMERIC}: # 对于这三种数据类型绘制条形图
            values['freqtable'] = build_bar_chart(row,
                                                  'extra',
                                                  merged_data['var_group_count'][index],
                                                  templates.template('extra_bar_diagram'),
                                                  templates.template('extra_bar_diagram_row'))
        if values['type'] in {dfo.TYPE_NUMERIC, dfo.TYPE_DATE}: # 对于数值型数据绘制直方图
            values['histogram'] = merged_data['numeric_histogram_data'][index]

        if values['type'] in {dfo.TYPE_NUMERIC, dfo.TYPE_UNIQUE}:  # 对于这两种数据类型绘制极值表
            values['firstn_expanded'] = build_extreme_table(merged_data['var_group_count'][index],
                                                            templates.template('extra_bar_diagram'),
                                                            templates.template('extra_bar_diagram_row'),
                                                            row['count'],
                                                            ascending=True)
            values['lastn_expanded'] = build_extreme_table(merged_data['var_group_count'][index],
                                                           templates.template('extra_bar_diagram'),
                                                           templates.template('extra_bar_diagram_row'),
                                                           row['count'],
                                                           ascending=False)

        column_detail_html += templates.row_templates_dict[row['type']].render(values=values,
                                                                               row_classes=row_classes)

    html = templates.template('content').render(dict(data_overview_html=data_overview_html,
                                                     column_overview_html=column_overview_html,
                                                     column_detail_html=column_detail_html))
    return html

