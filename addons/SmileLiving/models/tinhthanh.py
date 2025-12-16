# -*- coding: utf-8 -*-
from odoo import models, fields, api

class TinhThanh(models.Model):
    _name = 'tinh.thanh'
    _description = 'Tỉnh/Thành phố'
    _order = 'name'
    
    name = fields.Char('Tên tỉnh/thành', required=True)
    code = fields.Char('Mã tỉnh/thành', size=5, required=True)
    active = fields.Boolean('Hoạt động', default=True)
    
    # Quan hệ với quận/huyện
    quanhuyen_ids = fields.One2many('quan.huyen', 'tinhthanh_id', string='Quận/Huyện')
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Mã tỉnh/thành phải là duy nhất!'),
        ('name_unique', 'unique(name)', 'Tên tỉnh/thành phải là duy nhất!'),
    ]
