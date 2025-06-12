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

class StockInventory(models.Model):
    _inherit = "stock.inventory"

    machine_type = fields.Selection([('loan_pull_machime', 'Loan Pool Machine'),
                                     ('new_machine', 'New Machine')])

    name = fields.Char(
        'Inventory Reference',
        readonly=True, required=False,
        states={'draft': [('readonly', False)]})

    vendor_id = fields.Many2one('sltech.purchase.vendor', 'Vendor', required=True)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['sltech.purchase.vendor'].browse(vals['vendor_id']).name
        return super(StockInventory, self).create(vals)

    def action_import_bulk(self):
        return {
            # 'view_id': self.env.ref('stock.vpicktree').id,
            'type': 'ir.actions.act_window',
            'name': _('Import File'),
            'res_model': 'sltech.import.excel',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            # 'domain': [('id', 'in', self.picking_ids.ids)]
        }

class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    product_qty = fields.Float(
        'Checked Quantity',
        digits=dp.get_precision('Product Unit of Measure'), default=1)

    @api.onchange('prod_lot_id')
    def sltech_prod_lot_id(self):
        if self.prod_lot_id:
            self.product_qty = 1

    @api.onchange('product_id')
    def sltech_product_id(self):
        if self.inventory_id.machine_type == 'loan_pull_machime':
            return {
                'domain': {
                    'product_id':[('id', 'in', self.env['product.product'].search(
                       [('categ_id', '=', self.env.ref('sltech_delivery.Loan_Pull_Machine').id)]).ids)]
                }}
        elif self.inventory_id.machine_type == 'new_machine':
            return {
                'domain': {
                    'product_id': [('id', 'in', self.env['product.product'].search(
                        [('categ_id', '=', self.env.ref('sltech_delivery.New_Machine').id)]).ids)]
                }}
