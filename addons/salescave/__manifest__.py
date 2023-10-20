# -*- coding: utf-8 -*-
{
    'name': "salescave",

    'summary': """
        Purchase and sales managment of products""",

    'description': """
        Purchase and sales managment of products
    """,

    'author': "Eduardo Miguel Hernández",
    'website': "https://edwardc91.github.io/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
}
