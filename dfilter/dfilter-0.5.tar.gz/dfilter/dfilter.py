# coding: utf-8 -*-
import pandas as pd
import numpy as np
import scipy.stats
from prettytable import PrettyTable
import math
from math import sqrt

SMALL_NUMBER = 0.000001

def asymmetricKL(P,Q):
    return sum(P * math.log(P / Q))

def error_output(message):
    print '#####################################################'
    print '# ' + str(message)
    print '#####################################################'
    return False

def message_output(message_name,describe):
    print '*****************************************************'
    print '* ' + str(message_name)
    print '*****************************************************'
    if describe:
        print '* ' + str(describe)
    print '*****************************************************\n\n'

def get_mean(list):
    return sum(list) / float(len(list))

def get_var(nlist):
    N = len(nlist)
    sum1 = 0.0
    sum2 = 0.0
    for i in range(N):
        sum1 += nlist[i]
        sum2 += nlist[i] ** 2
    mean = sum1 / N
    var = sum2 / N - mean ** 2
    if var == 0:
        return SMALL_NUMBER
    return var

def default_header(lists):
    head_str = ''
    for index in range(len(lists[0])):
        head_str += 'list' + str(index) + ' '
    return head_str

def print_out_as_table(lists,header,table_name,describe=False):
    if header == False:
        header = default_header(lists)
    header_list = header.split()
    pt = PrettyTable()
    pt._set_field_names(header_list)
    for train in lists:
        pt.add_row(train)
    print '*****************************************************'
    print '* ' + str(table_name)
    print '*****************************************************'
    if describe:
        print '* ' + str(describe)
    print(pt)
    print '*****************************************************\n\n'


def get_colume_name_as_list(dataframe):
    print_out_as_table([dataframe.columns.values.tolist()],False,'输入内容的列名称')

def get_coverage(dataframe,colume_name):
    if colume_name not in dataframe.columns.values.tolist():
        return error_output('colume_name 参数错误：咩有这个参数')
    counter = 0
    none_counter = 0
    item_dict = {}
    print_list = []
    for item in dataframe[colume_name]:
        if item == None or (isinstance(item,float) and math.isnan(item)):
            none_counter += 1
        else:
            counter += 1
            if item in item_dict.keys():
                item_dict[item] += 1
            else:
                item_dict[item] = 1
    for key,val in item_dict.items():
        rate = round(val*100/float(counter),2)
        print_list.append((key,val,str(rate)))

    print_out_as_table(sorted(print_list,key=lambda student: student[2],reverse=True), '元素名称  个数  覆盖率%', '输入列中元素的覆盖率| 列名称：' + colume_name,describe='总行数：' + str(none_counter + counter) + ' 数据缺失：' +str(none_counter) + ' 缺失率：' + str(round(100* none_counter/float(none_counter + counter),2))+ '%')


def multipl(a, b):
    sumofab = 0.0
    for i in range(len(a)):
        temp = a[i] * b[i]
        sumofab += temp
    return sumofab

def get_pearson_similarity(dataframe,colume_name_1,colume_name_2,mean_fill = True):
    if colume_name_1 not in dataframe.columns.values.tolist():
        return error_output('colume_name_1 参数错误：咩有这个参数')
    if colume_name_2 not in dataframe.columns.values.tolist():
        return error_output('colume_name_2 参数错误：咩有这个参数')
    tmp_x = dataframe[colume_name_1].tolist()
    tmp_y = dataframe[colume_name_2].tolist()
    x = []
    y = []
    mean1 = 0
    mean2 = 0
    if mean_fill:
        mean1 = dataframe[colume_name_1].mean()
        mean2 = dataframe[colume_name_2].mean()
    for item in tmp_x:
        if math.isnan(item):
            x.append(mean1)
        else:
            x.append(item)
    for item in tmp_y:
        if math.isnan(item):
            y.append(mean2)
        else:
            y.append(item)
    if not len(x) == len(y):
        return error_output('数据错误：数据长度不同')
    n = len(x)
    sum1 = sum(x)
    sum2 = sum(y)
    sumofxy = multipl(x, y)
    sumofx2 = sum([pow(i, 2) for i in x])
    sumofy2 = sum([pow(j, 2) for j in y])
    num = sumofxy - (float(sum1) * float(sum2) / n)
    den = sqrt((sumofx2 - float(sum1 ** 2) / n) * (sumofy2 - float(sum2 ** 2) / n))
    pearson_simi = num / den

    title = '[零]填充'
    if mean_fill:
        title = '[均值]填充'

    message_output('皮尔逊相关系数 | '+title,'列1：' + colume_name_1 +' 列2：' + colume_name_2 + ' 的皮尔逊相关系数为：' + str(pearson_simi))

