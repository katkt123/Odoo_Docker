{
    'name': "Odoo Real Estate Module (Estate)",
    'version': '1.0',
    'summary': 'Quản lý bất động sản, đặt cọc và thanh toán.',
    'description': "Module tùy chỉnh cho nghiệp vụ bất động sản.",
    'category': 'Sales/Real Estate',
    'author': "Siêu Nhân Odoo",
    'license': 'LGPL-3',
    
    # Khai báo các module phụ thuộc TỐI THIỂU
    'depends': ['base'], 

    # Khai báo các file dữ liệu sẽ được load
    'data': [
        # Ta sẽ load một file Security/View rỗng để module có file dữ liệu để Odoo đọc
        'security/ir.model.access.csv',
        'views/estate_menu.xml', # Tạo file này chỉ để tạo Menu Root cho module
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}