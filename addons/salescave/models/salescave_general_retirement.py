# -*- coding: utf-8 -*-

from odoo import models, fields, api


class GeneralRetirement(models.Model):
    _name = 'salescave.general.retirement'
    _description = 'Retirement of money'
    _order = 'date desc'

    _sql_constraints = [
        ('positive_value', 'CHECK(value>0)',
         'La cantidad del retiro debe ser mayor que cero'),
    ]

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