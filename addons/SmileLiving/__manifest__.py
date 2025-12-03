{
    'name': "SmileLiving",
    'version': '1.0',
    'depends': ['base', 'mail', 'web', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/house_property_views.xml',
        'views/invoice_property_views.xml',
        'views/property_type_views.xml',
        'views/smileliving_template_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
