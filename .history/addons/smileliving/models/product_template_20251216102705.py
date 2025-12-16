from odoo import api, models
from odoo.http import request
from odoo.osv import expression


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _search_get_detail(self, website, order, options):
        """Inject SmileLiving /shop filters into the products_only fuzzy search domain.

        In Odoo 19, /shop uses website._search_with_fuzzy('products_only', ...) which relies on
        product.template._search_get_detail() to build the base domain.
        """
        detail = super()._search_get_detail(website, order, options)

        httprequest = getattr(request, 'httprequest', None)
        path = getattr(httprequest, 'path', '') or ''
        if not path.startswith('/shop'):
            return detail

        args = getattr(httprequest, 'args', {}) or {}

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

        extra_domain = [
            ('is_house', '=', True),
        ]

        # Location filters
        tinhthanh_id = _safe_int(_first(args.get('tinhthanh_id', '')))
        quanhuyen_id = _safe_int(_first(args.get('quanhuyen_id', '')))
        phuongxa_id = _safe_int(_first(args.get('phuongxa_id', '')))
        if tinhthanh_id:
            extra_domain.append(('tinhthanh_id', '=', tinhthanh_id))
        if quanhuyen_id:
            extra_domain.append(('quanhuyen_id', '=', quanhuyen_id))
        if phuongxa_id:
            extra_domain.append(('phuongxa_id', '=', phuongxa_id))

        # Custom filters (multi select)
        filter_type_ids = []
        if hasattr(args, 'getlist'):
            filter_type_ids = [_safe_int(v) for v in args.getlist('filter_type_id')]
        else:
            filter_type_ids = [_safe_int(_first(args.get('filter_type_id', '')))]
        filter_type_ids = [v for v in filter_type_ids if v]
        if filter_type_ids:
            extra_domain.append(('type_id', 'in', filter_type_ids))

        filter_status = _first(args.get('filter_status', ''))
        if filter_status:
            extra_domain.append(('house_status', '=', filter_status))

        filter_area_min = _safe_float(_first(args.get('filter_area_min', '')))
        filter_area_max = _safe_float(_first(args.get('filter_area_max', '')))
        if filter_area_min is not None:
            extra_domain.append(('area', '>=', filter_area_min))
        if filter_area_max is not None:
            extra_domain.append(('area', '<=', filter_area_max))

        filter_price_min = _safe_float(_first(args.get('filter_price_min', '')))
        filter_price_max = _safe_float(_first(args.get('filter_price_max', '')))
        if filter_price_min is not None:
            extra_domain.append(('list_price', '>=', filter_price_min))
        if filter_price_max is not None:
            extra_domain.append(('list_price', '<=', filter_price_max))

        base_domain = detail.get('base_domain')
        if base_domain:
            detail['base_domain'] = expression.AND([base_domain, extra_domain])
        else:
            detail['base_domain'] = extra_domain

        return detail
