{
    'name': "Estate",
    'version': '1.0',
    'depends': ['base', 'mail', 'website', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/estate_menu.xml',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_property_deposit_views.xml',
        'views/estate_invoice_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}