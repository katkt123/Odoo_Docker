from odoo import api, fields, models
from odoo.exceptions import ValidationError


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
                raise ValidationError('Mỗi product.template chỉ được gắn với 1 smileliving.property.')

    # -------------------------------------------------------------------------
    # Demo reset & seed (VN Real Estate) - for test projects
    # -------------------------------------------------------------------------

    @api.model
    def _cron_reset_and_seed_vn_demo(self):
        """One-time cron job to replace demo e-commerce catalog with VN real-estate demo data.

        This is designed for TEST databases without backups.
        """
        ICP = self.env['ir.config_parameter'].sudo()
        if ICP.get_param('smileliving.vn_demo_seeded'):
            cron = self.env.ref('smileliving.ir_cron_smileliving_reset_seed_vn_demo', raise_if_not_found=False)
            if cron:
                cron.active = False
            return

        self._reset_and_seed_vn_demo(hard_delete=False)

        ICP.set_param('smileliving.vn_demo_seeded', '1')
        cron = self.env.ref('smileliving.ir_cron_smileliving_reset_seed_vn_demo', raise_if_not_found=False)
        if cron:
            cron.active = False

    @api.model
    def reset_and_seed_vn_demo(self, hard_delete=False):
        """Manual entrypoint (can be called from Odoo shell).

        - `hard_delete=False` (default): unpublish + archive demo products.
        - `hard_delete=True`: try unlinking demo products (risky).
        """
        self._reset_and_seed_vn_demo(hard_delete=bool(hard_delete))

    @api.model
    def _reset_and_seed_vn_demo(self, hard_delete=False):
        company = self._seed_target_company()
        self._reset_demo_catalog(company, hard_delete=hard_delete)
        self._delete_previous_seed(company)
        self._seed_vn_real_estate(company)

    @api.model
    def _seed_target_company(self):
        website = self.env['website'].sudo().search([], limit=1)
        if website and website.company_id:
            return website.company_id
        return self.env.company

    @api.model
    def _delete_previous_seed(self, company):
        ProductTmpl = self.env['product.template'].sudo().with_company(company)
        seeded = ProductTmpl.search([
            ('company_id', 'in', [company.id, False]),
            ('product_variant_ids.default_code', '=ilike', 'VNRE-%'),
        ])
        if seeded:
            seeded.unlink()

        props = self.sudo().search([
            ('company_id', 'in', [company.id, False]),
            ('product_tmpl_id.product_variant_ids.default_code', '=ilike', 'VNRE-%'),
        ])
        if props:
            props.unlink()

    @api.model
    def _reset_demo_catalog(self, company, hard_delete=False):
        """Remove/disable existing published shop items (desk, box, etc.).

        By default we *archive + unpublish* to avoid breaking references.
        """
        ProductTmpl = self.env['product.template'].sudo().with_company(company)
        demo_products = ProductTmpl.search([
            ('company_id', 'in', [company.id, False]),
            ('is_published', '=', True),
            ('sale_ok', '=', True),
            ('product_variant_ids.default_code', 'not ilike', 'VNRE-%'),
        ])

        if not demo_products:
            return

        if hard_delete:
            # Best-effort: will fail if referenced by orders/invoices.
            try:
                demo_products.unlink()
                return
            except Exception:
                # Fall back to archive/unpublish.
                pass

        demo_products.write({'is_published': False, 'active': False})

    @api.model
    def _seed_vn_real_estate(self, company):
        """Create VN real-estate demo: categories, amenities, types, products + properties."""
        env = self.env
        ProductTmpl = env['product.template'].sudo().with_company(company)
        PublicCateg = env['product.public.category'].sudo()
        Type = env['smileliving.type'].sudo()
        Amenity = env['smileliving.amenity'].sudo()

        root_categ = PublicCateg.search([('name', '=', 'Bất động sản')], limit=1)
        if not root_categ:
            root_categ = PublicCateg.create({'name': 'Bất động sản'})

        def _child(name):
            rec = PublicCateg.search([('name', '=', name), ('parent_id', '=', root_categ.id)], limit=1)
            if not rec:
                rec = PublicCateg.create({'name': name, 'parent_id': root_categ.id})
            return rec

        categ_apartment = _child('Căn hộ chung cư')
        categ_house = _child('Nhà ở')
        categ_land = _child('Đất nền')
        categ_villa = _child('Biệt thự')
        categ_shophouse = _child('Shophouse')

        amenity_names = [
            'Bảo vệ 24/7',
            'Hồ bơi',
            'Phòng gym',
            'Bãi đậu xe',
            'Thang máy',
            'Sân chơi trẻ em',
            'Công viên nội khu',
            'Gần trường học',
            'Gần bệnh viện',
            'Nội thất cơ bản',
        ]
        amenities = {}
        for name in amenity_names:
            rec = Amenity.search([('name', '=', name)], limit=1)
            if not rec:
                rec = Amenity.create({'name': name})
            amenities[name] = rec

        def _type(name, amenity_list):
            rec = Type.search([('name', '=', name)], limit=1)
            if not rec:
                rec = Type.create({'name': name})
            rec.amenity_ids = [(6, 0, [amenities[a].id for a in amenity_list if a in amenities])]
            return rec

        t_apartment = _type('Căn hộ chung cư', ['Bảo vệ 24/7', 'Hồ bơi', 'Phòng gym', 'Bãi đậu xe', 'Thang máy', 'Sân chơi trẻ em'])
        t_house = _type('Nhà phố', ['Bãi đậu xe', 'Gần trường học', 'Gần bệnh viện', 'Nội thất cơ bản'])
        t_villa = _type('Biệt thự', ['Công viên nội khu', 'Bảo vệ 24/7', 'Hồ bơi', 'Bãi đậu xe'])
        t_land = _type('Đất nền', ['Gần trường học', 'Gần bệnh viện'])
        t_shophouse = _type('Shophouse', ['Bảo vệ 24/7', 'Bãi đậu xe', 'Công viên nội khu'])

        samples = [
            {
                'code': 'VNRE-0001',
                'name': 'Căn hộ 2PN Vinhomes Grand Park',
                'price': 2650000000,
                'area': 68.5,
                'type_id': t_apartment.id,
                'type_sale': 'sale',
                'categ': categ_apartment,
                'address': 'TP. Thủ Đức, TP. Hồ Chí Minh',
                'lat': 10.8429,
                'lng': 106.8287,
            },
            {
                'code': 'VNRE-0002',
                'name': 'Căn hộ 1PN Masteri Thảo Điền',
                'price': 3950000000,
                'area': 52.0,
                'type_id': t_apartment.id,
                'type_sale': 'sale',
                'categ': categ_apartment,
                'address': 'Thảo Điền, TP. Thủ Đức, TP. Hồ Chí Minh',
                'lat': 10.8049,
                'lng': 106.7366,
            },
            {
                'code': 'VNRE-0003',
                'name': 'Nhà phố 1 trệt 2 lầu Quận 7',
                'price': 7850000000,
                'area': 92.0,
                'type_id': t_house.id,
                'type_sale': 'sale',
                'categ': categ_house,
                'address': 'Quận 7, TP. Hồ Chí Minh',
                'lat': 10.7367,
                'lng': 106.7219,
            },
            {
                'code': 'VNRE-0004',
                'name': 'Biệt thự sân vườn Thảo Điền',
                'price': 38500000000,
                'area': 240.0,
                'type_id': t_villa.id,
                'type_sale': 'sale',
                'categ': categ_villa,
                'address': 'Thảo Điền, TP. Thủ Đức, TP. Hồ Chí Minh',
                'lat': 10.8062,
                'lng': 106.7338,
            },
            {
                'code': 'VNRE-0005',
                'name': 'Đất nền KDC Long An (sổ riêng)',
                'price': 1450000000,
                'area': 100.0,
                'type_id': t_land.id,
                'type_sale': 'sale',
                'categ': categ_land,
                'address': 'Đức Hòa, Long An',
                'lat': 10.8739,
                'lng': 106.4253,
            },
            {
                'code': 'VNRE-0006',
                'name': 'Shophouse mặt tiền khu đô thị',
                'price': 12500000000,
                'area': 120.0,
                'type_id': t_shophouse.id,
                'type_sale': 'sale',
                'categ': categ_shophouse,
                'address': 'TP. Thủ Đức, TP. Hồ Chí Minh',
                'lat': 10.8203,
                'lng': 106.7606,
            },
            {
                'code': 'VNRE-0007',
                'name': 'Căn hộ 2PN cho thuê Quận Bình Thạnh',
                'price': 18000000,
                'area': 70.0,
                'type_id': t_apartment.id,
                'type_sale': 'rent',
                'categ': categ_apartment,
                'address': 'Bình Thạnh, TP. Hồ Chí Minh',
                'lat': 10.8106,
                'lng': 106.7091,
            },
        ]

        for s in samples:
            tmpl = ProductTmpl.create({
                'name': s['name'],
                'sale_ok': True,
                'purchase_ok': False,
                'is_published': True,
                'company_id': company.id,
                'detailed_type': 'service',
                'list_price': float(s['price']),
                'public_categ_ids': [(6, 0, [root_categ.id, s['categ'].id])],
            })
            if tmpl.product_variant_id:
                tmpl.product_variant_id.default_code = s['code']

            prop_vals = {
                'product_tmpl_id': tmpl.id,
                'type_id': s['type_id'],
                'type_sale': s['type_sale'],
                'area': float(s['area']),
                'house_status': 'available',
                'address': s['address'],
                'latitude': float(s['lat']),
                'longitude': float(s['lng']),
                'amenity_ids': [(6, 0, Type.browse(s['type_id']).amenity_ids.ids)],
            }
            self.sudo().create(prop_vals)

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

    @api.model
    def reset_and_seed_vn_demo(self, force=False):
        """Reset website catalog to Vietnamese real-estate demo data.

        - Creates VN real-estate types/amenities
        - Creates a small set of real-estate products + linked smileliving.property rows
        - Archives or deletes existing website-published products not linked to a property

        This is intended for test environments without legacy columns/backups.
        """
        ICP = self.env['ir.config_parameter'].sudo()
        if not force and ICP.get_param('smileliving.vn_demo_seeded') == '1':
            return True

        Property = self.env['smileliving.property'].sudo()
        ProductTemplate = self.env['product.template'].sudo()
        Type = self.env['smileliving.type'].sudo()
        Amenity = self.env['smileliving.amenity'].sudo()
        TinhThanh = self.env['tinh.thanh'].sudo()
        QuanHuyen = self.env['quan.huyen'].sudo()
        PhuongXa = self.env['phuong.xa'].sudo()

        # If force: remove previously seeded items (identified by default_code prefix)
        if force:
            seeded_templates = ProductTemplate.search([
                '|',
                ('default_code', '=ilike', 'VNRE-%'),
                ('product_variant_ids.default_code', '=ilike', 'VNRE-%'),
            ])
            seeded_props = Property.search([('product_tmpl_id', 'in', seeded_templates.ids)])
            try:
                seeded_props.unlink()
            except Exception:
                seeded_props.write({'active': False})

            try:
                seeded_templates.unlink()
            except Exception:
                write_vals = {'active': False}
                if 'is_published' in seeded_templates._fields:
                    write_vals['is_published'] = False
                elif 'website_published' in seeded_templates._fields:
                    write_vals['website_published'] = False
                seeded_templates.write(write_vals)

        # Seed geographic samples (minimal, used by filters)
        def _get_or_create(model, domain, vals):
            rec = model.search(domain, limit=1)
            return rec or model.create(vals)

        hcm = _get_or_create(TinhThanh, [('code', '=', '79')], {'name': 'TP. Hồ Chí Minh', 'code': '79', 'active': True})
        hn = _get_or_create(TinhThanh, [('code', '=', '01')], {'name': 'Hà Nội', 'code': '01', 'active': True})
        dn = _get_or_create(TinhThanh, [('code', '=', '48')], {'name': 'Đà Nẵng', 'code': '48', 'active': True})

        q7 = _get_or_create(QuanHuyen, [('code', '=', 'Q7')], {
            'name': 'Quận 7',
            'code': 'Q7',
            'tinhthanh_id': hcm.id,
            'active': True,
        })
        bthanh = _get_or_create(QuanHuyen, [('code', '=', 'BTHANH')], {
            'name': 'Quận Bình Thạnh',
            'code': 'BTHANH',
            'tinhthanh_id': hcm.id,
            'active': True,
        })
        td = _get_or_create(QuanHuyen, [('code', '=', 'THUDUC')], {
            'name': 'TP. Thủ Đức',
            'code': 'THUDUC',
            'tinhthanh_id': hcm.id,
            'active': True,
        })

        tanphu_q7 = _get_or_create(PhuongXa, [('code', '=', 'TANPHU_Q7')], {
            'name': 'Phường Tân Phú',
            'code': 'TANPHU_Q7',
            'quanhuyen_id': q7.id,
            'active': True,
        })

        # Seed types
        def _get_or_create_type(name):
            rec = Type.search([('name', '=', name)], limit=1)
            return rec or Type.create({'name': name})

        type_chcc = _get_or_create_type('Căn hộ chung cư')
        type_nhapho = _get_or_create_type('Nhà phố')
        type_bietthu = _get_or_create_type('Biệt thự')
        type_datnen = _get_or_create_type('Đất nền')
        type_shophouse = _get_or_create_type('Shophouse')

        # Seed amenities
        def _get_or_create_amenity(name):
            rec = Amenity.search([('name', '=', name)], limit=1)
            return rec or Amenity.create({'name': name})

        am_baove = _get_or_create_amenity('Bảo vệ 24/7')
        am_baixe = _get_or_create_amenity('Bãi đỗ xe')
        am_thangmay = _get_or_create_amenity('Thang máy')
        am_hoboi = _get_or_create_amenity('Hồ bơi')
        am_gym = _get_or_create_amenity('Phòng gym')
        am_congvien = _get_or_create_amenity('Công viên')
        am_gantruong = _get_or_create_amenity('Gần trường học')
        am_ganbv = _get_or_create_amenity('Gần bệnh viện')

        # Helper to set default_code across Odoo versions
        def _set_default_code(tmpl, code):
            if 'default_code' in tmpl._fields:
                tmpl.default_code = code
                return
            if tmpl.product_variant_id and 'default_code' in tmpl.product_variant_id._fields:
                tmpl.product_variant_id.default_code = code

        # Seed product templates + properties (company_id=False to avoid multi-company record-rule issues)
        seed_items = [
            {
                'code': 'VNRE-CHCC-001',
                'name': 'Căn hộ 2PN – Quận 7 (TP.HCM)',
                'list_price': 2500000000,
                'type_id': type_chcc,
                'type_sale': 'sale',
                'area': 68.0,
                'address': 'Khu đô thị Phú Mỹ Hưng, Quận 7, TP. Hồ Chí Minh',
                'tinh': hcm,
                'quan': q7,
                'phuong': tanphu_q7,
                'amenities': [am_baove, am_baixe, am_thangmay, am_hoboi, am_gym, am_congvien],
                'lat': 10.7298,
                'lng': 106.7210,
            },
            {
                'code': 'VNRE-CHCC-002',
                'name': 'Căn hộ Studio – Bình Thạnh (TP.HCM)',
                'list_price': 1800000000,
                'type_id': type_chcc,
                'type_sale': 'sale',
                'area': 35.0,
                'address': 'Khu vực Landmark 81, Quận Bình Thạnh, TP. Hồ Chí Minh',
                'tinh': hcm,
                'quan': bthanh,
                'phuong': False,
                'amenities': [am_baove, am_baixe, am_thangmay, am_gym, am_ganbv],
                'lat': 10.7952,
                'lng': 106.7218,
            },
            {
                'code': 'VNRE-NP-001',
                'name': 'Nhà phố 1 trệt 2 lầu – Thủ Đức (TP.HCM)',
                'list_price': 4900000000,
                'type_id': type_nhapho,
                'type_sale': 'sale',
                'area': 92.0,
                'address': 'Khu dân cư, TP. Thủ Đức, TP. Hồ Chí Minh',
                'tinh': hcm,
                'quan': td,
                'phuong': False,
                'amenities': [am_baixe, am_gantruong],
                'lat': 10.8456,
                'lng': 106.7740,
            },
            {
                'code': 'VNRE-BT-001',
                'name': 'Biệt thự – Phú Mỹ Hưng (Quận 7)',
                'list_price': 25000000000,
                'type_id': type_bietthu,
                'type_sale': 'sale',
                'area': 250.0,
                'address': 'Phú Mỹ Hưng, Quận 7, TP. Hồ Chí Minh',
                'tinh': hcm,
                'quan': q7,
                'phuong': False,
                'amenities': [am_baove, am_baixe, am_congvien],
                'lat': 10.7280,
                'lng': 106.7200,
            },
            {
                'code': 'VNRE-DN-001',
                'name': 'Đất nền 100m² – Long An (mẫu)',
                'list_price': 1200000000,
                'type_id': type_datnen,
                'type_sale': 'sale',
                'area': 100.0,
                'address': 'Khu vực Long An (dữ liệu mẫu)',
                'tinh': False,
                'quan': False,
                'phuong': False,
                'amenities': [],
                'lat': 10.6950,
                'lng': 106.2000,
            },
            {
                'code': 'VNRE-SH-001',
                'name': 'Shophouse – Hà Nội (mẫu)',
                'list_price': 9800000000,
                'type_id': type_shophouse,
                'type_sale': 'rent',
                'area': 120.0,
                'address': 'Khu vực Hà Nội (dữ liệu mẫu)',
                'tinh': hn,
                'quan': False,
                'phuong': False,
                'amenities': [am_baove, am_baixe],
                'lat': 21.0285,
                'lng': 105.8542,
            },
            {
                'code': 'VNRE-CHCC-003',
                'name': 'Căn hộ 3PN – Đà Nẵng (mẫu)',
                'list_price': 3600000000,
                'type_id': type_chcc,
                'type_sale': 'sale',
                'area': 85.0,
                'address': 'Khu vực Sơn Trà, Đà Nẵng (dữ liệu mẫu)',
                'tinh': dn,
                'quan': False,
                'phuong': False,
                'amenities': [am_baove, am_baixe, am_thangmay, am_hoboi],
                'lat': 16.0596,
                'lng': 108.2470,
            },
        ]

        for item in seed_items:
            # Prevent duplicates by code
            existing = ProductTemplate.search([
                '|',
                ('default_code', '=', item['code']),
                ('product_variant_ids.default_code', '=', item['code']),
            ], limit=1)
            if not existing:
                tmpl_vals = {
                    'name': item['name'],
                    'list_price': item['list_price'],
                    'sale_ok': True,
                    'company_id': False,
                }
                if 'is_published' in ProductTemplate._fields:
                    tmpl_vals['is_published'] = True
                elif 'website_published' in ProductTemplate._fields:
                    tmpl_vals['website_published'] = True
                if 'detailed_type' in ProductTemplate._fields:
                    tmpl_vals['detailed_type'] = 'service'
                tmpl = ProductTemplate.create(tmpl_vals)
                _set_default_code(tmpl, item['code'])
            else:
                tmpl = existing
                if 'is_published' in tmpl._fields:
                    tmpl.is_published = True
                elif 'website_published' in tmpl._fields:
                    tmpl.website_published = True

            prop = Property.search([('product_tmpl_id', '=', tmpl.id)], limit=1)
            if not prop:
                prop_vals = {
                    'product_tmpl_id': tmpl.id,
                    'type_id': item['type_id'].id,
                    'type_sale': item['type_sale'],
                    'area': float(item['area']),
                    'house_status': 'available',
                    'address': item['address'],
                    'latitude': float(item['lat'] or 0.0),
                    'longitude': float(item['lng'] or 0.0),
                    'tinhthanh_id': item['tinh'].id if item['tinh'] else False,
                    'quanhuyen_id': item['quan'].id if item['quan'] else False,
                    'phuongxa_id': item['phuong'].id if item['phuong'] else False,
                }
                prop = Property.create(prop_vals)

                if item['amenities']:
                    prop.amenity_ids = [(6, 0, [a.id for a in item['amenities']])]

        # Cleanup: remove/disable any website-published products not linked to a property.
        property_product_ids = Property.search([]).mapped('product_tmpl_id').ids
        if property_product_ids:
            candidates = ProductTemplate.search([
                ('is_published', '=', True) if 'is_published' in ProductTemplate._fields else ('website_published', '=', True),
                ('id', 'not in', property_product_ids),
            ])
            if candidates:
                for tmpl in candidates:
                    try:
                        tmpl.unlink()
                    except Exception:
                        write_vals = {'active': False}
                        if 'is_published' in tmpl._fields:
                            write_vals['is_published'] = False
                        elif 'website_published' in tmpl._fields:
                            write_vals['website_published'] = False
                        tmpl.write(write_vals)

        ICP.set_param('smileliving.vn_demo_seeded', '1')
        return True

    @api.model
    def _cron_reset_and_seed_vn_demo(self):
        """One-time cron entrypoint."""
        ICP = self.env['ir.config_parameter'].sudo()
        if ICP.get_param('smileliving.vn_demo_seeded') == '1':
            return True
        return self.reset_and_seed_vn_demo(force=False)
