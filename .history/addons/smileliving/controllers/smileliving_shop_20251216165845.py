from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
from odoo.osv import expression

class SmileLivingShop(WebsiteSale):

    def _get_shop_domain(self, search_term, category, attribute_value_dict):
        """Override to apply SmileLiving filters on the /shop domain (Odoo 19 uses this hook)."""
        domain = super()._get_shop_domain(search_term, category, attribute_value_dict)

        extra_domain = [
            # Only show real-estate products
            ('is_house', '=', True),
        ]

        request_args = request.httprequest.args

        def _first(val):
            return val[0] if isinstance(val, list) and val else val

        def _safe_int(val):
            try:
                return int(val)
            except (TypeError, ValueError):
                return None

        def _safe_float(val):
            try:
                return float(val)
            except (TypeError, ValueError):
                return None

        # Location filters
        tinhthanh_id = _safe_int(_first(request_args.get('tinhthanh_id', '')))
        quanhuyen_id = _safe_int(_first(request_args.get('quanhuyen_id', '')))
        phuongxa_id = _safe_int(_first(request_args.get('phuongxa_id', '')))
        if tinhthanh_id:
            extra_domain.append(('tinhthanh_id', '=', tinhthanh_id))
        if quanhuyen_id:
            extra_domain.append(('quanhuyen_id', '=', quanhuyen_id))
        if phuongxa_id:
            extra_domain.append(('phuongxa_id', '=', phuongxa_id))

        # Custom filters
        filter_type_ids = []
        if hasattr(request_args, 'getlist'):
            filter_type_ids = [_safe_int(v) for v in request_args.getlist('filter_type_id')]
        else:
            filter_type_ids = [_safe_int(_first(request_args.get('filter_type_id', '')))]
        filter_type_ids = [v for v in filter_type_ids if v]
        if filter_type_ids:
            extra_domain.append(('type_id', 'in', tuple(filter_type_ids)))

        type_sale = _first(request_args.get('type_sale', ''))
        if type_sale in ('sale', 'rent'):
            extra_domain.append(('type_sale', '=', type_sale))

        filter_area_min = _safe_float(_first(request_args.get('filter_area_min', '')))
        filter_area_max = _safe_float(_first(request_args.get('filter_area_max', '')))
        if filter_area_min is not None:
            extra_domain.append(('area', '>=', filter_area_min))
        if filter_area_max is not None:
            extra_domain.append(('area', '<=', filter_area_max))

        # (Removed) price filtering

        return expression.AND([domain, extra_domain])

    def _shop_get_query_url_kwargs(self, search, min_price, max_price, **post):
        """Override để thêm các filter SmileLiving vào keep() function"""
        kwargs = super()._shop_get_query_url_kwargs(search, min_price, max_price, **post)
        
        # Lấy các filter parameters từ request
        request_args = request.httprequest.args

        # WebsiteSale thường set min_price/max_price theo available range -> dẫn tới URL luôn có
        # &min_price=...&max_price=... dù user chưa lọc. Chỉ giữ lại nếu user thực sự truyền.
        raw_min_price = request_args.get('min_price', '')
        raw_max_price = request_args.get('max_price', '')
        if not raw_min_price:
            kwargs.pop('min_price', None)
        if not raw_max_price:
            kwargs.pop('max_price', None)

        filter_type_id = request_args.getlist('filter_type_id') if hasattr(request_args, 'getlist') else request_args.get('filter_type_id', '')
        type_sale = request_args.get('type_sale', '')
        filter_area_min = request_args.get('filter_area_min', '')
        filter_area_max = request_args.get('filter_area_max', '')
        # (Removed) price filtering
        
        # Lấy filter địa lý
        tinhthanh_id = request_args.get('tinhthanh_id', '')
        quanhuyen_id = request_args.get('quanhuyen_id', '')
        phuongxa_id = request_args.get('phuongxa_id', '')
        
        # Xử lý nếu là list (multi select)
        if isinstance(filter_type_id, (list, tuple)):
            filter_type_id = [v for v in filter_type_id if v]
        if isinstance(type_sale, list):
            type_sale = type_sale[0] if type_sale else ''
        
        # Thêm vào kwargs để keep() giữ lại khi chuyển trang
        if filter_type_id:
            kwargs['filter_type_id'] = filter_type_id
        if type_sale:
            kwargs['type_sale'] = type_sale
        if filter_area_min:
            kwargs['filter_area_min'] = filter_area_min
        if filter_area_max:
            kwargs['filter_area_max'] = filter_area_max
        # (Removed) price filtering
        
        # Thêm filter địa lý vào kwargs
        if tinhthanh_id:
            kwargs['tinhthanh_id'] = tinhthanh_id
        if quanhuyen_id:
            kwargs['quanhuyen_id'] = quanhuyen_id
        if phuongxa_id:
            kwargs['phuongxa_id'] = phuongxa_id
        
        return kwargs

    def _get_search_domain(self, search, category, attrib_values):
        """Override để thêm domain filter theo thuộc tính BĐS"""
        domain = super()._get_search_domain(search, category, attrib_values)
        
        # Chỉ hiển thị sản phẩm BĐS
        domain.append(('is_house', '=', True))
        
        # Lấy filter parameters từ request
        filter_type_id = request.httprequest.args.get('filter_type_id', '')
        # Lấy filter_status - có thể là string hoặc list nếu có nhiều checkbox
        filter_status = request.httprequest.args.get('filter_status', '')
        # Nếu là list (khi có nhiều checkbox được check), lấy giá trị đầu tiên
        if isinstance(filter_status, list):
            filter_status = filter_status[0] if filter_status else ''
        filter_area_min = request.httprequest.args.get('filter_area_min', '')
        filter_area_max = request.httprequest.args.get('filter_area_max', '')
        # (Removed) price filtering
        
        # Lấy filter địa lý
        tinhthanh_id = request.httprequest.args.get('tinhthanh_id', '')
        quanhuyen_id = request.httprequest.args.get('quanhuyen_id', '')
        phuongxa_id = request.httprequest.args.get('phuongxa_id', '')
        
        # Filter theo địa lý
        if tinhthanh_id:
            try:
                domain.append(('tinhthanh_id', '=', int(tinhthanh_id)))
                print(f"DEBUG: Filter theo tinhthanh_id = {tinhthanh_id}")
            except (ValueError, TypeError):
                pass
        if quanhuyen_id:
            try:
                domain.append(('quanhuyen_id', '=', int(quanhuyen_id)))
                print(f"DEBUG: Filter theo quanhuyen_id = {quanhuyen_id}")
            except (ValueError, TypeError):
                pass
        if phuongxa_id:
            try:
                domain.append(('phuongxa_id', '=', int(phuongxa_id)))
                print(f"DEBUG: Filter theo phuongxa_id = {phuongxa_id}")
            except (ValueError, TypeError):
                pass
        
        print(f"DEBUG: Final domain: {domain}")
        
        # Filter theo loại BĐS
        if filter_type_id:
            try:
                # Nếu là list, lấy giá trị đầu tiên
                if isinstance(filter_type_id, list):
                    filter_type_id = filter_type_id[0] if filter_type_id else ''
                domain.append(('type_id', '=', int(filter_type_id)))
            except (ValueError, TypeError):
                pass
        
        # Filter theo trạng thái
        # Nếu có filter_status, dùng giá trị đó
        # Nếu không có, không filter theo trạng thái (hiển thị tất cả)
        if filter_status:
            domain.append(('house_status', '=', filter_status))
        # Bỏ mặc định 'available' để cho phép hiển thị tất cả khi không filter
        
        # Filter theo diện tích
        if filter_area_min:
            try:
                domain.append(('area', '>=', float(filter_area_min)))
            except (ValueError, TypeError):
                pass
        if filter_area_max:
            try:
                domain.append(('area', '<=', float(filter_area_max)))
            except (ValueError, TypeError):
                pass
        
        # (Removed) price filtering
        
        return domain

    def _get_products_domain(self, search, category, attrib_values, **kwargs):
        """Override để thêm domain filter theo thuộc tính BĐS - Odoo 19 có thể dùng method này"""
        domain = super()._get_products_domain(search, category, attrib_values, **kwargs)
        
        # Chỉ hiển thị sản phẩm BĐS
        domain.append(('is_house', '=', True))
        
        # Lấy filter parameters từ request
        tinhthanh_id = request.httprequest.args.get('tinhthanh_id', '')
        quanhuyen_id = request.httprequest.args.get('quanhuyen_id', '')
        phuongxa_id = request.httprequest.args.get('phuongxa_id', '')
        
        print(f"DEBUG: _get_products_domain - tinhthanh_id={tinhthanh_id}, quanhuyen_id={quanhuyen_id}, phuongxa_id={phuongxa_id}")
        
        # Filter theo địa lý
        if tinhthanh_id:
            try:
                domain.append(('tinhthanh_id', '=', int(tinhthanh_id)))
                print(f"DEBUG: Filter theo tinhthanh_id = {tinhthanh_id}")
            except (ValueError, TypeError):
                pass
        if quanhuyen_id:
            try:
                domain.append(('quanhuyen_id', '=', int(quanhuyen_id)))
                print(f"DEBUG: Filter theo quanhuyen_id = {quanhuyen_id}")
            except (ValueError, TypeError):
                pass
        if phuongxa_id:
            try:
                domain.append(('phuongxa_id', '=', int(phuongxa_id)))
                print(f"DEBUG: Filter theo phuongxa_id = {phuongxa_id}")
            except (ValueError, TypeError):
                pass
        
        print(f"DEBUG: Final domain in _get_products_domain: {domain}")
        return domain

    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>',
    ], type='http', auth='public', website=True)
    def shop(self, page=0, category='', search='', **kwargs):
        """Override shop method để thêm context cho filter"""
        # Gọi super() để lấy context gốc
        # Gọi super() để lấy context gốc
        response = super().shop(category=category, search=search, **kwargs)
        
        # Lấy filter parameters từ request.httprequest.args (đúng cách)
        # Vì kwargs có thể không có khi chuyển trang
        request_args = request.httprequest.args
        filter_type_id = request_args.get('filter_type_id', '') or kwargs.get('filter_type_id', '')
        type_sale = request_args.get('type_sale', '') or kwargs.get('type_sale', '')
        filter_area_min = request_args.get('filter_area_min', '') or kwargs.get('filter_area_min', '')
        filter_area_max = request_args.get('filter_area_max', '') or kwargs.get('filter_area_max', '')
        # (Removed) price filtering
        
        # Lấy filter địa lý
        tinhthanh_id = request_args.get('tinhthanh_id', '') or kwargs.get('tinhthanh_id', '')
        quanhuyen_id = request_args.get('quanhuyen_id', '') or kwargs.get('quanhuyen_id', '')
        phuongxa_id = request_args.get('phuongxa_id', '') or kwargs.get('phuongxa_id', '')
        
        # Xử lý nếu là list (từ checkbox)
        if isinstance(filter_type_id, list):
            filter_type_id = filter_type_id[0] if filter_type_id else ''
        if isinstance(type_sale, list):
            type_sale = type_sale[0] if type_sale else ''

        # Available min/max area for slider (global across real-estate)
        area_stats = request.env['product.template'].sudo().read_group(
            [('is_house', '=', True), ('area', '!=', False)],
            ['area:min', 'area:max'],
            []
        )
        available_min_area = 0.0
        available_max_area = 0.0
        if area_stats:
            available_min_area = float(area_stats[0].get('area_min') or 0.0)
            available_max_area = float(area_stats[0].get('area_max') or available_min_area or 0.0)

        def _safe_float(val):
            try:
                return float(val)
            except (TypeError, ValueError):
                return None

        current_area_min = _safe_float(filter_area_min)
        current_area_max = _safe_float(filter_area_max)
        if current_area_min is None:
            current_area_min = available_min_area
        if current_area_max is None:
            current_area_max = available_max_area
        
        # Lấy danh sách property types để hiển thị trong filter
        property_types = request.env['smileliving.type'].sudo().search([
            ('active', '=', True)
        ])
        
        # Lấy dữ liệu địa lý
        tinhthanhs = request.env['tinh.thanh'].sudo().search([
            ('active', '=', True)
        ], order='name')
        
        quanhuyens = request.env['quan.huyen'].sudo().search([
            ('active', '=', True)
        ], order='name')
        
        phuongxas = request.env['phuong.xa'].sudo().search([
            ('active', '=', True)
        ], order='name')
        
        # Cập nhật context với thông tin filter
        response.qcontext['property_types'] = property_types
        response.qcontext['tinhthanhs'] = tinhthanhs
        response.qcontext['quanhuyens'] = quanhuyens
        response.qcontext['phuongxas'] = phuongxas
        response.qcontext['filter_type_id'] = filter_type_id
        response.qcontext['type_sale'] = type_sale
        response.qcontext['filter_area_min'] = current_area_min
        response.qcontext['filter_area_max'] = current_area_max
        response.qcontext['available_min_area'] = available_min_area
        response.qcontext['available_max_area'] = available_max_area
        # (Removed) price filtering
        
        # Thêm context cho filter địa lý
        response.qcontext['tinhthanh_id'] = tinhthanh_id
        response.qcontext['quanhuyen_id'] = quanhuyen_id
        response.qcontext['phuongxa_id'] = phuongxa_id
        
        return response

    @http.route('/smileliving/get_quanhuyen', type='json', auth='public', website=True)
    def get_quanhuyen(self, tinhthanh_id):
        """API để load quận huyện theo tỉnh thành"""
        if tinhthanh_id:
            quanhuyens = request.env['quan.huyen'].sudo().search([
                ('tinhthanh_id', '=', int(tinhthanh_id)),
                ('active', '=', True)
            ], order='name')
            return [{'id': q.id, 'name': q.name} for q in quanhuyens]
        return []

    @http.route('/smileliving/get_phuongxa', type='json', auth='public', website=True)
    def get_phuongxa(self, quanhuyen_id):
        """API để load phường xã theo quận huyện"""
        if quanhuyen_id:
            phuongxas = request.env['phuong.xa'].sudo().search([
                ('quanhuyen_id', '=', int(quanhuyen_id)),
                ('active', '=', True)
            ], order='name')
            return [{'id': p.id, 'name': p.name} for p in phuongxas]
        return []
