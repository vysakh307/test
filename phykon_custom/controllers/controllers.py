# -*- coding: utf-8 -*-
from odoo import http

# class PhykonCustom(http.Controller):
#     @http.route('/phykon_custom/phykon_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/phykon_custom/phykon_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('phykon_custom.listing', {
#             'root': '/phykon_custom/phykon_custom',
#             'objects': http.request.env['phykon_custom.phykon_custom'].search([]),
#         })

#     @http.route('/phykon_custom/phykon_custom/objects/<model("phykon_custom.phykon_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('phykon_custom.object', {
#             'object': obj
#         })