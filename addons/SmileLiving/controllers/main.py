# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class SmileLivingController(http.Controller):
    
    @http.route('/test', type='http', auth='public')
    def test(self):
        return "<h1>Test route works!</h1>"
    
    @http.route('/smileliving', type='http', auth='public', website=True)
    def homepage(self, **kwargs):
        """Trang chủ - danh sách properties"""
        try:
            # Debug: Kiểm tra model
            properties = request.env['smileliving.house'].search([('status', '=', 'available')])
            
            # Debug: Kiểm tra template
            template = request.env.ref('smileliving.homepage', raise_if_not_found=False)
            
            debug_info = f"""
            <h2>DEBUG INFO</h2>
            <p><strong>Properties found:</strong> {len(properties)}</p>
            <p><strong>Template exists:</strong> {bool(template)}</p>
            <p><strong>Module loaded:</strong> SmileLiving</p>
            """
            
            if properties and template:
                return request.render('smileliving.homepage', {
                    'properties': properties,
                })
            else:
                return debug_info + "<h3 style='color:red'>ERROR: No properties or template not found!</h3>"
                
        except Exception as e:
            return f"<h1>ERROR: {str(e)}</h1>"
    
    @http.route('/smileliving/properties', type='http', auth='public', website=True)
    def property_listing(self, **kwargs):
        """Danh sách properties"""
        domain = []
        if kwargs.get('type'):
            domain.append(('type_id', '=', int(kwargs['type'])))
        
        properties = request.env['smileliving.house'].search(domain)
        property_types = request.env['smileliving.type'].search([])
        
        return request.render('smileliving.property_listing', {
            'properties': properties,
            'property_types': property_types,
        })
    
    @http.route('/smileliving/property/<int:property_id>', type='http', auth='public', website=True)
    def property_detail(self, property_id, **kwargs):
        """Chi tiết property"""
        property = request.env['smileliving.house'].browse(property_id)
        if not property.exists():
            return request.not_found()
            
        return request.render('smileliving.property_detail', {
            'property': property,
        })
