# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools


class Profit(models.Model):
    _name = 'salescave.profit.report'
    _description = 'SQL view based model for lot profit'
    _auto = False

    lot_name = fields.Char(string='Lote', readonly=True)
    lot_date = fields.Date(string="Fecha del lote", readonly=True)
    product_name = fields.Char(string='Producto', readonly=True)
    total_cost = fields.Float(string='Costo Total', readonly=True)
    restored_investment = fields.Float(string='Inversión recuperada', readonly=True)
    real_gain = fields.Float(string='Ganancia real', readonly=True)

    def _query(self):
        select = """
             SELECT ROW_NUMBER() OVER (order by product_purchase.id)::integer AS id,
                        CAST(lot.purchase_date AS VARCHAR(25)) AS lot_name,
                        lot.purchase_date AS lot_date,
                        product.name AS product_name,
                        product_purchase.total_cost AS total_cost,
                        product_purchase.restored_investment AS restored_investment,
                        product_purchase.real_gain AS real_gain
        """

        from_clause = """
                FROM salescave_product_purchase AS product_purchase
                INNER JOIN salescave_product AS product ON product.id=product_purchase.product_id
                INNER JOIN salescave_lot AS lot ON product_purchase.lot_id = lot.id
        """

        expression = """
            %s
            %s
        """ % (
            select,
            from_clause,
        )

        query = """ 
                CREATE OR REPLACE VIEW salescave_profit_report AS (
                    %s
                );
        """ % (expression)

        return query

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)

        self.env.cr.execute(self._query())