# estate_property_offer.py
from odoo import models, fields, api
from datetime import timedelta

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Đề nghị giá (Bidding)"
    _order = "price desc"

    price = fields.Float("Giá đề nghị", required=True)
    partner_id = fields.Many2one("res.partner", string="Khách hàng", required=True)
    property_id = fields.Many2one("estate.property", string="Bất động sản", required=True)
    
    status = fields.Selection([
        ('accepted', 'Chấp nhận'),
        ('refused', 'Từ chối')
    ], string="Trạng thái", copy=False)

    # Khi chấp nhận Offer -> Tự động tạo Phiếu Đặt Cọc (Deposit)
    def action_accept(self):
        for record in self:
            record.status = 'accepted'
            record.property_id.state = 'offer_accepted'
            record.property_id.buyer_id = record.partner_id
            record.property_id.selling_price = record.price
            
            # Tự động tạo bản ghi Deposit (nháp)
            self.env['estate.property.deposit'].create({
                'property_id': record.property_id.id,
                'partner_id': record.partner_id.id,
                'amount': record.price * 0.1, # Mặc định cọc 10%
                'note': f"Đặt cọc theo offer giá {record.price}"
            })