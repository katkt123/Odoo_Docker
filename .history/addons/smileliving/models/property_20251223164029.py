from odoo import api, fields, models


class SmileLivingProperty(models.Model):
    _name = 'smileliving.property'
    _description = 'Bất Động Sản'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc, id desc'

    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Sản phẩm (Product Template)',
        required=True,
        ondelete='cascade',
        index=True,
        tracking=True,
    )

    company_id = fields.Many2one(
        'res.company',
        string='Công ty',
        related='product_tmpl_id.company_id',
        store=True,
        readonly=True,
    )

    type_id = fields.Many2one(
        'smileliving.type',
        string='Danh Mục Bất Động Sản',
        tracking=True,
    )

    type_sale = fields.Selection(
        [
            ('sale', 'Mua bán'),
            ('rent', 'Cho thuê'),
        ],
        string='Loại',
        default='sale',
        tracking=True,
    )

    area = fields.Float(
        string='Diện Tích (m²)',
        required=True,
        tracking=True,
        digits=(10, 2),
    )

    house_status = fields.Selection(
        [
            ('available', 'Còn Trống'),
            ('reserved', 'Đã Giữ'),
            ('sold', 'Đã Bán'),
            ('maintenance', 'Bảo Trì'),
        ],
        string='Trạng Thái',
        default='available',
        tracking=True,
    )

    description_detail = fields.Text(string='Mô Tả Chi Tiết')

    address = fields.Text(string='Địa Chỉ', tracking=True)

    tinhthanh_id = fields.Many2one('tinh.thanh', string='Tỉnh/Thành phố', tracking=True)
    quanhuyen_id = fields.Many2one('quan.huyen', string='Quận/Huyện', tracking=True)
    phuongxa_id = fields.Many2one('phuong.xa', string='Phường/Xã', tracking=True)

    amenity_ids = fields.Many2many(
        'smileliving.amenity',
        'smileliving_property_amenity_rel',
        'property_id',
        'amenity_id',
        string='Tiện Ích',
        tracking=True,
        help='Các tiện ích của bất động sản (chọn nhiều).',
    )

    latitude = fields.Float(string='Vĩ Độ', digits=(10, 6))
    longitude = fields.Float(string='Kinh Độ', digits=(10, 6))

    google_maps_url = fields.Char(string='Google Maps URL', compute='_compute_google_maps_urls', store=True)
    google_maps_embed_url = fields.Char(string='Google Maps Embed URL', compute='_compute_google_maps_urls', store=True)
    google_maps_iframe = fields.Html(string='Google Maps Iframe', compute='_compute_google_maps_iframe', store=True)

    @api.constrains('product_tmpl_id')
    def _check_unique_product_tmpl(self):
        for rec in self:
            if not rec.product_tmpl_id:
                continue
            dup = self.search([
                ('id', '!=', rec.id),
                ('product_tmpl_id', '=', rec.product_tmpl_id.id),
            ], limit=1)
            if dup:
                raise ValueError('Mỗi product.template chỉ được gắn với 1 smileliving.property.')

    @api.depends('latitude', 'longitude')
    def _compute_google_maps_urls(self):
        for rec in self:
            if rec.latitude and rec.longitude:
                rec.google_maps_url = f"https://www.google.com/maps?q={rec.latitude},{rec.longitude}"
                rec.google_maps_embed_url = f"https://www.google.com/maps?q={rec.latitude},{rec.longitude}&output=embed"
            else:
                rec.google_maps_url = False
                rec.google_maps_embed_url = False

    @api.depends('google_maps_embed_url')
    def _compute_google_maps_iframe(self):
        for rec in self:
            if rec.google_maps_embed_url:
                rec.google_maps_iframe = (
                    f"<iframe width=\"100%\" height=\"400\" src=\"{rec.google_maps_embed_url}\" "
                    f"style=\"border:0;\" allowfullscreen=\"\"></iframe>"
                )
            else:
                rec.google_maps_iframe = "<div>Không có bản đồ</div>"

    @api.onchange('tinhthanh_id')
    def _onchange_tinhthanh_id(self):
        if self.tinhthanh_id:
            self.quanhuyen_id = False
            self.phuongxa_id = False

    @api.onchange('quanhuyen_id')
    def _onchange_quanhuyen_id(self):
        if self.quanhuyen_id:
            self.phuongxa_id = False
