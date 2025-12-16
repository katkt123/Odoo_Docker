# -*- coding: utf-8 -*-
from odoo import models, fields, api

class QuanHuyen(models.Model):
    _name = 'quan.huyen'
    _description = 'Quận/Huyện'
    _order = 'name'
    
    name = fields.Char('Tên quận/huyện', required=True)
    code = fields.Char('Mã quận/huyện', size=10, required=True)
    tinhthanh_id = fields.Many2one('tinh.thanh', string='Tỉnh/Thành', required=True, ondelete='cascade')
    active = fields.Boolean('Hoạt động', default=True)
    
    # Quan hệ với phường/xã
    phuongxa_ids = fields.One2many('phuong.xa', 'quanhuyen_id', string='Phường/Xã')
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Mã quận/huyện phải là duy nhất!'),
        ('name_tinhthanh_unique', 'unique(name, tinhthanh_id)', 'Tên quận/huyện phải là duy nhất trong cùng tỉnh/thành!'),
    ]
