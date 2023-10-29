# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Lot(models.Model):
    _name = 'salescave.lot'
    _description = 'Purchase lot'
    _order = 'purchase_date desc'

    purchase_date = fields.Date(string='Fecha de compra', required=True)

    product_purchases_ids = fields.One2many('salescave.product.purchase', 'lot_id',
                                            string='Compras')

    expenses_ids = fields.One2many('salescave.expense', 'lot_id',
                                   string='Gastos')

    sales_ids = fields.One2many('salescave.sale', 'lot_id',
                                string='Ventas')

    retirements_ids = fields.One2many('salescave.retirement', 'lot_id',
                                      string='Retiros')

    currency_id = fields.Many2one('res.currency', string='Moneda de compra')

    # compute fields
    expenses_by_lost = fields.Monetary(
        string='Gastos por perdidas', compute='_compute_expenses_by_lost')

    total_expenses = fields.Monetary(
        string='Gastos totales', compute='_compute_total_expenses', store=True)

    total_investment = fields.Monetary(
        string='Inversión total', compute='_compute_total_investment')

    total_investment_expenses = fields.Monetary(
        string='Total inversión/gastos', compute='_compute_total_investment_expenses')

    planned_total_sale_value = fields.Monetary(
        string='Total ganancia planificada', compute='_compute_planned_total_sale_value')

    real_total_sale_value = fields.Monetary(
        string='Total ganancia real', compute='_compute_real_total_sale_value')

    restored_investment = fields.Monetary(
        string='Inversión recuperada', compute='_compute_restored_investment')

    real_gain = fields.Monetary(
        string='Ganancia real', compute='_compute_restored_investment')

    total_debt = fields.Monetary(
        string='Total de deuda (en la calle)', compute='_compute_total_debt')

    total_inversion_retirements_value = fields.Monetary(
        string='Valor total de retiros de inversion', compute='_compute_total_inversion_retirements_value', store=True)

    total_gain_retirements_value = fields.Monetary(
        string='Valor total de retiros de inversion', compute='_compute_total_gain_retirements_value', store=True)

    total_retirements_value = fields.Monetary(
        string='Valor total de retiros', compute='_compute_total_retirements_value', store=True)

    @api.depends('product_purchases_ids')
    def _compute_expenses_by_lost(self):
        for record in self:
            products_lost = self.env['salescave.product.purchase'].search(
                [('quantity_lost', '>', 0), ('lot_id', '=', record.id)])
            lost_value = 0
            for product in products_lost:
                lost_value += product.quantity_lost * product.cost_x_product

            record.expenses_by_lost = lost_value

    @api.depends('expenses_ids', 'expenses_by_lost')
    def _compute_total_expenses(self):
        for record in self:
            total_expense = 0
            for expense in record.expenses_ids:
                total_expense += expense.value

            record.total_expenses = total_expense + record.expenses_by_lost

    @api.depends('product_purchases_ids')
    def _compute_total_investment(self):
        for record in self:
            total_investment = 0
            for purchase in record.product_purchases_ids:
                total_investment += purchase.total_cost

            record.total_investment = total_investment

    @api.depends('product_purchases_ids')
    def _compute_total_sale_value(self):
        for record in self:
            total_sale_value = 0
            for purchase in record.product_purchases_ids:
                total_sale_value += purchase.total_sale_price

            record.total_sale_value = total_sale_value

    @api.depends('total_investment', 'total_expenses')
    def _compute_total_investment_expenses(self):
        for record in self:
            record.total_investment_expenses = record.total_investment + record.total_expenses

    @api.depends('product_purchases_ids', 'total_expenses')
    def _compute_planned_total_sale_value(self):
        for record in self:
            planned_total_sale_value = 0
            for purchase in record.product_purchases_ids:
                planned_total_sale_value += purchase.planned_total_gain

            record.planned_total_sale_value = planned_total_sale_value - record.total_expenses

    @api.depends('product_purchases_ids')
    def _compute_restored_investment(self):
        for record in self:
            restored_investment = 0
            real_gain = 0
            for sale in record.product_purchases_ids:
                restored_investment += sale.restored_investment
                real_gain += sale.real_gain

            record.restored_investment = restored_investment
            record.real_gain = real_gain

    @api.depends('sales_ids.total_debt')
    def _compute_total_debt(self):
        for record in self:
            total_debt = 0
            for sale in record.sales_ids:
                total_debt += sale.total_debt

            record.total_debt = total_debt

    @api.depends('sales_ids.total_paid')
    def _compute_real_total_sale_value(self):
        for record in self:
            total_paid = 0
            for sale in record.sales_ids:
                total_paid += sale.total_paid

            record.real_total_sale_value = total_paid

    @api.depends('retirements_ids')
    def _compute_total_inversion_retirements_value(self):
        for record in self:
            total_inversion_retirements_value = 0
            for retirement in record.retirements_ids:
                if retirement.take_from == 'inversion':
                    total_inversion_retirements_value += retirement.value

            record.total_inversion_retirements_value = total_inversion_retirements_value

    @api.depends('retirements_ids')
    def _compute_total_gain_retirements_value(self):
        for record in self:
            total_gain_retirements_value = 0
            for retirement in record.retirements_ids:
                if retirement.take_from == 'gain':
                    total_gain_retirements_value += retirement.value

            record.total_gain_retirements_value = total_gain_retirements_value

    @api.depends('total_gain_retirements_value', 'total_inversion_retirements_value')
    def _compute_total_retirements_value(self):
        for record in self:
            record.total_retirements_value = record.total_gain_retirements_value + \
                record.total_inversion_retirements_value

    def name_get(self):
        result = []
        for record in self:
            rec_name = "Lote {}".format(record.purchase_date)
            result.append((record.id, rec_name))
        return result


