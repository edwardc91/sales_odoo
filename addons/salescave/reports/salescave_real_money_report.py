# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools


class RealMoney(models.Model):
    _name = 'salescave.real.money.report'
    _description = 'SQL view based model for lot real money existence'
    _auto = False

    lot_name = fields.Char(string='Lote', readonly=True)
    lot_date = fields.Date(string="Fecha del lote", readonly=True)
    restored_investment = fields.Float(string='Inversión recuperada', readonly=True)
    real_gain = fields.Float(string='Ganancia real', readonly=True)
    expenses = fields.Float(string='Gastos', readonly=True)
    total_inversion_retirements_value = fields.Float(string='Retiros desde inversión', readonly=True)
    total_gain_retirements_value = fields.Float(string='Retiros desde ganancia', readonly=True)
    net_restored_investment = fields.Float(string='Inversión recuperada neta', readonly=True)
    net_real_gain = fields.Float(string='Ganancia neta', readonly=True)

    def _query(self):
        select = """
             SELECT ROW_NUMBER() OVER (order by lot.id)::integer AS id,
                        CAST(lot.purchase_date AS VARCHAR(25)) AS lot_name,
                        lot.purchase_date AS lot_date,
                        lot.total_expenses AS expenses,
                        lot.total_inversion_retirements_value AS total_inversion_retirements_value,
                        lot.total_gain_retirements_value AS total_gain_retirements_value,
                        lot.restored_investment AS restored_investment,
                        lot.real_gain AS real_gain,
                        CASE
                            WHEN real_gain>=total_expenses 
                            THEN (restored_investment + total_expenses) - total_inversion_retirements_value
                            ELSE restored_investment - total_inversion_retirements_value
                        END AS net_restored_investment,
                        CASE
                            WHEN real_gain>=total_expenses 
                            THEN (real_gain - total_expenses) - total_gain_retirements_value
                            ELSE real_gain - total_gain_retirements_value
                        END AS net_real_gain
        """

        from_clause = """
                FROM salescave_lot AS lot
        """

        expression = """
            %s
            %s
        """ % (
            select,
            from_clause,
        )

        query = """ 
                CREATE OR REPLACE VIEW salescave_real_money_report AS (
                    %s
                );
        """ % (expression)

        return query

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)

        self.env.cr.execute(self._query())