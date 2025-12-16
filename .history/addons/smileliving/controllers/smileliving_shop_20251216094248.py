from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request

class SmileLivingShop(WebsiteSale):

    def _get_shop_domain(self, search_term, category, attribute_value_dict):
        """Override to apply SmileLiving filters on the /shop domain (Odoo 19 uses this hook)."""
        domain = super()._get_shop_domain(search_term, category, attribute_value_dict)

        # Only show real-estate products
        domain.append(('is_house', '=', True))

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
            domain.append(('tinhthanh_id', '=', tinhthanh_id))
        if quanhuyen_id:
            domain.append(('quanhuyen_id', '=', quanhuyen_id))
        if phuongxa_id:
            domain.append(('phuongxa_id', '=', phuongxa_id))

        # Custom filters
        filter_type_id = _safe_int(_first(request_args.get('filter_type_id', '')))
        if filter_type_id:
            domain.append(('type_id', '=', filter_type_id))

        filter_status = _first(request_args.get('filter_status', ''))
        if filter_status:
            domain.append(('house_status', '=', filter_status))

        filter_area_min = _safe_float(_first(request_args.get('filter_area_min', '')))
        filter_area_max = _safe_float(_first(request_args.get('filter_area_max', '')))
        if filter_area_min is not None:
            domain.append(('area', '>=', filter_area_min))
        if filter_area_max is not None:
            domain.append(('area', '<=', filter_area_max))

        filter_price_min = _safe_float(_first(request_args.get('filter_price_min', '')))
        filter_price_max = _safe_float(_first(request_args.get('filter_price_max', '')))
        if filter_price_min is not None:
            domain.append(('list_price', '>=', filter_price_min))
        if filter_price_max is not None:
            domain.append(('list_price', '<=', filter_price_max))

        return domain

    def _shop_get_query_url_kwargs(self, search, min_price, max_price, **post):
        """Override để thêm các filter SmileLiving vào keep() function"""
        kwargs = super()._shop_get_query_url_kwargs(search, min_price, max_price, **post)
        
        # Lấy các filter parameters từ request
        request_args = request.httprequest.args
        filter_type_id = request_args.get('filter_type_id', '')
        filter_status = request_args.get('filter_status', '')
        filter_area_min = request_args.get('filter_area_min', '')
        filter_area_max = request_args.get('filter_area_max', '')
        filter_price_min = request_args.get('filter_price_min', '')
        filter_price_max = request_args.get('filter_price_max', '')
        
        # Lấy filter địa lý
        tinhthanh_id = request_args.get('tinhthanh_id', '')
        quanhuyen_id = request_args.get('quanhuyen_id', '')
        phuongxa_id = request_args.get('phuongxa_id', '')
        
        # Xử lý nếu là list
        if isinstance(filter_type_id, list):
            filter_type_id = filter_type_id[0] if filter_type_id else ''
        if isinstance(filter_status, list):
            filter_status = filter_status[0] if filter_status else ''
        
        # Thêm vào kwargs để keep() giữ lại khi chuyển trang
        if filter_type_id:
            kwargs['filter_type_id'] = filter_type_id
        if filter_status:
            kwargs['filter_status'] = filter_status
        if filter_area_min:
            kwargs['filter_area_min'] = filter_area_min
        if filter_area_max:
            kwargs['filter_area_max'] = filter_area_max
        if filter_price_min:
            kwargs['filter_price_min'] = filter_price_min
        if filter_price_max:
            kwargs['filter_price_max'] = filter_price_max
        
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
        filter_price_min = request.httprequest.args.get('filter_price_min', '')
        filter_price_max = request.httprequest.args.get('filter_price_max', '')
        
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
        
        # Filter theo giá
        if filter_price_min:
            try:
                domain.append(('list_price', '>=', float(filter_price_min)))
            except (ValueError, TypeError):
                pass
        if filter_price_max:
            try:
                domain.append(('list_price', '<=', float(filter_price_max)))
            except (ValueError, TypeError):
                pass
        
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
        print(f"DEBUG: Shop method called with kwargs: {kwargs}")
        
        # Lấy filter địa lý từ kwargs
        tinhthanh_id = kwargs.get('tinhthanh_id', '')
        quanhuyen_id = kwargs.get('quanhuyen_id', '')
        phuongxa_id = kwargs.get('phuongxa_id', '')
        
        print(f"DEBUG: Shop method - tinhthanh_id={tinhthanh_id}, quanhuyen_id={quanhuyen_id}, phuongxa_id={phuongxa_id}")
        
        # Gọi super() để lấy context gốc
        response = super().shop(category=category, search=search, **kwargs)
        
        # Lấy lại filter từ request để đảm bảo có giá trị
        request_args = request.httprequest.args
        tinhthanh_id = request_args.get('tinhthanh_id', '') or kwargs.get('tinhthanh_id', '')
        quanhuyen_id = request_args.get('quanhuyen_id', '') or kwargs.get('quanhuyen_id', '')
        phuongxa_id = request_args.get('phuongxa_id', '') or kwargs.get('phuongxa_id', '')
        
        print(f"DEBUG: After super() - tinhthanh_id={tinhthanh_id}, quanhuyen_id={quanhuyen_id}, phuongxa_id={phuongxa_id}")
        
        # Lấy filter parameters từ request.httprequest.args (đúng cách)
        # Vì kwargs có thể không có khi chuyển trang
        request_args = request.httprequest.args
        filter_type_id = request_args.get('filter_type_id', '') or kwargs.get('filter_type_id', '')
        filter_status = request_args.get('filter_status', '') or kwargs.get('filter_status', '')
        filter_area_min = request_args.get('filter_area_min', '') or kwargs.get('filter_area_min', '')
        filter_area_max = request_args.get('filter_area_max', '') or kwargs.get('filter_area_max', '')
        filter_price_min = request_args.get('filter_price_min', '') or kwargs.get('filter_price_min', '')
        filter_price_max = request_args.get('filter_price_max', '') or kwargs.get('filter_price_max', '')
        
        # Lấy filter địa lý
        tinhthanh_id = request_args.get('tinhthanh_id', '') or kwargs.get('tinhthanh_id', '')
        quanhuyen_id = request_args.get('quanhuyen_id', '') or kwargs.get('quanhuyen_id', '')
        phuongxa_id = request_args.get('phuongxa_id', '') or kwargs.get('phuongxa_id', '')
        
        print(f"DEBUG: Shop method - tinhthanh_id={tinhthanh_id}, quanhuyen_id={quanhuyen_id}, phuongxa_id={phuongxa_id}")
        
        # Xử lý nếu là list (từ checkbox)
        if isinstance(filter_type_id, list):
            filter_type_id = filter_type_id[0] if filter_type_id else ''
        if isinstance(filter_status, list):
            filter_status = filter_status[0] if filter_status else ''
        
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
        response.qcontext['filter_status'] = filter_status
        response.qcontext['filter_area_min'] = filter_area_min
        response.qcontext['filter_area_max'] = filter_area_max
        response.qcontext['filter_price_min'] = filter_price_min
        response.qcontext['filter_price_max'] = filter_price_max
        
        # Thêm context cho filter địa lý
        response.qcontext['tinhthanh_id'] = tinhthanh_id
        response.qcontext['quanhuyen_id'] = quanhuyen_id
        response.qcontext['phuongxa_id'] = phuongxa_id
        
        # Thông tin status selection
        response.qcontext['status_options'] = [
            ('available', 'Còn Trống'),
            ('reserved', 'Đã Giữ'),
            ('sold', 'Đã Bán'),
        ]
        
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