def get_fisher_score(dataframe,colume_name,y,mean_fill = True):
    if colume_name not in dataframe.columns.values.tolist():
        return error_output('colume_name 参数错误：咩有这个参数')
    tmp_x = dataframe[colume_name].tolist()
    mean1 = 0
    x= []
    if mean_fill:
        mean1 = dataframe[colume_name].mean()
    for item in tmp_x:
        if math.isnan(item):
            x.append(mean1)
        else:
            x.append(item)
    n = len(x)
    if not len(x) == len(y):
        return error_output('数据错误：数据长度不同')

    labels = set(y)
    lab_dic = dict()
    for label in labels:
        lab_dic[label] = []
    for index in range(len(x)):
        lab_dic[y[index]].append(x[index])
    up_val = 0
    down_val = 0
    x_mean = get_mean(x)
    for label in labels:
        up_val += len(lab_dic[label])*((get_mean(lab_dic[label])-x_mean) ** 2)
        down_val += len(lab_dic[label])*(get_var(lab_dic[label]) ** 2)
    Si = up_val/down_val
    title = '[零]填充'
    if mean_fill:
        title = '[均值]填充'
    message_output('Fisher得分 | ' + title, '列：' + colume_name  + ' 的Fisher得分为：' + str(Si))
    return Si

def get_fisher_score_with_list(dataframe,columes,y,mean_fill = True):
    title = ''
    val = []
    for colume in columes:
        title += str(colume) + ' '
        val.append(str(get_fisher_score(dataframe,colume,y,mean_fill)))
    title_fill = '[零]填充'
    if mean_fill:
        title_fill = '[均值]填充'
    print_out_as_table([val], title ,'输入列中元素的Fisher得分|' + title_fill)

def get_K_L_divergence(dataframe,colume_name_1,colume_name_2):
    mean_fill = True
    if colume_name_1 not in dataframe.columns.values.tolist():
        return error_output('colume_name_1 参数错误：咩有这个参数')
    if colume_name_2 not in dataframe.columns.values.tolist():
        return error_output('colume_name_2 参数错误：咩有这个参数')
    tmp_x = dataframe[colume_name_1].tolist()
    tmp_y = dataframe[colume_name_2].tolist()
    x = []
    y = []
    mean1 = 0
    mean2 = 0
    if mean_fill:
        mean1 = dataframe[colume_name_1].mean()
        mean2 = dataframe[colume_name_2].mean()
    for item in tmp_x:
        if math.isnan(item):
            x.append(mean1)
        else:
            if item == 0:
                x.append(SMALL_NUMBER)
            else:
                x.append(item)
    for item in tmp_y:
        if math.isnan(item):
            y.append(mean2)
        else:
            if item == 0:
                y.append(SMALL_NUMBER)
            else:
                y.append(item)
    if not len(x) == len(y):
        return error_output('数据错误：数据长度不同')
    KL = 0.0
    for i in range(10):
        KL += x[i] * np.log(x[i] / y[i])
    return KL

def get_K_L_divergence_as_list(dataframe,columes):
    title = '- '
    val = []
    val1 = []
    for colume in columes:
        title += str(colume) + ' '
        val1.append(colume)
        for colume1 in columes:
            val1.append(str(get_K_L_divergence(dataframe, str(colume), str(colume1))))
        val.append(val1)
        val1=[]
    title_fill = '[均值]填充'
    print_out_as_table(val, title, '输入列中元素的KL散度|' + title_fill)

def get_K_L_divergence_as_list_with_y(dataframe,columes,y):
    title = '- '
    val = []
    val.append('y')
    for colume_name_1 in columes:
        title += str(colume_name_1) + ' '

        mean_fill = True
        if colume_name_1 not in dataframe.columns.values.tolist():
            return error_output('colume_name_1 参数错误：咩有这个参数')
        tmp_x = dataframe[colume_name_1].tolist()
        tmp_y = y
        x = []
        y = []
        mean1 = 0
        if mean_fill:
            mean1 = dataframe[colume_name_1].mean()
            mean2 = sum(tmp_y)/len(tmp_y)
        for item in tmp_x:
            if math.isnan(item):
                x.append(mean1)
            else:
                if item == 0:
                    x.append(SMALL_NUMBER)
                else:
                    x.append(item)
        for item in tmp_y:
            if math.isnan(item):
                y.append(mean2)
            else:
                if item == 0:
                    y.append(SMALL_NUMBER)
                else:
                    y.append(item)
        if not len(x) == len(y):
            return error_output('数据错误：数据长度不同')
        KL = 0.0
        for i in range(10):
            KL += x[i] * np.log(x[i] / y[i])
        val.append(str(KL))
    title_fill = '[均值]填充'
    print_out_as_table([val], title, '输入列中元素的KL散度|' + title_fill)

