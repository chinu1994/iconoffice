# -*- coding: utf-8 -*-
##############################################################################
#
#    SLTECH ERP SOLUTION
#    Copyright (C) 2020-Today(www.slecherpsolution.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, api, fields, _
from odoo.tools.float_utils import float_round
from datetime import datetime
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp

class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    sltech_mono = fields.Char('Mono')
    sltech_color = fields.Char('Color')
    sltech_product_categ_id = fields.Many2one('product.category', 'Product Category')
    vendor_id = fields.Many2one('sltech.purchase.vendor', 'Inventory Reference')