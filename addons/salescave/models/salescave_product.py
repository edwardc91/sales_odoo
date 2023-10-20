# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Product(models.Model):
    _name = 'salescave.product'
    _description = 'Product purchased to set on sale'

    name = fields.Char(string="Nombre del product", required=True)
    image = fields.Binary(string='Imagen')
    description = fields.Text(string="Descripción")