def check_normal_cluster(dataframe,colume_name,mean_fill=True):
    x = []
    tmp_x = dataframe[colume_name].tolist()
    mean1 = 0
    if mean_fill:
        mean1 = dataframe[colume_name].mean()
    for item in tmp_x:
        if math.isnan(item):
            x.append(mean1)
        else:
            x.append(item)
    out_put_list = []
    KS_check = scipy.stats.kstest(x, 'norm')
    message_output('K-S 检验 | 正态性检验' ,
                   '特点是比较严格，基于的原理是CDF，理论上可以检验任何分布。\n* ' + str(KS_check))
    out_put_list.append(['K-S 检验',KS_check[0],KS_check[1]])
    Shapiro_check = scipy.stats.shapiro(x)
    message_output('Shapiro 检验 | 正态性检验',
                   '专门用来检验正态分布。\n* ' + str(Shapiro_check))
    out_put_list.append(['Shapiro 检验', Shapiro_check[0], Shapiro_check[1]])

    Normal_check = scipy.stats.normaltest(x)
    message_output('Normal 检验 | 正态性检验',
                   '原理是基于数据的skewness和kurtosis。\n* ' + str(Normal_check))
    out_put_list.append(['Normal 检验', Normal_check[0], Normal_check[1]])

    Anderson_check = scipy.stats.anderson(x, dist='norm')
    message_output('Anderson 检验 | 正态性检验',
                   '是ks检验的正态检验加强版。\n* ' + str(Anderson_check))
    out_put_list.append(['Anderson 检验', Anderson_check[0], Normal_check[1]])

    title_fill = '[零]填充'
    if mean_fill:
        title_fill = '[均值]填充'

    print_out_as_table(out_put_list, '检验方法 统计量 P-value ', '输入列中元素的 正态检验|' + title_fill)

def basic_info(dataframe,colume_name):
    basic_infor = dataframe[colume_name].describe()
    output_list = []
    output_list.append(['总数',basic_infor['count']])
    output_list.append(['均值',basic_infor['mean']])
    output_list.append(['标准差',basic_infor['std']])
    output_list.append(['最大值',basic_infor['max']])
    output_list.append(['最小值',basic_infor['min']])
    output_list.append(['25%分为数',basic_infor['25%']])
    output_list.append(['50%分为数',basic_infor['50%']])
    output_list.append(['75%分为数',basic_infor['75%']])
    print_out_as_table(output_list, '统计量 数据', '输入列中元素的基本信息')


# 方差齐性检验
def get_homogeneity_of_variance(dataframe,colume_name_1,colume_name_2,mean_fill=True):
    if colume_name_1 not in dataframe.columns.values.tolist():
        return error_output('colume_name_1 参数错误：咩有这个参数')
    if colume_name_2 not in dataframe.columns.values.tolist():
        return error_output('colume_name_2 参数错误：咩有这个参数')
    tmp_x = dataframe[colume_name_1].tolist()
    tmp_y = dataframe[colume_name_2].tolist()
    x = []
    y = []
    mean1 = 0
    mean2 = 0
    if mean_fill:
        mean1 = dataframe[colume_name_1].mean()
        mean2 = dataframe[colume_name_2].mean()
    for item in tmp_x:
        if math.isnan(item):
            x.append(mean1)
        else:
            x.append(item)
    for item in tmp_y:
        if math.isnan(item):
            y.append(mean2)
        else:
            y.append(item)
    if not len(x) == len(y):
        return error_output('数据错误：数据长度不同')
    out_put_list = []
    Bartlett_test = scipy.stats.bartlett(x, y)
    message_output('Bartlett 检验 | 检验方差是否齐',
                   '对数据有正态性要求!!!\n* ' + str(Bartlett_test))
    out_put_list.append(['Bartlett 检验', Bartlett_test[0], Bartlett_test[1]])

    Levene_test = scipy.stats.levene(x, y, center='trimmed')
    message_output('Levene 检验 | 检验方差是否齐',
                   '在数据非正态的情况下，精度比Bartlett检验好，可调中间值的度量\n* ' + str(Levene_test))
    out_put_list.append(['Levene 检验', Levene_test[0], Levene_test[1]])
    Fligner_killeen_test = scipy.stats.fligner(x, y, center='mean')
    message_output('Fligner-Killeen 检验 | 检验方差是否齐',
                   '非参检验，不依赖于分布 \n* ' + str(Fligner_killeen_test))
    out_put_list.append(['Fligner-Killeen 检验', Fligner_killeen_test[0], Fligner_killeen_test[1]])

    title_fill = '[零]填充'
    if mean_fill:
        title_fill = '[均值]填充'

    print_out_as_table(out_put_list, '检验方法 统计量F P-value ', '输入列中元素的 方差齐性检验|' + title_fill,'LXK的结论：齐性检验时F越小（p越大），就证明没有差异，就说明齐，比如F=1.27，p>0.05则齐，这与方差分析均数时F越大约好相反\n* LXK注：方差(MS或s2)=离均差平方和/自由度（即离均差平方和的均数）\n* 标准差=方差的平方根（s) \n* F=MS组间/MS误差=（处理因素的影响+个体差异带来的误差）/个体差异带来的误差')

