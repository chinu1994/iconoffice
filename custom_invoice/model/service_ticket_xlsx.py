from odoo import models
import base64
import io
import logging
import requests
import werkzeug.utils

from PIL import Image
from odoo import http, tools, _
from odoo.http import request
from werkzeug.urls import url_encode
import json
from odoo import models, tools, fields, api, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime, date, timedelta

class ServiceTicketReport(models.TransientModel):
    _name = "helpdesk.ticket.report"

    name = fields.Char()
    type = fields.Selection([('custom', 'Custom Dates'),
                             ('today', 'Today'),
                             ('yesterday', 'Yesterday'),
                             ('last_week', 'Last Week'),
                             ('last_month', 'Last Month')], default='custom', string="Type")
    from_date = fields.Date('From date')
    to_date = fields.Date('To date')

    ticket_inv_line_ids = fields.Many2many('helpdesk.invoice.line', 'report_helpdesk_rel', 'report_id', 'ticket_id', 'Tickets')
    product_id = fields.Many2one('product.product', 'Product')

    @api.onchange('type', 'from_date', 'to_date', 'product_id')
    def populate_data(self):
        if not self.type:
            return
        if self.type == 'custom' and not (self.from_date and self.to_date):
            return
        self.ticket_inv_line_ids = [(6, 0, self.get_ticket_ids().ids)]

    def get_ticket_ids(self):

        from_date = ''
        to_date = ''

        if self.from_date and self.to_date:
            from_date = self.from_date
            to_date = self.to_date

        if self.type == 'today':
            from_date = date.today() + timedelta(days=-1)
            to_date = date.today() + timedelta(days=1)

        if self.type == 'yesterday':
            from_date = date.today() + timedelta(days=-2)
            to_date = date.today()

        if self.type == 'last_week':
            from_date = date.today() + timedelta(days=-8)
            to_date = date.today()

        if self.type == 'last_month':
            from_date = date.today() + timedelta(days=-32)
            to_date = date.today()

        ticket_inv_line_ids = self.env['helpdesk.invoice.line'].search([('helpdesk_inv_ids', '!=', False)])
        if self.product_id:
            ticket_inv_line_ids = self.env['helpdesk.invoice.line'].search([('product_id', '=', self.product_id.id),
                                                                            ('helpdesk_inv_ids', '!=', False)])
        ticket_inv_line_ids = ticket_inv_line_ids.filtered(
            lambda self: str(self.create_date.date()) > str(from_date) and str(
                self.create_date.date()) < str(to_date))

        return ticket_inv_line_ids

    def check_dates(self):
        if self.type == 'custom':
            if not self.from_date or not self.to_date or self.from_date > self.to_date:
                raise ValidationError('Please Select Valid Date Range!')
        return False
        pass

    def generate_report_pdf(self):
        if self.check_dates():
            return
        return dict(
            context=dict(type=self.type, from_date=self.from_date, to_date=self.to_date),
            report_name='custom_invoice.service_ticket_pdf',
            report_type='qweb-pdf',
            type='ir.actions.report',
        )
        pass

    def generate_report_xlsx(self):
        if self.check_dates():
            return
        return dict(
            context=dict(type=self.type, from_date=self.from_date, to_date=self.to_date, product_id=self.product_id.id),
            report_name='custom_invoice.service_ticket_xlsx',
            report_type='xlsx',
            type='ir.actions.report',
        )
        pass

