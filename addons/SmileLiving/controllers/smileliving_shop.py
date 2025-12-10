from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request

class SmileLivingShop(WebsiteSale):

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

    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>',
    ], type='http', auth='public', website=True)
    def shop(self, page=0, category='', search='', **kwargs):
        """Override shop method để thêm context cho filter"""
        # Gọi super() để lấy context gốc
        response = super().shop(category=category, search=search, **kwargs)
        
        # Lấy các filter parameters từ request.httprequest.args (đúng cách)
        # Vì kwargs có thể không có khi chuyển trang
        request_args = request.httprequest.args
        filter_type_id = request_args.get('filter_type_id', '') or kwargs.get('filter_type_id', '')
        filter_status = request_args.get('filter_status', '') or kwargs.get('filter_status', '')
        filter_area_min = request_args.get('filter_area_min', '') or kwargs.get('filter_area_min', '')
        filter_area_max = request_args.get('filter_area_max', '') or kwargs.get('filter_area_max', '')
        filter_price_min = request_args.get('filter_price_min', '') or kwargs.get('filter_price_min', '')
        filter_price_max = request_args.get('filter_price_max', '') or kwargs.get('filter_price_max', '')
        
        # Xử lý nếu là list (từ checkbox)
        if isinstance(filter_type_id, list):
            filter_type_id = filter_type_id[0] if filter_type_id else ''
        if isinstance(filter_status, list):
            filter_status = filter_status[0] if filter_status else ''
        
        # Lấy danh sách property types để hiển thị trong filter
        property_types = request.env['smileliving.type'].sudo().search([
            ('active', '=', True)
        ])
        
        # Cập nhật context với thông tin filter
        response.qcontext['property_types'] = property_types
        response.qcontext['filter_type_id'] = filter_type_id
        response.qcontext['filter_status'] = filter_status
        response.qcontext['filter_area_min'] = filter_area_min
        response.qcontext['filter_area_max'] = filter_area_max
        response.qcontext['filter_price_min'] = filter_price_min
        response.qcontext['filter_price_max'] = filter_price_max
        
        # Thông tin status selection
        response.qcontext['status_options'] = [
            ('available', 'Còn Trống'),
            ('reserved', 'Đã Giữ'),
            ('sold', 'Đã Bán'),
        ]
        
        return response
