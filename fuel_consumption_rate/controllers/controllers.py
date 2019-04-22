# -*- coding: utf-8 -*-
from odoo import http

# class FuelConsumptionRate(http.Controller):
#     @http.route('/fuel_consumption_rate/fuel_consumption_rate/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fuel_consumption_rate/fuel_consumption_rate/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fuel_consumption_rate.listing', {
#             'root': '/fuel_consumption_rate/fuel_consumption_rate',
#             'objects': http.request.env['fuel_consumption_rate.fuel_consumption_rate'].search([]),
#         })

#     @http.route('/fuel_consumption_rate/fuel_consumption_rate/objects/<model("fuel_consumption_rate.fuel_consumption_rate"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fuel_consumption_rate.object', {
#             'object': obj
#         })