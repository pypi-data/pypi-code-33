# -*- coding: utf-8 -*-
{
    'name': "odoo-la-borda",

    'summary': """
        Odoo customizations for La Borda.""",

    'description': """
        For now basically UI stuff.
    """,

    'author': "Coopdevs",
    'website': "http://coopdevs.org",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
