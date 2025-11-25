# invoice_property.py
from odoo import models, fields, api, _

class EstateInvoice(models.Model):
    _name = "estate.invoice"
    _description = "Giao dịch Thanh toán BĐS"
    _inherit = ['mail.thread']

    name = fields.Char("Mã giao dịch", default=lambda self: _('New'), readonly=True)
    property_id = fields.Many2one("estate.property", required=True)
    partner_id = fields.Many2one("res.partner", required=True)
    
    description = fields.Char("Nội dung thanh toán")
    origin = fields.Char("Nguồn gốc (Mã cọc)")
    
    amount_total = fields.Monetary("Số tiền", required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='property_id.currency_id')
    
    type = fields.Selection([
        ('deposit', 'Tiền cọc'),
        ('installment', 'Thanh toán đợt'),
        ('liquidation', 'Thanh toán tất toán')
    ], string="Loại thanh toán", required=True)

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('posted', 'Đã ghi nhận'), # Đã tạo account.move
        ('paid', 'Đã thanh toán')  # Khách đã trả tiền
    ], default='draft', tracking=True)

    # Link sang Kế toán chuẩn Odoo
    move_id = fields.Many2one('account.move', string="Hóa đơn Odoo", readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('estate.invoice') or _('New')
        return super(EstateInvoice, self).create(vals)

    def action_post_entry(self):
        """Tạo Hóa đơn (Customer Invoice) trong module Account"""
        for record in self:
            move_vals = {
                'move_type': 'out_invoice',
                'partner_id': record.partner_id.id,
                'invoice_line_ids': [(0, 0, {
                    'name': f"{record.description} - {record.property_id.name}",
                    'quantity': 1,
                    'price_unit': record.amount_total,
                })],
            }
            move = self.env['account.move'].create(move_vals)
            record.move_id = move.id
            record.state = 'posted'