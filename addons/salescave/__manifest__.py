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
    'depends': ['base', 'base_optional_quick_create', 'web_domain_field'],
    
    'application': True,
    'installable': True,

    # always loaded
    'data': [
        # security
        'security/salescave_groups.xml',
        'security/ir.model.access.csv',
        # vistas modelos
        'views/salescave_product_purchase_views.xml',
        'views/salescave_sale_payment_views.xml',
        'views/salescave_sale_product_views.xml',
        'views/salescave_sale_views.xml',
        'views/salescave_lot_views.xml',
        'views/salescave_general_retirement_views.xml',
        'views/salescave_product_views.xml',
        'views/res_partner_views.xml',
        # reports
        'reports/salescave_profit_report_views.xml',
        'reports/salescave_debt_report_views.xml',
        'reports/salescave_real_money_report_views.xml',
        'reports/salescave_general_balance_report_views.xml',
        # menu
        'views/salescave_menu.xml',
    ],
}
