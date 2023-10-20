# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Buyer(models.Model):
    _name = 'salescave.buyer'
    _description = 'Buyer of products'

    name = fields.Char(string="Nombre del comprador", required=True)
    phone = fields.Char(string="Número de teléfono")
    address1 = fields.Char(string="Dirección")
    address2 = fields.Char(string="Dirección")