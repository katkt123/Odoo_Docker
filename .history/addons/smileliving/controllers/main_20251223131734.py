# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json


class SmileLivingController(http.Controller):
    
    @http.route('/test', type='http', auth='public')
    def test(self):
        return "<h1>Test route works!</h1>"
    
    @http.route('/smileliving', type='http', auth='public', website=True)
    def homepage(self, **kwargs):
        """Trang chủ - chỉ hiển thị BĐS"""
        try:
            # Lấy bất động sản từ product.template
            properties = request.env['product.template'].search([
                ('is_house', '=', True),
                ('house_status', '=', 'available')
            ])
            
            return request.render('smileliving.homepage', {
                'properties': properties,
            })
                
        except Exception as e:
            return f"<h1>ERROR: {str(e)}</h1>"
    
    
    @http.route('/smileliving/properties', type='http', auth='public', website=True)
    def property_listing(self, **kwargs):
        """Danh sách properties"""
        domain = []
        if kwargs.get('type'):
            domain.append(('type_id', '=', int(kwargs['type'])))
        
        properties = request.env['product.template'].search(domain + [('is_house', '=', True)])
        property_types = request.env['smileliving.type'].search([])
        
        return request.render('smileliving.property_listing', {
            'properties': properties,
            'property_types': property_types,
        })
    
    @http.route('/smileliving/property/<int:property_id>', type='http', auth='public', website=True)
    def property_detail(self, property_id, **kwargs):
        """Chi tiết property"""
        property = request.env['product.template'].browse(property_id)
        if not property.exists():
            return request.not_found()
             
        return request.render('smileliving.property_detail', {
            'property': property,
            'google_maps_embed_url': property.google_maps_embed_url,
        })
    
    @http.route('/smileliving/interest/<int:property_id>', type='http', auth='public', website=True)
    def show_interest_form(self, property_id, **kwargs):
        """Hiển thị form quan tâm bất động sản"""
        property = request.env['product.template'].browse(property_id)
        if not property.exists():
            return request.not_found()
             
        return request.render('smileliving.interest_form', {
            'property': property,
        })
    
    @http.route('/smileliving/submit_interest/<int:property_id>', type='http', auth='public', website=True, methods=['POST'], csrf=False)
    def submit_interest(self, property_id, **kwargs):
        """Xử lý submit form quan tâm và tạo CRM Lead"""
        try:
            website_company = request.website.company_id if getattr(request, 'website', None) else request.env.company
            lead_model = request.env['crm.lead'].sudo().with_company(website_company)
            property = request.env['product.template'].sudo().browse(property_id)
            if not property.exists():
                return request.redirect('/smileliving?error=property_not_found')
            
            # Lấy thông tin từ form
            name = kwargs.get('name', '').strip()
            email = kwargs.get('email', '').strip()
            phone = kwargs.get('phone', '').strip()
            message = kwargs.get('message', '').strip()
            
            # Validate
            if not name or not email or not phone:
                return request.render('smileliving.interest_form', {
                    'property': property,
                    'error': 'Vui lòng điền đầy đủ thông tin bắt buộc',
                    'values': kwargs
                })
            
            # Tạo hoặc tìm partner
            partner = False
            if email:
                partner = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
                if not partner:
                    partner = request.env['res.partner'].sudo().create({
                        'name': name,
                        'email': email,
                        'phone': phone,
                    })
            
            # Tạo CRM Lead
            lead_name = f"Quan tâm: {property.name} - {name}"
            description = f"""
            Khách hàng quan tâm bất động sản:
            - Tên bất động sản: {property.name}
            - Địa chỉ: {property.address}
            - Giá: {property.list_price:,.0f} VNĐ
            - Diện tích: {property.area} m²
            - Loại hình: {property.type_id.name if property.type_id else 'Chưa xác định'}
            - Trạng thái: {dict(property._fields['house_status'].selection).get(property.house_status) if 'house_status' in property._fields else (property.house_status or '')}
            
            Thông tin khách hàng:
            - Họ tên: {name}
            - Email: {email}
            - Số điện thoại: {phone}
            - Tin nhắn: {message or 'Không có'}
            """
            
            # Lấy UTM và team với sudo để tránh lỗi permissions
            medium_id = False
            source_id = False
            team_id = False
            
            try:
                medium_id = request.env.ref('utm.utm_medium_website').sudo().id
            except:
                pass
                
            try:
                source_id = request.env.ref('utm.utm_source_website').sudo().id
            except:
                pass
                
            try:
                team_id = request.env['crm.team'].sudo().with_company(website_company).search([
                    '|', ('company_id', '=', False), ('company_id', '=', website_company.id)
                ], limit=1).id
            except:
                pass
            
            # Thử tạo lead với priority
            lead_vals = {
                'name': lead_name,
                'description': description,
                'type': 'lead',
                'partner_id': partner.id if partner else False,
                'email_from': email,
                'phone': phone,
                'medium_id': medium_id,
                'source_id': source_id,
                'team_id': team_id,
                'company_id': website_company.id,
            }
            
            # Thêm priority với fallback
            try:
                lead_vals['priority'] = 'high'  # Thử string trước
                lead = lead_model.create(lead_vals)
            except:
                try:
                    lead_vals['priority'] = '2'  # Thử numeric
                    lead = lead_model.create(lead_vals)
                except:
                    # Bỏ priority nếu không hợp lệ
                    lead = lead_model.create(lead_vals)
            
            # Ghi log vào property
            property.sudo().message_post(body=f"Đã tạo CRM Lead <a href='#' data-oe-model='crm.lead' data-oe-id='{lead.id}'>{lead.name}</a> từ quan tâm của khách hàng {name}")
            
            # Redirect đến trang cảm ơn
            return request.render('smileliving.interest_success', {
                'property': property,
                'customer_name': name,
                'lead_id': lead.id
            })
                
        except Exception as e:
            # Log lỗi để debug
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in submit_interest: {str(e)}")
            
            # Trả về form với lỗi
            try:
                property = request.env['product.template'].sudo().browse(property_id)
                return request.render('smileliving.interest_form', {
                    'property': property,
                    'error': f'Có lỗi xảy ra: {str(e)}',
                    'values': kwargs
                })
            except:
                return request.redirect('/smileliving?error=general_error')

    @http.route('/smileliving/wishlist/interest', type='json', auth='public', website=True)
    def wishlist_interest(self, product_id, **kw):
        """Create a crm.lead when a visitor clicks 'Quan tâm' on a wishlist product (JSON route)."""
        try:
            website_company = request.website.company_id if getattr(request, 'website', None) else request.env.company
            lead_model = request.env['crm.lead'].sudo().with_company(website_company)
            product = request.env['product.product'].sudo().browse(int(product_id))
            if not product.exists():
                return {'success': False, 'error': 'Product not found'}
            team_id = False
            try:
                team_id = request.env['crm.team'].sudo().with_company(website_company).search([
                    '|', ('company_id', '=', False), ('company_id', '=', website_company.id)
                ], limit=1).id
            except:
                pass
            lead = lead_model.create({
                'name': f"Quan tâm {product.display_name}",
                'type': 'opportunity',
                'description': f"Sản phẩm wishlist: {product.display_name} (id: {product.id})",
                'team_id': team_id,
                'company_id': website_company.id,
            })
            return {'success': True, 'lead_id': lead.id}
        except Exception as e:
            import logging
            logging.getLogger(__name__).exception('Error creating wishlist interest lead: %s', e)
            return {'success': False, 'error': 'server error'}

    # Same behavior as above, but exposed under the Website Sale wishlist URL namespace.
    # This keeps the frontend route consistent with `/shop/wishlist` (no `/smileliving` prefix).
    @http.route('/shop/wishlist/interest', type='json', auth='public', website=True)
    def shop_wishlist_interest(self, product_id, **kw):
        return self.wishlist_interest(product_id, **kw)
