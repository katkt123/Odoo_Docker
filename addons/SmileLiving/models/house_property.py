from odoo import models, fields, api, _
import requests

class HouseProperty(models.Model):
    _name = 'smileliving.house'
    _description = 'Bất Động Sản'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Tên Bất Động Sản', required=True, tracking=True, help="Tên của bất động sản")
    type_id = fields.Many2one('smileliving.type', string='Loại Bất Động Sản', required=True, tracking=True, help="Loại bất động sản với các tiện ích")
    price = fields.Float(string='Giá', required=True, tracking=True, digits=(16, 2), help="Giá bất động sản")
    area = fields.Float(string='Diện Tích (m²)', required=True, tracking=True, digits=(10, 2), help="Diện tích bất động sản tính bằng mét vuông")
    status = fields.Selection([('available', 'Còn Trống'), ('reserved', 'Đã Giữ'), ('sold', 'Đã Bán'), ('maintenance', 'Bảo Trì')],
                              string='Trạng Thái', default='available', required=True, tracking=True, help="Trạng thái hiện tại của bất động sản")
    image = fields.Image(string='Hình Ảnh', max_width=1024, max_height=1024, help="Hình ảnh bất động sản")
    description = fields.Text(string='Mô Tả', tracking=True, help="Mô tả chi tiết về bất động sản")
    address = fields.Text(string='Địa Chỉ', required=True, tracking=True, help="Địa chỉ đầy đủ của bất động sản")
    latitude = fields.Float(string='Vĩ Độ', digits=(10, 6), help="Vĩ độ của bất động sản")
    longitude = fields.Float(string='Kinh Độ', digits=(10, 6), help="Kinh độ của bất động sản")
    google_maps_url = fields.Char(string='Google Maps', compute='_compute_google_maps_url', store=True)
    google_maps_embed_url = fields.Char(string='Google Maps Embed', compute='_compute_google_maps_embed_url', store=True)
    google_maps_iframe = fields.Html(string='Google Maps Iframe', compute='_compute_google_maps_iframe', store=True)
    active = fields.Boolean(string='Hoạt Động', default=True, help="Kích hoạt/vô hiệu hóa bản ghi")
    created_date = fields.Datetime(string='Ngày Tạo', default=fields.Datetime.now, readonly=True)
    invoice_count = fields.Integer(string='Số Hóa Đơn', compute='_compute_invoice_count', store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'name' not in vals or not vals['name']:
                vals['name'] = self.env['ir.sequence'].next_by_code('smileliving.house') or 'Bất Động Sản Mới'
        return super(HouseProperty, self).create(vals_list)

    @api.depends('latitude', 'longitude')
    def _compute_google_maps_url(self):
        for record in self:
            if record.latitude and record.longitude:
                record.google_maps_url = f'https://www.google.com/maps?q={record.latitude},{record.longitude}'
            else:
                record.google_maps_url = False

    @api.depends('latitude', 'longitude')
    def _compute_google_maps_embed_url(self):
        for record in self:
            if record.latitude and record.longitude:
                record.google_maps_embed_url = f'https://www.google.com/maps?q={record.latitude},{record.longitude}&output=embed'
            else:
                record.google_maps_embed_url = False

    @api.depends('latitude', 'longitude')
    def _compute_google_maps_iframe(self):
        for record in self:
            if record.latitude and record.longitude:
                embed_url = f'https://www.google.com/maps?q={record.latitude},{record.longitude}&output=embed'
                record.google_maps_iframe = f'<iframe width="100%" height="400" src="{embed_url}" style="border:0;" frameborder="0" allowfullscreen="true"></iframe>'
            else:
                record.google_maps_iframe = '<div style="padding: 20px; text-align: center; color: #666;">Chưa có tọa độ để hiển thị bản đồ</div>'

    @api.depends('name')
    def _compute_invoice_count(self):
        """Compute invoice count"""
        for property in self:
            property.invoice_count = self.env['smileliving.invoice'].search_count([('property_id', '=', property.id)])

    def action_sold(self):
        self.status = 'sold'
        self.message_post(body=_("Bất động sản đã được bán"))

    def action_reserve(self):
        self.status = 'reserved'
        self.message_post(body=_("Bất động sản đã được giữ"))

    def action_available(self):
        self.status = 'available'
        self.message_post(body=_("Bất động sản đã có sẵn"))

    def action_view_invoices(self):
        """View invoices related to this property"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hóa Đơn',
            'res_model': 'smileliving.invoice',
            'view_mode': 'list,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
        }

    def action_open_map_popup(self):
        """Open Google Maps in new window"""
        if self.google_maps_url:
            return {
                'type': 'ir.actions.act_url',
                'url': self.google_maps_url,
                'target': 'new',
            }
        return False

    @api.onchange('address')
    def _onchange_address(self):
        if self.address:
            try:
                url = "https://nominatim.openstreetmap.org/search"
                response = requests.get(url, params={
                    "q": self.address,
                    "format": "json"
                }, headers={"User-Agent": "Odoo"}, timeout=5)
                if response.status_code == 200 and response.json():
                    pos = response.json()[0]
                    self.latitude = float(pos["lat"])
                    self.longitude = float(pos["lon"])
                else:
                    self.latitude = False
                    self.longitude = False
            except Exception:
                self.latitude = False
                self.longitude = False