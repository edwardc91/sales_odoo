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

    sale_id = fields.Many2one(
        'salescave.product.purchase', string='Venta', required=True)
    quantity = fields.Integer(
        string='Cantidad vendida', default=1, required=True)

    currency_id = fields.Many2one('res.currency', string='Moneda de compra')
    sale_price_x_product = fields.Monetary(
        string='Precio venta por producto', required=True)

    payments_ids = fields.One2many('salescave.sale.payment', 'sale_product_id',
                                   string='Pagos')


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

    currency_id = fields.Many2one('res.currency', string='Moneda de compra')
    payment = fields.Monetary(
        string='Precio venta por producto', required=True)