class ProductPurchase(models.Model):
    _name = 'salescave.product.purchase'
    _description = 'Product purchase on a Lot'

    _sql_constraints = [
        ('positive_quantity', 'CHECK(quantity>0)',
         'La cantidad comprada del producto debe ser mayor que cero'),
        ('positive_cost_x_product', 'CHECK(cost_x_product>=0)',
         'El precio de compra por producto no puede ser negativo'),
        ('positive_cost_x_product', 'CHECK(cost_x_product>=0)',
         'El precio de venta por producto no puede ser negativo'),
        ('sales_price_higher_than_cost', 'CHECK(sale_price_x_product>cost_x_product)',
         'El precio de venta por producto debe ser mayor que el precio de compra'),
    ]

    lot_id = fields.Many2one('salescave.lot', string='Lote', ondelete='cascade')

    product_id = fields.Many2one(
        'salescave.product', string='Producto', required=True, ondelete='restrict')
    quantity = fields.Integer(string='Cantidad', default=1, required=True)
    quantity_lost = fields.Integer(
        string='Cantidad perdida', default=0, required=True)

    currency_id = fields.Many2one('res.currency', string='Moneda de compra')
    cost_x_product = fields.Monetary(
        string='Costo por producto', required=True)

    sale_price_x_product = fields.Monetary(
        string='Precio de venta por producto', required=True)

    sales_products_ids = fields.One2many('salescave.sale.product', 'product_purchase_id',
                                         string='Ventas productos')

    # compute field
    current_quantity = fields.Integer(
        string='Cantidad actual', compute='_compute_current_quantity', store=True)

    total_cost = fields.Monetary(
        string='Costo total', compute='_compute_total_cost', store=True)

    total_sale_price = fields.Monetary(
        string='Valor de venta total', compute='_compute_total_sale_price')

    planned_gain_x_product = fields.Monetary(
        string='Ganancia planificada por producto', compute='_compute_planned_gain_x_product')

    planned_total_gain = fields.Monetary(
        string='Ganancia total planificada', compute='_compute_planned_total_gain')

    restored_investment = fields.Monetary(
        string='Inversión recuperada', compute='_compute_restored_investment')

    real_gain = fields.Monetary(
        string='Ganancia real', compute='_compute_restored_investment')

    @api.depends('sales_products_ids.quantity', 'quantity', 'quantity_lost', 'sales_products_ids')
    def _compute_current_quantity(self):
        for record in self:
            quantity_sold = 0
            for sale in record.sales_products_ids:
                quantity_sold += sale.quantity

            record.current_quantity = record.quantity - quantity_sold - record.quantity_lost

    @api.depends('cost_x_product', 'quantity')
    def _compute_total_cost(self):
        for record in self:
            record.total_cost = record.cost_x_product * record.quantity

    @api.depends('sale_price_x_product', 'quantity')
    def _compute_total_sale_price(self):
        for record in self:
            record.total_sale_price = record.sale_price_x_product * record.quantity

    @api.depends('sale_price_x_product', 'cost_x_product')
    def _compute_planned_gain_x_product(self):
        for record in self:
            record.planned_gain_x_product = record.sale_price_x_product - record.cost_x_product

    @api.depends('planned_gain_x_product', 'quantity')
    def _compute_planned_total_gain(self):
        for record in self:
            record.planned_total_gain = record.planned_gain_x_product * record.quantity

    @api.depends('sales_products_ids.restored_investment', 'sales_products_ids.real_gain')
    def _compute_restored_investment(self):
        for record in self:
            restored_investment = 0
            real_gain = 0
            for sale in record.sales_products_ids:
                restored_investment += sale.restored_investment
                real_gain += sale.real_gain

            record.restored_investment = restored_investment
            record.real_gain = real_gain

    def name_get(self):
        result = []
        for record in self:
            rec_name = "{} {}".format(
                record.product_id.name, record.cost_x_product)
            result.append((record.id, rec_name))
        return result


class Expense(models.Model):
    _name = 'salescave.expense'
    _description = 'Lot expense'

    _sql_constraints = [
        ('positive_value', 'CHECK(value>0)',
         'El valor del gasto debe ser mayor que cero'),
    ]

    lot_id = fields.Many2one('salescave.lot', string='Lote', ondelete='cascade')

    name = fields.Char(string='Descripción del gasto', required=True)

    currency_id = fields.Many2one('res.currency', string='Moneda de compra')
    value = fields.Monetary(string='Valor del gasto', required=True)


class Retirement(models.Model):
    _name = 'salescave.retirement'
    _description = 'Lot money retirement'
    _order = 'date desc'

    _sql_constraints = [
        ('positive_value', 'CHECK(value>0)',
         'La cantidad del retiro debe ser mayor que cero'),
    ]

    lot_id = fields.Many2one('salescave.lot', string='Lote', ondelete='cascade')

    name = fields.Char(string='Descripción del retiro', required=True)
    date = fields.Date(string='Fecha del retiro', required=True)

    take_from_choices = [
        ('inversion', 'Inversión'),
        ('gain', 'Ganancia')
    ]

    take_from = fields.Selection(
        take_from_choices, string="Tomar de", required=True)

    destiny_choices = [
        ('inversion', 'Inversión'),
        ('others', 'Otros')
    ]

    destiny = fields.Selection(
        destiny_choices, string="Destino", required=True)

    currency_id = fields.Many2one('res.currency', string='Moneda de compra')
    value = fields.Monetary(string='Valor del retiro', required=True)
