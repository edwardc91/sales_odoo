# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Lot(models.Model):
    _name = 'salescave.lot'
    _description = 'Purchase lot'

    purchase_date = fields.Date(string='Fecha de compra', required=True)

    product_purchases_ids = fields.One2many('salescave.product.purchase', 'lot_id',
                                            string='Compras')

    expenses_ids = fields.One2many('salescave.pexpense', 'lot_id',
                                   string='Gastos')

    currency_id = fields.Many2one('res.currency', string='Moneda de compra')
    
    # compute fields
    total_expenses = fields.Monetary(
        string='Total expenses', compute='_compute_total_expenses')
    
    total_investment = fields.Monetary(
        string='Total investment', compute='_compute_total_investment')
    
    planned_total_sale_value = fields.Monetary(
        string='Total investment', compute='_compute_planned_total_sale_value')
    
    @api.depends('expenses_ids')
    def _compute_total_expenses(self):
        for record in self:
            total_expense = 0
            for expense in record.expenses_ids:
                total_expense += expense.value
                
            record.total_expenses = total_expense
            
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
            
    @api.depends('product_purchases_ids')
    def _compute_planned_total_sale_value(self):
        for record in self:
            planned_total_sale_value = 0
            for purchase in record.product_purchases_ids:
                planned_total_sale_value += purchase.planned_total_gain
                
            record.planned_total_sale_value = planned_total_sale_value


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

    lot_id = fields.Many2one('salescave.lot', string='Lote')

    product_id = fields.Many2one(
        'salescave.product', string='Producto', required=True)
    quantity = fields.Integer(string='Cantidad', default=1, required=True)

    currency_id = fields.Many2one('res.currency', string='Moneda de compra')
    cost_x_product = fields.Monetary(
        string='Costo por producto', required=True)
    
    sale_price_x_product = fields.Monetary(
        string='Precio de venta por producto', required=True)
    
    # compute field
    total_cost = fields.Monetary(
        string='Costo total', compute='_compute_total_cost')
    
    total_sale_price = fields.Monetary(
        string='Valor de venta total', compute='_compute_total_sale_price')
    
    planned_gain_x_product = fields.Monetary(
        string='Valor de venta total', compute='_compute_planned_gain_x_product')
    
    planned_total_gain = fields.Monetary(
        string='Valor de venta total', compute='_compute_planned_total_gain')

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
            
    @api.depends('gain_x_product', 'quantity')
    def _compute_planned_total_gain(self):
        for record in self:
            record.planned_total_gain = record.planned_gain_x_product * record.quantity
            
    def name_get(self):
        result = []
        for record in self:
            rec_name = record.product_id.name
            result.append((record.id, rec_name))
        return result


class Expense(models.Model):
    _name = 'salescave.expense'
    _description = 'Lot expense'

    _sql_constraints = [
        ('positive_value', 'CHECK(value>0)',
         'El valor del gasto debe ser mayor que cero'),
    ]

    lot_id = fields.Many2one('salescave.lot', string='Lote')

    description = fields.Text(string='Descripción del gasto', required=True)

    currency_id = fields.Many2one('res.currency', string='Moneda de compra')
    value = fields.Monetary(string='Valor del gasto', required=True)
