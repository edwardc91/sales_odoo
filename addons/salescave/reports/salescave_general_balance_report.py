# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools


class GeneralBalanceReport(models.Model):
    _name = 'salescave.general.balance.report'
    _description = 'SQL view based model for general balance of money report'
    _auto = False

    current_restored_inversion = fields.Float(string='Inversión recuperada', readonly=True)
    current_gain = fields.Float(string='Ganancia real', readonly=True)

    def _query(self):
        select = """
        SELECT ROW_NUMBER() OVER (order by net_restored_investment)::integer AS id,
                ((net_restored_investment + expenses) - inversion_retirement) AS current_restored_inversion, 
	            (net_real_gain - expenses - gain_retirement) AS current_gain
        """

        from_clause = """
                FROM 
                (SELECT SUM(product_sale.restored_investment) AS net_restored_investment,
                        SUM(product_sale.real_gain) AS net_real_gain
                        FROM salescave_sale_product AS product_sale) AS purchase_table,
                (SELECT SUM(lot.total_expenses) AS expenses
                        FROM salescave_lot AS lot) AS lot_table,
                (SELECT SUM(salescave_general_retirement.value) AS gain_retirement
                        FROM salescave_general_retirement
                        WHERE take_from = 'gain') AS retirement_gain_table,
                (SELECT SUM(salescave_general_retirement.value) AS inversion_retirement
                        FROM salescave_general_retirement
                        WHERE take_from = 'inversion') AS retirement_inversion_table
        """

        expression = """
            %s
            %s
        """ % (
            select,
            from_clause,
        )

        query = """ 
                CREATE OR REPLACE VIEW salescave_general_balance_report AS (
                    %s
                );
        """ % (expression)

        return query

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)

        self.env.cr.execute(self._query())