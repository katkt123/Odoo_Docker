{
    'name': "Odoo Real Estate Module (Estate)",
    'version': '1.0',
    'summary': 'Quản lý bất động sản, đặt cọc và thanh toán.',
    'description': "Module tùy chỉnh cho nghiệp vụ bất động sản.",
    'category': 'Sales/Real Estate',
    'author': "Siêu Nhân Odoo",
    'license': 'LGPL-3',
    'depends': ['base'], 
    'data': [
        'views/estate_menu.xml', 
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}