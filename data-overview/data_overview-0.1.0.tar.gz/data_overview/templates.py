from jinja2 import Environment, PackageLoader

"""该文件对html页面渲染进行设置
templates：要渲染的页面组成

"""
package_loader = PackageLoader('data_overview', 'templates')

# lstrip_blocks和trim_blocks用于去除模板中的空白项
env = Environment(lstrip_blocks=True, trim_blocks=True, loader=package_loader)

templates = {
    'wrapper': 'wrapper.html',
    'content': 'content.html',
    'data_overview': 'data_overview.html',
    'column_overview': 'column_overview.html',
    'var_num': 'var_numeric.html',
    'var_date': 'var_date.html',
    'var_category': 'var_categorical.html',
    'var_bool': 'var_bool.html',
    'var_constant': 'var_constant.html',
    'var_unique': 'var_unique.html',
    'var_unsupported': 'var_unsupported.html',
    'main_bar_diagram': 'main_bar_diagram.html',
    'main_bar_diagram_row': '_main_bar_diagram_row.html',
    'extra_bar_diagram': 'extra_bar_diagram.html',
    'extra_bar_diagram_row': '_extra_bar_diagram_row.html',
}


# 定义数据类型的展示内容
var_type = {'num': 'Numeric',
            'date': 'Date',
            'category': 'Categorical',
            'unique': 'Categorical, Unique',
            'bool': 'Boolean',
            'constant': 'Constant',
            'unsupported': 'Unsupported'
            }


# 数据类型对应的条形图显示的行数
main_bar_diagram_row_col = {'categorical': 6, 'bool': 3, 'numeric': 0}

# 统计图标展示的value行数：区分mini和扩展的详情展示区分
bar_diagram_value_num = {'mini': 3, 'extra': 10}


def template(name):
    """根据模板名获取对应的template"""

    globals = None
    if name.startswith('var_'):
        # This is a row template setting global variable
        globals = dict()
        globals['type'] = var_type[name.split('_')[1]]
    return env.get_template(templates[name], globals=globals)


# 数据类型和渲染的html页面对应关系
row_templates_dict = {'numeric': template('var_num'),
                      'date': template('var_date'),
                      'categorical': template('var_category'),
                      'bool': template('var_bool'),
                      'unique': template('var_unique'),
                      'constant': template('var_constant'),
                      'unsupported': template('var_unsupported')
                      }


