from odoo import models, fields, api, _


class EstatePropertyDeposit(models.Model):
    _name = "estate.property.deposit"
    _description = "Phiếu Đặt Cọc / Giữ Chỗ"
    _inherit = ['mail.thread']

    name = fields.Char("Mã đặt cọc", required=True, copy=False, readonly=True, default=lambda self: _('New'))
    property_id = fields.Many2one("estate.property", string ="Tên bất động sản", required=True)
    partner_id = fields.Many2one("res.partner", string="Khách hàng", required=True)
    
    amount = fields.Monetary("Số tiền cọc", required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='property_id.currency_id')
    date_deposit = fields.Date("Ngày đặt", default=fields.Date.today())
    note = fields.Text("Ghi chú")

    state = fields.Selection([
        ('draft', 'Nháp'),
        ('confirmed', 'Đã xác nhận'),
        ('converted', 'Đã chuyển thành Hóa đơn'),
        ('cancel', 'Hủy')
    ], default='draft', tracking=True)

    @api.model
    def create(self, vals_list):
        if isinstance(vals_list, list):
            # Xử lý trường hợp tạo nhiều bản ghi
            for vals in vals_list:
                if vals.get('name', _('New')) == _('New'):
                    vals['name'] = self.env['ir.sequence'].next_by_code('estate.property.deposit') or _('New')
            return super().create(vals_list)
        else:
            # Xử lý trường hợp tạo một bản ghi
            if vals_list.get('name', _('New')) == _('New'):
                vals_list['name'] = self.env['ir.sequence'].next_by_code('estate.property.deposit') or _('New')
            return super().create(vals_list)

    def action_create_invoice(self):
        self.ensure_one()
        invoice = self.env['estate.invoice'].create({
            'property_id': self.property_id.id,
            'partner_id': self.partner_id.id,
            'amount_total': self.amount,
            'description': f"Thanh toán tiền cọc: {self.name}",
            'type': 'deposit',
            'origin': self.name
        })
        self.state = 'converted'
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'estate.invoice',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }