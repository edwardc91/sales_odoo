# -*- coding: utf-8 -*-
{
    'name': "Sales Cave",

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
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],
    
    'application': True,
    'installable': True,

    # always loaded
    'data': [
        'security/salescave_groups.xml',
        'security/ir.model.access.csv',
        'views/salescave_product_purchase_views.xml',
        'views/salescave_lot_views.xml',
        'views/salescave_product_views.xml',
        'views/res_partner_views.xml',
        'views/salescave_menu.xml',
    ],
}
