# -*- coding: utf-8 -*-
# from odoo import http


# class Building(http.Controller):
#     @http.route('/building/building', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/building/building/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('building.listing', {
#             'root': '/building/building',
#             'objects': http.request.env['building.building'].search([]),
#         })

#     @http.route('/building/building/objects/<model("building.building"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('building.object', {
#             'object': obj
#         })