class IconOffice(models.AbstractModel):
    _name = 'report.custom_invoice.service_ticket_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        if data.get('data', False):
            report_data = json.loads(data['data'])
            if isinstance(report_data, list) and len(report_data) > 1:
                report_data = json.loads(data['data'])[2]
                if len(report_data) > 0:
                    report_data = json.loads(data['data'])[2][0]

                    from_date = ''
                    to_date = ''

                    if report_data.get('from_date', False) and report_data.get('to_date', False):
                        from_date = report_data.get('from_date', False)
                        to_date = report_data.get('to_date', False)

                    if report_data.get('type', False) and report_data.get('type', False) == 'today':
                        from_date = date.today()+timedelta(days=-1)
                        to_date = date.today()+timedelta(days=1)

                    if report_data.get('type', False) and report_data.get('type', False) == 'yesterday':
                        from_date = date.today()+timedelta(days=-2)
                        to_date = date.today()

                    if report_data.get('type', False) and report_data.get('type', False) == 'last_week':
                        from_date = date.today()+timedelta(days=-8)
                        to_date = date.today()

                    if report_data.get('type', False) and report_data.get('type', False) == 'last_month':
                        from_date = date.today()+timedelta(days=-32)
                        to_date = date.today()

                    # ticket_ids = self.env['helpdesk.ticket'].search([]).filtered(
                    #                 lambda self: str(self.create_date.date()) > str(from_date) and str(
                    #                 self.create_date.date()) < str(to_date))

                    ticket_inv_line_ids = self.env['helpdesk.invoice.line'].search([('helpdesk_inv_ids', '!=', False)])
                    if report_data.get('product_id'):
                        ticket_inv_line_ids = self.env['helpdesk.invoice.line'].search(
                            [('product_id', '=', report_data.get('product_id')),
                             ('helpdesk_inv_ids', '!=', False)])
                    ticket_inv_line_ids = ticket_inv_line_ids.filtered(
                        lambda self: str(self.create_date.date()) > str(from_date) and str(
                            self.create_date.date()) < str(to_date))



                    worksheet = workbook.add_worksheet('Service Ticket')
                    worksheet.set_column('A:A', 10)
                    worksheet.set_column('B:B', 15)
                    worksheet.set_column('C:C', 10)
                    worksheet.set_column('D:D', 20)
                    worksheet.set_column('E:E', 8)
                    worksheet.set_column('F:F', 8)
                    worksheet.set_column('G:G', 12)
                    worksheet.set_column('H:H', 8)
                    worksheet.set_column('I:I', 10)
                    # worksheet.set_column('J:J', 10)

                    row=1

                    merge_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': 1, })
                    worksheet.write('A1', 'Ticket No', merge_format)
                    worksheet.write('B1', 'Assigned To', merge_format)
                    worksheet.write('C1', 'Product', merge_format)
                    worksheet.write('D1', 'Create Date', merge_format)
                    worksheet.write('E1', 'Fault Area', merge_format)
                    worksheet.write('F1', 'SO Number', merge_format)
                    worksheet.write('G1', 'Ref', merge_format)
                    worksheet.write('H1', 'Customer Name', merge_format)
                    worksheet.write('I1', 'Resolution', merge_format)
                    worksheet.write('J1', 'Status', merge_format)
                    worksheet.write('K1', 'Closed Date', merge_format)

                    row+=1
                    col = workbook.add_format({'align': 'center', 'valign': 'vcenter',})
                    states = ''
                    if ticket_inv_line_ids:
                        states = [res for res in ticket_inv_line_ids[0].helpdesk_inv_ids._fields['state'].selection]        # if state == res[0]][0][1]

                    # for tkt in set([rec.assi_to.id for rec in ticket_inv_line_ids]):
                    #
                    #     for rec in ticket_inv_line_ids:
                    #         if tkt == rec.assi_to.id:
                    #             worksheet.write(('A%s' % (str(row))), rec.assi_to.name, col)
                    #             worksheet.write(('B%s' % (str(row))), rec.ticket_no, col)
                    #             worksheet.write(('C%s' % (str(row))), rec.tref if rec.tref else '', col)
                    #             worksheet.write(('D%s' % (str(row))), rec.tpartner_name, col)
                    #             worksheet.write(('E%s' % (str(row))), rec.fault_area if rec.fault_area else '', col)
                    #             worksheet.write(('F%s' % (str(row))), [st for st in states if rec.state == st[0]][0][1], col)
                    #             worksheet.write(('G%s' % (str(row))), str(rec.create_date), col)
                    #             worksheet.write(('H%s' % (str(row))), str(rec.close_date) if rec.close_date else '', col)
                    #             worksheet.write(('I%s' % (str(row))), rec.total_hours, col)
                    #
                    #             row+=1
                    for inv_tkt in ticket_inv_line_ids:
                        worksheet.write(('A%s' % (str(row))), inv_tkt.helpdesk_inv_ids.ticket_no, col)
                        worksheet.write(('B%s' % (str(row))), inv_tkt.assi_to.name, col)
                        worksheet.write(('C%s' % (str(row))), inv_tkt.product_id.name, col)
                        worksheet.write(('D%s' % (str(row))), str(inv_tkt.ticket_create_date), col)
                        worksheet.write(('E%s' % (str(row))), inv_tkt.ticket_fault_area if inv_tkt.ticket_fault_area else '', col)
                        worksheet.write(('F%s' % (str(row))), inv_tkt.serial_no if inv_tkt.serial_no else '', col)
                        worksheet.write(('G%s' % (str(row))), inv_tkt.tref if inv_tkt.tref else '', col)
                        worksheet.write(('H%s' % (str(row))), inv_tkt.tpartner_name if inv_tkt.tpartner_name else '', col)
                        worksheet.write(('I%s' % (str(row))), inv_tkt.resolution if inv_tkt.resolution else '', col)
                        worksheet.write(('J%s' % (str(row))), [st for st in states if inv_tkt.state == st[0]][0][1], col)
                        worksheet.write(('K%s' % (str(row))), str(inv_tkt.close_date), col)

                        row += 1