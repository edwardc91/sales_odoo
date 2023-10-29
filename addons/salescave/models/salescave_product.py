# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Product(models.Model):
    _name = 'salescave.product'
    _description = 'Product purchased to set on sale'
    _order = 'name asc'

    name = fields.Char(string="Nombre del producto", required=True)
    image = fields.Binary(string='Imagen')
    description = fields.Text(string="Descripción")