# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ConsumptionRateResult(models.Model):
    '''TODO: DOCUMENT

    '''
    _name = 'consumption.rate.result'
    _auto = False

    liter = fields.Float()
    vehicle_id = fields.Many2one('fleet.vehicle', readonly=True)
    amount = fields.Float()
    odometer = fields.Integer()
    consumption_date = fields.Date(readonly=True)
    km_by_liter = fields.Float(compute='get_consumption_rate',
                                    readonly=True)
    liter_by_hour = fields.Float(compute='get_consumption_rate',
                                             readonly=True)
    average_km_liter = fields.Char(readonly=True)
    average_liter_by_hour = fields.Char(readonly=True)

    def get_consumption_rate(self):
        ''' Calculate the consumption rate by each vehicle.

        '''
        from operator import truediv
        analysed_consumpt = {}
        for consump in self:
            if not analysed_consumpt.get(consump.vehicle_id, False):
                fuel_registries = [(x.liter, x.id) for x in self
                                  if x.vehicle_id == consump.vehicle_id]
                # Sorting all the fuel registry.
                sorted_registries = sorted(fuel_registries, key=lambda r: r[1])
                # Removing the last fuel registry if exist more than one.
                if len(sorted_registries) > 1:
                    sorted_registries = sorted_registries[:-1]
                total_consumpt = sum([x[0] for x in sorted_registries])
                all_odometers = [x.odometer for x in self
                                 if x.vehicle_id == consump.vehicle_id]
                if len(all_odometers) > 1:
                    real_odometer = max(all_odometers) - min(all_odometers)
                else:
                    real_odometer = all_odometers[0]
                if total_consumpt != 0:
                    consump.km_by_liter = truediv(real_odometer,
                                                       total_consumpt)
                    consump.liter_by_hour = truediv(total_consumpt,
                                                                real_odometer)
                else:
                    consump.km_by_liter = 0
                    consump.liter_by_hour = 0
                analysed_consumpt[consump.vehicle_id.id] = consump.km_by_liter
            else:
                consump.km_by_liter = analysed_consumpt[
                    consump.vehicle_id.id]

    @api.model_cr
    def init(self):
        pass
        # cr.execute("""
        # CREATE OR REPLACE VIEW consumption_rate_result AS (
        # SELECT 
        #     fv.id AS id,
        #     liter AS liter,
        #     fvc.date as consumption_date,
        #     fvc.vehicle_id as vehicle_id,
        #     fvc.amount as amount,
        #     fvo.value as odometer
        # FROM fleet_vehicle_log_fuel AS fv
        # INNER JOIN fleet_vehicle_cost AS fvc 
        #     ON(fvc.id=fv.cost_id)
        # INNER JOIN fleet_vehicle_odometer fvo 
        #     ON(fvc.odometer_id= fvo.id)
        
        # )""")


