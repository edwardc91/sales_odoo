# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

import logging
import json


_logger = logging.getLogger(__name__)


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

    @api.depends('sales_products_ids.total_sale', 'sales_products_ids')
    def _compute_total_sale(self):
        for record in self:
            total_sale = 0
            for sale in record.sales_products_ids:
                total_sale += sale.total_sale

            record.total_sale = total_sale

    @api.depends('sales_products_ids.total_gain', 'sales_products_ids')
    def _compute_total_gain(self):
        for record in self:
            total_gain = 0
            for sale in record.sales_products_ids:
                total_gain += sale.total_gain

            record.total_gain = total_gain

    @api.depends('sales_products_ids.total_paid', 'sales_products_ids')
    def _compute_total_paid(self):
        for record in self:
            total_paid = 0
            for sale in record.sales_products_ids:
                total_paid += sale.total_paid

            record.total_paid = total_paid

    @api.depends('sales_products_ids', 'sales_products_ids.debt')
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
        ('unique_together_sale_product', 'UNIQUE(sale_id, product_purchase_id)',
         'No puede existir mas de una venta para un mismo producto')
    ]

    sale_id = fields.Many2one('salescave.sale', string='Venta')

    lot_integer_id = fields.Integer(
        'Lote ID',
        related='sale_id.lot_id.id',
        readonly=True)

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

    gain_x_product = fields.Monetary(
        string='Ganancia por producto', compute='_compute_gain_x_product')

    total_gain = fields.Monetary(
        string='Ganancia total', compute='_compute_total_gain')

    total_paid = fields.Monetary(
        string='Total pagado', compute='_compute_total_paid')

    debt = fields.Monetary(
        string='Deuda', compute='_compute_debt', store=True)

    restored_investment = fields.Monetary(
        string='Inversión recuperada', compute='_compute_restored_investment', store=True)

    real_gain = fields.Monetary(
        string='Ganancia real', compute='_compute_restored_investment', store=True)

    # Compute methods
    # @api.depends('sale_id')
    # def _compute_product_purchase_id_domain(self):
    #     for rec in self:
    #         _logger.debug(
    #             'Updating product_purchase_id domain for lot %s', rec.sale_id.lot_id.purchase_date)
    #         new_domain = json.dumps(
    #             [('lot_id', '=', rec.sale_id.lot_id.id), ('current_quantity', '>', 0)])
    #         _logger.debug('Updating domain value with %s', new_domain)

    #         rec.product_purchase_id_domain = new_domain

    @api.depends('sale_price_x_product', 'quantity')
    def _compute_total_sale(self):
        for record in self:
            record.total_sale = record.sale_price_x_product * record.quantity

    @api.depends('sale_price_x_product', 'product_purchase_id', 'product_purchase_id.cost_x_product')
    def _compute_gain_x_product(self):
        for record in self:
            gain_x_product = 0
            if record.product_purchase_id:
                gain_x_product = record.sale_price_x_product - \
                    record.product_purchase_id.cost_x_product

            record.gain_x_product = gain_x_product

    @api.depends('total_sale', 'product_purchase_id', 'quantity', 'product_purchase_id.cost_x_product')
    def _compute_total_gain(self):
        for record in self:
            total_gain = 0
            if record.product_purchase_id:
                total_gain = record.total_sale - \
                    (record.product_purchase_id.cost_x_product * record.quantity)

            record.total_gain = total_gain

    @api.depends('payments_ids', 'payments_ids.payment')
    def _compute_total_paid(self):
        for record in self:
            total_paid = 0
            for payment in record.payments_ids:
                total_paid += payment.payment

            record.total_paid = total_paid

    @api.depends('total_paid', 'total_sale')
    def _compute_debt(self):
        for record in self:
            total_sale = record.total_sale if record.total_sale else 0
            total_paid = record.total_paid if record.total_paid else 0
            record.debt = total_sale - total_paid

    @api.depends('total_paid', 'gain_x_product', 'product_purchase_id')
    def _compute_restored_investment(self):
        for record in self:
            quantity = record.quantity
            rest = record.total_paid if record.total_paid else 0
            restored_investment = 0
            real_gain = 0
            cost_x_product = record.product_purchase_id.cost_x_product
            gain_x_product = record.gain_x_product
            while quantity > 0 and rest > 0:
                if rest >= cost_x_product:
                    restored_investment += cost_x_product
                    rest -= cost_x_product
                    if rest >= gain_x_product:
                        real_gain += gain_x_product
                        rest -= gain_x_product
                    else:
                        real_gain += rest
                        rest = 0
                else:
                    restored_investment += rest
                    rest = 0

                quantity -= 1

            # if quantity == 0 and rest > 0:
            #     real_gain += rest

            record.restored_investment = restored_investment
            record.real_gain = real_gain

    # checks and validations
    def _check_quantity(self, values):
        if "quantity" in values:
            new_quantity = values["quantity"]

            if "product_purchase_id" in values:
                purchase = self.env['salescave.product.purchase'].browse(
                    values["product_purchase_id"])
            else:
                purchase = self.product_purchase_id

            if new_quantity > purchase.current_quantity:
                raise ValidationError(
                    'La cantidad de {}(s) excede las existencias del producto.'.format(
                        purchase.product_id.name)
                )

    @api.model
    def create(self, values):
        # checks and validations
        # self._check_quantity(values)

        return super(SaleProduct, self).create(values)

    @api.model
    def write(self, values):
        # checks and validations
        # self._check_quantity(values)

        return super(SaleProduct, self).write(values)


class SalePayment(models.Model):
    _name = 'salescave.sale.payment'
    _description = 'Buyer sale for a Lot'
    _order = 'payment_date desc'

    _sql_constraints = [
        ('positive_payment', 'CHECK(payment>0)',
         'La cantidad vendida del producto debe ser mayor que cero'),
    ]

    sale_product_id = fields.Many2one(
        'salescave.sale.product', string='Venta/Producto')
    payment_date = fields.Date(string='Fecha de venta', required=True)

    currency_id = fields.Many2one('res.currency', string='Moneda de venta')
    payment = fields.Monetary(
        string='Cantidad pago', required=True)
