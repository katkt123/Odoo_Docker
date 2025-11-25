# estate_property.py
from odoo import models, fields, api

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Thông tin Bất Động Sản"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'website.published.mixin']

    # --- Cơ bản ---
    name = fields.Char("Tên BĐS", required=True)
    description = fields.Text("Mô tả")
    property_type_id = fields.Many2one("estate.property.type", string="Loại BĐS")
    tag_ids = fields.Many2many("estate.property.tag", string="Tiện ích")
    
    # --- Giá & Trạng thái ---
    expected_price = fields.Float("Giá mong muốn", required=True)
    selling_price = fields.Float("Giá bán chốt", readonly=True)
    currency_id = fields.Many2one('res.currency', string="Tiền tệ")
    state = fields.Selection([
        ('new', 'Mới'),
        ('offer_received', 'Có đề nghị'),
        ('offer_accepted', 'Đã nhận cọc'),
        ('sold', 'Đã bán'),
        ('canceled', 'Đã hủy'),
    ], default='new', tracking=True)

    # --- Quan hệ (Kết nối với các file khác) ---
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Danh sách Đề nghị")
    deposit_ids = fields.One2many("estate.property.deposit", "property_id", string="Danh sách Đặt cọc")
    invoice_ids = fields.One2many("estate.invoice", "property_id", string="Lịch sử Hóa đơn")

    # --- Người phụ trách ---
    salesperson_id = fields.Many2one('res.users', default=lambda self: self.env.user, string="Salesman")
    buyer_id = fields.Many2one('res.partner', string="Người mua", copy=False)