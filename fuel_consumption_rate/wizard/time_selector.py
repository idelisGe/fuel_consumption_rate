import openerp.addons.decimal_precision as dp
from openerp import models, fields, api
from openerp.exceptions import except_orm
from openerp.tools.translate import _

DATE_RANGE = ['asd', 'asdsa']

    
class ConsumptionRateDate(models.TransientModel):
    ''' Open the windows where the user will select the date range for 
    calculate the consumption rate.

    TODO: DOCUMENT.

    '''
    _name = 'consumption.rate.date'
    _description = 'Used for select the date range of consumption.'

    initial_date_range = fields.Date(required=True)
    end_date_range = fields.Date(required=True)

    def raice_exeption(self):
        raise except_orm(
            "Not Selected Vehicle Error",
            _("Must to select a vehicle(s) for calculate the consumption rate.")
        )
    
    @api.multi
    def get_consumption_rate_view(self, vals):
        '''TODO:DOCUMENT
        '''
        import itertools
        from operator import truediv
        LogFuel = self.env['fleet.vehicle.log.fuel']
        assert  vals.get('active_ids', False), self.raice_exeption()
        fuel_ids = ','.join([str(f.id) for f in LogFuel.search(
            [('date', '>=', self.initial_date_range),
             ('date', '<=', self.end_date_range),
             ('vehicle_id', 'in', tuple(vals['active_ids']))
             ])])
        analysed_consumpt = {}
        def build_dataset(self, average_km_liter=0, average_liter_by_hour=0):
            ''' Build the view who will be show by the model
            consumption.rate.result. Use also some calculated field like
            average_km_liter and average_liter_by_hour who initially have 0
            value.
            Note: The chunk of code {0:.4f} is used for take only 4 decimal
            points. here the  

            '''
            self.env.cr.execute("""
            CREATE OR REPLACE VIEW consumption_rate_result AS (
            SELECT
                fv.id AS id,
                liter AS liter,
                '{average_km}' as average_km_liter,
                '{average_l}' as average_liter_by_hour,
                fvc.date as consumption_date,
                fvc.vehicle_id as vehicle_id,
                fvc.amount as amount,
                fvo.value as odometer
            FROM fleet_vehicle_log_fuel AS fv
            INNER JOIN fleet_vehicle_cost AS fvc
                ON(fvc.id=fv.cost_id)
            INNER JOIN fleet_vehicle_odometer fvo
                ON(fvc.odometer_id= fvo.id)
            WHERE fv.id in ({f_ids})
            ) """.format(f_ids=fuel_ids or 'Null',
                         average_km="{0:.4f}".format(average_km_liter),
                         average_l="{0:.4f}".format(average_liter_by_hour)
            ))

        def process_initial_dataset(self):
            ''' Calculate some values like average of km/L and L/H who will
            be passed to the function build dataset.

            '''
            sentence = '''
                SELECT
                    fv.id AS id,
                    liter AS liter,
                    fv.consumption_date as consumption_date,
                    fv.vehicle_id as vehicle_id,
                    fv.amount as amount,
                    fv.odometer as odometer
                FROM consumption_rate_result AS fv
                ORDER BY
                    vehicle_id, consumption_date
            '''
            cr = self.env.cr
            cr.execute(sentence)
            dataset = [{'id':row[0],
                        'liter':row[1],
                        'consumption_date':row[2],
                        'vehicle_id':row[3],
                        'amount':row[4],
                        'odometer':row[5]}
                        for row in cr.fetchall()]
                        
            func = lambda r: r.get('vehicle_id')
            for vehicle_id, fuel_reg in itertools.groupby(dataset, func):
                vehicle_fuel_reg = list(fuel_reg)
                if vehicle_fuel_reg:
                    all_odometers = [r.get('odometer')
                                     for r in vehicle_fuel_reg]
                    if len(vehicle_fuel_reg) > 1:
                        # Removing the last fuel registry if more than one.
                        total_consumpt = sum(r.get('liter')
                                             for r in vehicle_fuel_reg[:-1])
                        km_count = max(all_odometers) - min(all_odometers)
                        analysed_consumpt[vehicle_id] = (km_count,
                                                         total_consumpt)

        build_dataset(self)
        process_initial_dataset(self)
        if analysed_consumpt:
            # This total_km and total_liter are general indicators, and means
            # the total of km by all the selected vehicles and the total of
            # fuel liter consumpted by all the vehicles.
            total_km = sum([analysed_consumpt.get(x)[0]
                            for x in analysed_consumpt.keys()])
            total_liter = sum([analysed_consumpt.get(x)[1]
                               for x in analysed_consumpt.keys()])
            build_dataset(self,average_km_liter=(total_km/total_liter),
                          average_liter_by_hour=(total_liter/total_km))
            return {
                'name': 'Test',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'consumption.rate.result',
                'target': 'current',
                'context': {
                    'initial_date_range': self.initial_date_range,
                    'end_date_range' : self.end_date_range,
                    "search_default_by_vehicle" : 1,
                }
            }
        else:
            raise except_orm(
                "Log Fuel Error",
                _("The selected vehicle have not any fuel registry in this period.")
            )
