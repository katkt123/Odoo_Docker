{
    'name': "SmileLiving",
    'version': '1.0',
    'depends': ['base', 'mail', 'web', 'website', 'website_sale', 'crm'],
    'assets': {
        'web.assets_frontend': [
            'smileliving/static/src/js/wishlist_interest.js',
        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/house_property_views.xml',
        'views/invoice_property_views.xml',
        'views/property_type_views.xml',
        'views/website_sale_interest_inherit.xml',
        'views/smileliving_template_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
