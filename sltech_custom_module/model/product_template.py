# -*- coding: utf-8 -*-
##############################################################################
#
#    SLTECH ERP SOLUTION
#    Copyright (C) 2022-Today(www.slecherpsolution.com).
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

from odoo import models, tools, fields, api, _


class GenerateInvoice(models.TransientModel):
    _name = 'sltech.generate.invoice'
    _description = 'Sltech Generate Invoice'

    partner_id = fields.Many2one('res.partner', string='Customer Name', required=True,)
    sltech_months = fields.Selection([
        ('jan', 'January'),
        ('feb', 'February'),
        ('mar', 'March'),
        ('apr', 'April'),
        ('may', 'May'),
        ('jun', 'June'),
        ('jul', 'July'),
        ('aug', 'August'),
        ('sep', 'September'),
        ('oct', 'October'),
        ('nov', 'November'),
        ('dec', 'December'),
    ], string='Month', required=True,)

    sltech_years = fields.Char(string='Year', required=True,)

    def generate_invoice(self):
        active_ids = self._context.get('active_ids', []) or []
        helpdesk_invoice_line_ids = self.env['helpdesk.invoice.line'].browse(active_ids)
        data1=[]
        # data2=[]
        for helpdesk in helpdesk_invoice_line_ids:
            data1.append((0, 0, {'product_id': helpdesk.product_id.id,
                                 'name': helpdesk.description,
                                 'price_unit': helpdesk.unit_price,
                                 'invoice_line_tax_ids': [(6, 0, helpdesk.inv_tax.ids)],
                                 'quantity': helpdesk.qty,
                                 'account_id': helpdesk.product_id.categ_id.property_account_income_categ_id.id or helpdesk.product_id.property_account_income_id.id
                                 }))

        data3=[]
        if data1:
            consolidated_invoice_line = ",".join(set(helpdesk_invoice_line_ids.mapped('ticket_title')))
            account_invoice_create = self.env['account.invoice'].sudo().create({
                'partner_id': self.partner_id.id,
                'type':'out_invoice',
                'sltech_months': self.sltech_months,
                'sltech_years':self.sltech_years,
                'invoice_line_ids':data1,
                'consolidated_invoice_line': consolidated_invoice_line,
                'helpdesk_inv_ids': [(6,0,helpdesk_invoice_line_ids.ids)],
                'ticket_title' : consolidated_invoice_line

            })
            data3.append(account_invoice_create.id)

        form_view = self.env.ref('account.invoice_form')
        tree_view = self.env.ref('account.invoice_tree_with_onboarding')
        return {
            'name': _('Generate Invoice'),
            'res_model': 'account.invoice',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', data3)],
            'views': [
            (tree_view.id, 'tree'),
            (form_view.id, 'form'),
            ],
            'type': 'ir.actions.act_window',
        }