# 两组数之间的比较
def compare_between_two_couples(dataframe,colume_name_1,colume_name_2,mean_fill=True):
    if colume_name_1 not in dataframe.columns.values.tolist():
        return error_output('colume_name_1 参数错误：咩有这个参数')
    if colume_name_2 not in dataframe.columns.values.tolist():
        return error_output('colume_name_2 参数错误：咩有这个参数')
    tmp_x = dataframe[colume_name_1].tolist()
    tmp_y = dataframe[colume_name_2].tolist()
    x = []
    y = []
    mean1 = 0
    mean2 = 0
    if mean_fill:
        mean1 = dataframe[colume_name_1].mean()
        mean2 = dataframe[colume_name_2].mean()
    for item in tmp_x:
        if math.isnan(item):
            x.append(mean1)
        else:
            x.append(item)
    for item in tmp_y:
        if math.isnan(item):
            y.append(mean2)
        else:
            y.append(item)
    if not len(x) == len(y):
        return error_output('数据错误：数据长度不同')
    out_put_list = []
    PDF_t = scipy.stats.ttest_ind(x, y, equal_var=True, nan_policy='omit')
    message_output('独立两样本t 检验 | 参数方法',
                   '适用于 完全随机设计 的两样本均数的比较,其目的是检验两样本所来自总体的均数是否相等(总体服从正态分布)\n* ' + str(PDF_t))
    out_put_list.append(['独立两样本t 检验', PDF_t[0], PDF_t[1]])

    PDF_pare_t = scipy.stats.ttest_rel(x, y, nan_policy='omit')
    message_output('成对两样本t 检验 | 参数方法',
                   '适用于 完全随机设计 的两样本均数的比较,其目的是检验两样本所来自总体的均数是否相等(总体服从正态分布)\n* ' + str(PDF_pare_t))
    out_put_list.append(['成对两样本t 检验', PDF_pare_t[0], PDF_pare_t[1]])

    mean1 = dataframe[colume_name_1].mean()
    mean2 = dataframe[colume_name_2].mean()
    std1 = dataframe[colume_name_1].std()
    std2 = dataframe[colume_name_2].std()
    nobs1 = len(x) / 10
    nobs2 = len(y) / 10

    ttest_ind_from_stats = scipy.stats.ttest_ind_from_stats(mean1,std1,nobs1,mean2,std2,nobs2, equal_var=False)
    message_output('通过基本统计量来做独立两样本 检验 | 参数方法',
                   '\n* ' + str(ttest_ind_from_stats))
    out_put_list.append(['基本统计量-独立两样本 检验', ttest_ind_from_stats[0], ttest_ind_from_stats[1]])

    ranksums = scipy.stats.ranksums(x, y)
    message_output('wilcox秩序和 检验 | 非参数方法',
                   'wilcox秩序和检验，n < 20时独立样本效果比较好\n* ' + str(ranksums))
    out_put_list.append(['wilcox秩序和 检验', ranksums[0], ranksums[1]])

    mannwhitneyu = scipy.stats.mannwhitneyu(x, y)
    message_output('Mann-Whitney U 检验 | 非参数方法',
                   'U检验, n > 20时独立样本，比wilcox秩序和检验更稳健\n* ' + str(mannwhitneyu))
    out_put_list.append(['Mann-Whitney U 检验', mannwhitneyu[0], mannwhitneyu[1]])

    title_fill = '[零]填充'
    if mean_fill:
        title_fill = '[均值]填充'

    print_out_as_table(out_put_list, '检验方法 统计量 P-value ', '输入列中元素的 两组数之间的比较|' + title_fill)