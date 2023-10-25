# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools


class Debt(models.Model):
    _name = 'salescave.debt.report'
    _description = 'SQL view based model for lot debt'
    _auto = False

    lot_name = fields.Char(string='Lote', readonly=True)
    product_name = fields.Char(string='Producto', readonly=True)
    buyer_name = fields.Char(string='Comprador', readonly=True)
    debt = fields.Float(string='Deuda', readonly=True)

    def _query(self):
        select = """
             SELECT ROW_NUMBER() OVER (order by product_sale.id)::integer AS id,
                        CAST(lot.purchase_date AS VARCHAR(25)) AS lot_name,
                        product.name AS product_name,
                        product_sale.debt AS debt,
                        buyer.name AS buyer_name
        """

        from_clause = """
                FROM salescave_sale_product AS product_sale
                INNER JOIN salescave_product_purchase AS product_purchase ON product_purchase.id=product_sale.product_purchase_id
                INNER JOIN salescave_product AS product ON product.id=product_purchase.product_id
                INNER JOIN salescave_lot AS lot ON product_purchase.lot_id = lot.id
                INNER JOIN salescave_sale AS sale ON sale.id=product_sale.sale_id
                INNER JOIN res_partner AS buyer ON buyer.id=sale.buyer_id
        """
        
        where_clause = """WHERE debt > 0"""

        expression = """
            %s
            %s
            %s
        """ % (
            select,
            from_clause,
            where_clause,
        )

        query = """ 
                CREATE OR REPLACE VIEW salescave_debt_report AS (
                    %s
                );
        """ % (expression)

        return query

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)

        self.env.cr.execute(self._query())