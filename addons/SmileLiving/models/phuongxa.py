# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PhuongXa(models.Model):
    _name = 'phuong.xa'
    _description = 'Phường/Xã'
    _order = 'name'
    
    name = fields.Char('Tên phường/xã', required=True)
    code = fields.Char('Mã phường/xã', size=15, required=True)
    quanhuyen_id = fields.Many2one('quan.huyen', string='Quận/Huyện', required=True, ondelete='cascade')
    active = fields.Boolean('Hoạt động', default=True)
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Mã phường/xã phải là duy nhất!'),
        ('name_quanhuyen_unique', 'unique(name, quanhuyen_id)', 'Tên phường/xã phải là duy nhất trong cùng quận/huyện!'),
    ]
