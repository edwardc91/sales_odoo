# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Sale(models.Model):
    _name = 'salescave.sale'
    _description = 'Buyer sale for a Lot'
    _order = 'sale_date desc'

    lot_id = fields.Many2one('salescave.lot', string='Lote')
    buyer_id = fields.Many2one('res.partner', string='Comprador')
    sale_date = fields.Date(string='Fecha de venta', required=True)
    
    sales_products_ids = fields.One2many('salescave.sale.product', 'sale_id',
                                   string='Ventas/Productos')
    
    currency_id = fields.Many2one('res.currency', string='Moneda de venta')
    # compute fields
    total_sale = fields.Monetary(
        string='Valor total de la venta', compute='_compute_total_sale')
    
    total_gain = fields.Monetary(
        string='Inversión total', compute='_compute_total_gain')
    
    total_paid = fields.Monetary(
        string='Total pagado (en caja)', compute='_compute_total_paid')
    
    total_debt = fields.Monetary(
        string='Total de deuda (en la calle)', compute='_compute_total_debt')
    
    @api.depends('sales_products_ids')
    def _compute_total_sale(self):
        for record in self:
            total_sale = 0
            for sale in record.sales_products_ids:
                total_sale += sale.total_sale
                
            record.total_sale = total_sale
            
    @api.depends('sales_products_ids')
    def _compute_total_gain(self):
        for record in self:
            total_gain = 0
            for sale in record.sales_products_ids:
                total_gain += sale.total_gain
                
            record.total_gain = total_gain
            
    @api.depends('sales_products_ids')
    def _compute_total_paid(self):
        for record in self:
            total_paid = 0
            for sale in record.sales_products_ids:
                total_gain += sale.total_paid
                
            record.total_paid = total_paid
            
    @api.depends('sales_products_ids')
    def _compute_total_debt(self):
        for record in self:
            total_debt = 0
            for sale in record.sales_products_ids:
                total_debt += sale.debt
                
            record.total_debt = total_debt


class SaleProduct(models.Model):
    _name = 'salescave.sale.product'
    _description = 'Buyer sale for a Lot'

    _sql_constraints = [
        ('positive_quantity', 'CHECK(quantity>0)',
         'La cantidad vendida del producto debe ser mayor que cero'),
    ]

    sale_id = fields.Many2one('salescave.sale', string='Venta')
    buyer_id = fields.Many2one('res.partner', string='Comprador', domain=[
                               ('is_company', '=', False)], required=True)

    product_purchase_id = fields.Many2one(
        'salescave.product.purchase', string='Venta', required=True)
    quantity = fields.Integer(
        string='Cantidad vendida', default=1, required=True)

    currency_id = fields.Many2one('res.currency', string='Moneda de venta')
    sale_price_x_product = fields.Monetary(
        string='Precio venta por producto', required=True)

    payments_ids = fields.One2many('salescave.sale.payment', 'sale_product_id',
                                   string='Pagos')
    
    # compute fields
    total_sale = fields.Monetary(
        string='Valor total de la venta', compute='_compute_total_sale')
    
    total_gain = fields.Monetary(
        string='Ganancia total', compute='_compute_total_gain')
    
    total_paid = fields.Monetary(
        string='Total pagado', compute='_compute_total_paid')
    
    debt = fields.Monetary(
        string='Deuda', compute='_compute_debt')
    
    
    @api.depends('sale_price_x_product', 'quantity')
    def _compute_total_sale(self):
        for record in self:
            record.total_sale = record.sale_price_x_product * record.quantity
            
    @api.depends('total_sale', 'product_purchase_id')
    def _compute_total_gain(self):
        for record in self:
            if record.product_purchase_id:
                record.total_gain = record.total_sale - (record.product_purchase_id.cost_x_product * record.quantity)
                
    @api.depends('payments_ids')
    def _compute_total_paid(self):
        for record in self:
            total_paid = 0
            for payment in record.payments_ids:
                total_paid += payment.payment
                
            record.total_paid = total_paid
            
    @api.depends('total_paid', 'total_sale')
    def _compute_debt(self):
        for record in self:     
            record.total_debt = record.total_sale - record.total_paid


class SalePayment(models.Model):
    _name = 'salescave.sale.payment'
    _description = 'Buyer sale for a Lot'
    _order = 'payment_date desc'

    _sql_constraints = [
        ('positive_quantity', 'CHECK(quantity>0)',
         'La cantidad vendida del producto debe ser mayor que cero'),
    ]

    sale_product_id = fields.Many2one(
        'salescave.sale.product', string='Venta/Producto')
    payment_date = fields.Date(string='Fecha de venta', required=True)

    currency_id = fields.Many2one('res.currency', string='Moneda de venta')
    payment = fields.Monetary(
        string='Precio venta por producto', required=True)
