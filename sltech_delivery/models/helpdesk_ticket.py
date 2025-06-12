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

class Machines(models.Model):
    _name = "sltech.machines"

    product_id = fields.Many2one('product.product', 'Product')
    qty = fields.Float('Quantity')
    helpdesk_id = fields.Many2one('helpdesk.ticket')
    serial_no_id = fields.Many2one('stock.production.lot')

    @api.onchange('serial_no_id')
    def sltech_serial_no_id(self):
        if self.serial_no_id:
            self.qty = 1

    @api.onchange('product_id')
    def sltech_product_id(self):
        serial_ids = self.env['stock.production.lot']
        if self.product_id:
            serial_ids = serial_ids.search([('product_id', '=', self.product_id.id)])

        return {
                'domain': {
                    'product_id': [('id', 'in', self.env['product.product'].search(
                        [('categ_id', 'in', [self.env.ref('sltech_delivery.Loan_Pull_Machine').id,
                                             self.env.ref('sltech_delivery.New_Machine').id,])]).ids)],
                    'serial_no_id': [('id', 'in', serial_ids.ids)]
                }}


class StockPicking(models.Model):
    _inherit = "helpdesk.ticket"

    picking_ids = fields.One2many('stock.picking', 'ticket_id')
    delivery_count = fields.Integer('Delivery Count', default=0, compute='compute_delivery_count')
    machine_ids = fields.One2many('sltech.machines', 'helpdesk_id', 'Machines')

    is_deliver = fields.Boolean(default=False)

    def sltech_action_deliver_items(self):

        if self.sparepart_ids:
            for line in self.sparepart_ids:
                if line.product_id and line.product_id.type == 'product' and line.qty_used > 0:
                    qty_info = line.product_id._product_available(False, False).get(line.product_id.id)
                    if qty_info['qty_available'] <= 0:
                        raise ValidationError('%s is not there in stock!' % line.product_id.name)
        if self.machine_ids:
            for line in self.machine_ids:
                if line.product_id and line.product_id.type == 'product' and line.qty > 0:
                    qty_info = line.product_id._product_available(False, False).get(line.product_id.id)
                    if qty_info['qty_available'] <= 0:
                        raise ValidationError('%s is not there in stock!' % line.product_id.name)


        if len(list(set([x.product_id.id for x in self.machine_ids]))) != len(
                [x.product_id.id for x in self.machine_ids]):
            raise ValidationError('Product Entry Must be unique in Machine Lines!')
        if len(list(set([x.product_id.id for x in self.sparepart_ids]))) != len(
                [x.product_id.id for x in self.sparepart_ids]):
            raise ValidationError('Product Entry Must be unique in Sparepart Lines!')

        if self.state == 'closed':
            move_ids_without_package = []
            move_ids_without_package_ret = []
            all_picking_ids = []
            for line in self.sparepart_ids:

                if line.state == 'required':
                    raise ValidationError('Please Check the status of spareparts used!')

                if line.product_id and line.product_id.type == 'product' and line.qty_used > 0:
                    if line.state == 'used':
                        move_ids_without_package.append((0, 0, {
                            'product_id': line.product_id.id,
                            'name': line.product_id.name,
                            'location_id': self.env.ref('stock.stock_location_stock').id,
                            'location_dest_id': self.env.ref('stock.stock_location_customers').id,

                            'company_id': self.env.user.company_id.id,
                            'product_uom': line.product_id.uom_po_id.id,
                            'product_uom_qty': line.qty_used,
                        }))
                    elif line.state == 'returned':
                        move_ids_without_package_ret.append((0, 0, {
                            'product_id': line.product_id.id,
                            'name': line.product_id.name,
                            'location_id': self.env.ref('stock.stock_location_stock').id,
                            'location_dest_id': self.env.ref('stock.stock_location_customers').id,

                            'company_id': self.env.user.company_id.id,
                            'product_uom': line.product_id.uom_po_id.id,
                            'product_uom_qty': line.qty_used,
                        }))

            for line in self.machine_ids:

                if line.product_id and line.product_id.type == 'product' and line.qty > 0:
                    move_ids_without_package.append((0, 0, {
                        'product_id': line.product_id.id,
                        'name': line.product_id.name,
                        'location_id': self.env.ref('stock.stock_location_stock').id,
                        'location_dest_id': self.env.ref('stock.stock_location_customers').id,

                        'company_id': self.env.user.company_id.id,
                        'product_uom': line.product_id.uom_po_id.id,
                        'product_uom_qty': line.qty,
                    }))

            if move_ids_without_package:
                picking_id = self.env['stock.picking'].create({
                    'location_id': self.env.ref('stock.stock_location_stock').id,
                    'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                    'company_id': self.env.user.company_id.id,
                    'name': self.ticket_no,
                    'picking_type_id': self.env.ref('stock.picking_type_out').id,
                    'move_type': 'direct',
                    'move_ids_without_package': move_ids_without_package,
                    'ticket_id': self.id
                })
                picking_id.action_confirm()
                picking_id.action_assign()

                total_pro_ids = [(x.serial_no_id.id, x.product_id.id) for x in self.machine_ids] + \
                                [(x.serial_no_id.id, x.product_id.id) for x in self.sparepart_ids]

                for ml_line in picking_id.move_line_ids_without_package:
                    serial_id = [x[0] for x in total_pro_ids if x[1] == ml_line.product_id.id][0]
                    if ml_line.lot_id.id != serial_id:
                        ml_line.lot_id = serial_id

                button_validate_res = picking_id.button_validate()
                if button_validate_res:
                    get_return_model_pick_return = self.env[button_validate_res['res_model']].search(
                        [('id', '=', button_validate_res['res_id'])])
                    if self._context.get('default_type'):
                        self = self.with_context(default_type='entry')
                    get_return_model_pick_return_process = get_return_model_pick_return.with_context(
                        default_type='entry').process()

                    if get_return_model_pick_return_process:
                        get_return_model_pick_return_backorder = self.env[
                            get_return_model_pick_return_process['res_model']].search(
                            [('id', '=', get_return_model_pick_return_process['res_id'])])
                all_picking_ids.append(picking_id)
            if move_ids_without_package_ret:
                picking_id = self.env['stock.picking'].create({
                    'location_id': self.env.ref('stock.stock_location_stock').id,
                    'location_dest_id': self.env.ref('stock.stock_location_suppliers').id,
                    'company_id': self.env.user.company_id.id,
                    'name': self.ticket_no + "-RET",
                    'picking_type_id': self.env.ref('stock.picking_type_out').id,
                    'move_type': 'direct',
                    'move_ids_without_package': move_ids_without_package_ret,
                    'ticket_id': self.id
                })
                picking_id.action_confirm()
                picking_id.action_assign()

                total_pro_ids = [(x.serial_no_id.id, x.product_id.id) for x in self.sparepart_ids]

                for ml_line in picking_id.move_line_ids_without_package:
                    serial_id = [x[0] for x in total_pro_ids if x[1] == ml_line.product_id.id][0]
                    if ml_line.lot_id.id != serial_id:
                        ml_line.lot_id = serial_id

                button_validate_res = picking_id.button_validate()
                if button_validate_res:
                    get_return_model_pick_return = self.env[button_validate_res['res_model']].search(
                        [('id', '=', button_validate_res['res_id'])])
                    if self._context.get('default_type'):
                        self = self.with_context(default_type='entry')
                    get_return_model_pick_return_process = get_return_model_pick_return.with_context(
                        default_type='entry').process()

                    if get_return_model_pick_return_process:
                        get_return_model_pick_return_backorder = self.env[
                            get_return_model_pick_return_process['res_model']].search(
                            [('id', '=', get_return_model_pick_return_process['res_id'])])
                all_picking_ids.append(picking_id)
            if all_picking_ids:
                self.is_deliver = True

    def compute_delivery_count(self):
        self.delivery_count = len(self.picking_ids.ids)

    def view_delivery_list(self):
        return {
            # 'view_id': self.env.ref('stock.vpicktree').id,
            'type': 'ir.actions.act_window',
            'name': _('Spare Parts Delivery'),
            'res_model': 'stock.picking',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.picking_ids.ids)]
        }

    # @api.constrains('state')
    # def compute_closed_status_ticket(self):
    #     if self.state == 'closed':
    #         if self.sparepart_ids:
    #             for line in self.sparepart_ids:
    #                 if line.product_id and line.product_id.type == 'product' and line.qty_used > 0:
    #                     qty_info = line.product_id._product_available(False, False).get(line.product_id.id)
    #                     if qty_info['qty_available'] <= 0:
    #                         raise ValidationError('%s is not there in stock!' % line.product_id.name)
    #         if self.machine_ids:
    #             for line in self.machine_ids:
    #                 if line.product_id and line.product_id.type == 'product' and line.qty > 0:
    #                     qty_info = line.product_id._product_available(False, False).get(line.product_id.id)
    #                     if qty_info['qty_available'] <= 0:
    #                         raise ValidationError('%s is not there in stock!' % line.product_id.name)

class use_spareparts(models.Model):
    _inherit = "use.spareparts"

    serial_no_id = fields.Many2one('stock.production.lot')

    @api.onchange('product_id')
    def sltech_product_id(self):
        serial_ids = self.env['stock.production.lot']
        if self.product_id:
            serial_ids = serial_ids.search([('product_id', '=', self.product_id.id)])

        return {
            'domain': {
                'serial_no_id': [('id', 'in', serial_ids.ids)]
            }}