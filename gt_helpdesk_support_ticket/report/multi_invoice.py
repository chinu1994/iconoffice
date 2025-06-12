# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
import time
from openerp.exceptions import UserError, ValidationError
#from datetime import  timedelta
from dateutil.relativedelta import relativedelta
from datetime import date
from calendar import monthrange
from datetime import date
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _
from odoo.exceptions import UserError, AccessError
import itertools

class Multi_Invoice_data(models.TransientModel):
    _name = "multi.invoice"
    _description = "Sales Advance Payment Invoice"

    @api.multi
    def active_count(self):
        active_model = self._context.get('active_model', False)
        if active_model and active_model == 'helpdesk.ticket':
            hp_line = self.env['helpdesk.ticket'].search([('id', 'in', self._context.get('active_ids', []))])
        elif active_model and active_model == 'helpdesk.invoice.line':
            ticket_invoice_lines = self.env['helpdesk.invoice.line'].search([('id', 'in', self._context.get('active_ids', []))])
            temp_hp_line_ids = list(set([t_inv_line.helpdesk_inv_ids.id for t_inv_line in ticket_invoice_lines if t_inv_line.helpdesk_inv_ids]))
            hp_line = self.env['helpdesk.ticket'].browse(temp_hp_line_ids)
        # dt_date = str(hp_line.create_date)
        dt_date = datetime.now()
        rec_date = dt_date.replace(second=0, microsecond=0)
        final_date = datetime.strptime(str(rec_date), "%Y-%m-%d %H:%M:%S").date()
        invoice_obj = self.env['account.invoice']

        inv_fields = invoice_obj.fields_get()
        default_value = invoice_obj.default_get(inv_fields)

        invoice_line = self.env['account.invoice.line']
        line_f = invoice_line.fields_get()
        default_line = invoice_line.default_get(line_f)
        default_value.update({'partner_id': self.env.user.company_id.partner_id.id, 'date_invoice': final_date,
                              'user_id': self.env.user.id})

        invoice = invoice_obj.new(default_value)
        invoice._onchange_partner_id()
        default_value.update({'account_id': invoice.account_id.id, 'date_due': invoice.date_due})
        inv_id = invoice.create(default_value)
        invoicing_lines = []
        store_tktInvLines = []


        for desk_lines in hp_line:

            if desk_lines.state != 'closed':
                raise ValidationError('%s ticket\'s state is %s \n Invoice can be generated only for closed tickets!' % (desk_lines.ticket_no, desk_lines.state))
                continue

            check_inv_id = invoice_obj.search([])
            get_all_tkt_inv_lines_invce = []
            for inv_chk in check_inv_id:
                get_all_tkt_inv_lines_invce.append(inv_chk.ticket_inv_line_ids.ids)
            get_all_tkt_inv_lines_invce = list(itertools.chain(*get_all_tkt_inv_lines_invce))
            if active_model and active_model == 'helpdesk.invoice.line':
                chain_list = [[res for res in self._context.get('active_ids', []) if res == rec] for rec in
                              get_all_tkt_inv_lines_invce]
                if list(itertools.chain(*chain_list)):
                    raise ValidationError('%s ticket has already invoice created!' % (desk_lines.ticket_no))
                    break

            elif active_model == 'helpdesk.ticket':
                chain_list = [[res for res in desk_lines.tsk_inv_line_ids.ids if res == rec] for rec in
                              get_all_tkt_inv_lines_invce]
                if len(list(itertools.chain(*chain_list))) == len(desk_lines.tsk_inv_line_ids.ids):
                    raise ValidationError('%s ticket has already invoice created!' % (desk_lines.ticket_no))
                    break



            # inv_fields = invoice_obj.fields_get()
            # default_value = invoice_obj.default_get(inv_fields)
            #
            # invoice_line = self.env['account.invoice.line']
            # line_f = invoice_line.fields_get()
            # default_line = invoice_line.default_get(line_f)
            # default_value.update({'partner_id': desk_lines.customer.id, 'date_invoice': final_date,
            #                       'user_id': desk_lines.assi_to.id})
            #
            #
            # invoice = invoice_obj.new(default_value)
            # invoice._onchange_partner_id()
            # default_value.update({'account_id': invoice.account_id.id, 'date_due': invoice.date_due})
            # inv_id = invoice.create(default_value)



            #Sachin Burnawal
            # inv_id.ticket_id = desk_lines.id

            for invce_lst in desk_lines.tsk_inv_line_ids:
                if active_model and active_model == 'helpdesk.invoice.line':
                    if invce_lst.id not in self._context.get('active_ids', []):
                        continue
                else:
                    ticket_invline_line_ids = [invce.ticket_inv_line_ids.ids for invce in inv_id.search([])]
                    if invce_lst.id in list(itertools.chain(*ticket_invline_line_ids)):
                        continue
                    store_tktInvLines.append(invce_lst.id)
                invce_lst.status = True
                tax_ids = [tax.id for tax in invce_lst.inv_tax]
                invoicing_lines.append({
                    'invoice_id': inv_id.id,
                    'product_id': invce_lst.product_id.id,
                    'name': desk_lines.ticket_no,
                    'account_analytic_id': invce_lst.ac_analytic_id.id,
                    'quantity': invce_lst.qty,
                    'price_unit': invce_lst.unit_price,
                    # 'account_analytic_id': invoice_lst.ac_analytic_id.id,
                    'invoice_line_tax_ids': tax_ids,
                })
            for parts_line in desk_lines.sparepart_ids:
                tax_ids = [tax.id for tax in parts_line.product_id.taxes_id]
                invoicing_lines.append({
                    'invoice_id': inv_id.id,
                    'product_id': parts_line.product_id.id,
                    'name': desk_lines.ticket_no,
                    'account_analytic_id': False,
                    'quantity': parts_line.qty_used,
                    'price_unit': parts_line.product_id.list_price,
                    # 'account_analytic_id': invoice_lst.ac_analytic_id.id,
                    'invoice_line_tax_ids': tax_ids,
                })
        for invoice_lst in invoicing_lines:
            # tax_ids = [tax.id for tax in invoice_lst.inv_tax]
            # print "::::::::::::::::::::::::::::::::::::taxess:::::::",tax_ids
            default_line.update({
                'invoice_id': inv_id.id,
                'product_id': invoice_lst['product_id'],
                'name': invoice_lst['name'],
                'account_analytic_id': invoice_lst['account_analytic_id'],
                'quantity': invoice_lst['quantity'],
                'price_unit': invoice_lst['price_unit'],
                # 'account_analytic_id': invoice_lst.ac_analytic_id.id,
                'invoice_line_tax_ids': [(6, 0, invoice_lst['invoice_line_tax_ids'])],
            })
            inv_line = invoice_line.new(default_line)
            inv_line._onchange_product_id()
            default_line.update({'invoice_id': inv_id.id,
                                 'account_id': inv_line.with_context(
                                     {'journal_id': inv_id.journal_id.id})._default_account()})

            invoice_line.create(default_line)

        inv_id.amount_tax = sum([sum([(sum([tax.amount for tax in line.invoice_line_tax_ids]) * line.price_subtotal)/100]) for line in inv_id.invoice_line_ids])
        inv_id.amount_total = inv_id.amount_tax + sum([line.price_subtotal for line in inv_id.invoice_line_ids])

        desk_lines = desk_lines.with_context(stop_update=True)
        desk_lines.invoice_id = inv_id.id
        if active_model and active_model == 'helpdesk.invoice.line':
            inv_id.ticket_inv_line_ids = [(6, 0, self._context.get('active_ids', []))]
        else:
            inv_id.ticket_inv_line_ids = [(6, 0, store_tktInvLines)]



                # inv_id.action_invoice_open()
                #
                # template_obj = self.env.ref('account.email_template_edi_invoice', False)
                # template_obj.send_mail(inv_id.id)
            #End










            # for invoice_lst in desk_lines.tsk_inv_line_ids:
            #     tax_ids = [tax.id for tax in invoice_lst.inv_tax]
            #     default_line.update({
            #         'invoice_id': inv_id.id,
            #         'product_id': invoice_lst.product_id.id,
            #         'name': invoice_lst.description,
            #         # 'account_analytic_id': invoice_lst.ac_analytic_id.id,
            #         'quantity': invoice_lst.qty,
            #         'price_unit': invoice_lst.unit_price,
            #         # 'account_analytic_id': invoice_lst.ac_analytic_id.id,
            #         'invoice_line_tax_ids': [(6, 0, tax_ids)],
            #
            #     })
            #     inv_line = invoice_line.new(default_line)
            #     inv_line._onchange_product_id()
            #     default_line.update({'invoice_id': inv_id.id,
            #                          'account_id': inv_line.with_context(
            #                          {'journal_id': inv_id.journal_id.id})._default_account()})
            #
            #     invoice_line.create(default_line)
                # inv_id.action_invoice_open()




