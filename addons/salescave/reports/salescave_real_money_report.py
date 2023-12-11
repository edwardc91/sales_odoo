# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools


class RealMoney(models.Model):
    _name = 'salescave.real.money.report'
    _description = 'SQL view based model for lot real money existence'
    _auto = False

    lot_name = fields.Char(string='Lote', readonly=True)
    lot_date = fields.Date(string="Fecha del lote", readonly=True)
    sum_restored_investment = fields.Float(string='Inversión recuperada', readonly=True)
    sum_real_gain = fields.Float(string='Ganancia real', readonly=True)
    expenses = fields.Float(string='Gastos', readonly=True)
    net_restored_investment = fields.Float(string='Inversión recuperada neta', readonly=True)
    net_real_gain = fields.Float(string='Ganancia neta', readonly=True)

    def _query(self):
        select = """
        SELECT ROW_NUMBER() OVER (order by lot.id)::integer AS id,
                        CAST(lot.purchase_date AS VARCHAR(25)) AS lot_name,
                        lot.purchase_date AS lot_date,
                        lot.total_expenses AS expenses,
                        SUM(product_sale.restored_investment) AS sum_restored_investment,
                        SUM(product_sale.real_gain) AS sum_real_gain,
						SUM(product_sale.restored_investment) + total_expenses AS net_restored_investment,
                        SUM(product_sale.real_gain) - (total_expenses) AS net_real_gain
        """

        from_clause = """
                FROM salescave_sale_product AS product_sale
                INNER JOIN salescave_product_purchase AS product_purchase ON product_purchase.id=product_sale.product_purchase_id
                INNER JOIN salescave_lot AS lot ON product_purchase.lot_id = lot.id
                GROUP BY lot.id, lot_name, lot_date, expenses
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