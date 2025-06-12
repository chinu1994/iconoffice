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


class IconOffice(models.AbstractModel):
    _name = 'report.custom_invoice.ticket_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        worksheet = workbook.add_worksheet('Custom Invoice')
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 10)
        worksheet.set_column('C:C', 10)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 8)
        worksheet.set_column('F:F', 8)
        worksheet.set_column('G:G', 12)
        worksheet.set_column('H:H', 8)
        worksheet.set_column('I:I', 10)


        # date_format = workbook.add_format({'num_format': 'd-mmm-yyyy'})



        col = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': 1, })
        col_right = workbook.add_format({'align': 'right', 'bold': 1, })
        col.set_font_size(20)

        worksheet.merge_range('A%s:D%s' % (1,4), 'Tax Invoice', col)
        logo = self.env.user.company_id.logo
        buf_image = io.BytesIO(base64.b64decode(logo))
        worksheet.insert_image('G1:H1', "any_name.png", {'image_data': buf_image})

        col = workbook.add_format({'align': 'left', 'bold': 1, })
        # worksheet.insert_image('A2', image_path)
        worksheet.write('A%s' % (6), 'Attention:', col)
        worksheet.write('B6:C6', 'ACCOUNTS PAYABLE', col)

        worksheet.write('A%s' % (7), 'Company:', col)
        worksheet.write('B7:C7', self.env.user.company_id.name, col)

        address1 = ""
        if obj.partner_id.street:
            address1 += obj.partner_id.street
        if obj.partner_id.street2:
            address1 += obj.partner_id.street2
        address2 = ""
        if obj.partner_id.city:
            address2 += obj.partner_id.city
        if obj.partner_id.zip:
            address2 += obj.partner_id.zip

        worksheet.write('A%s' % (8), 'Address', col)
        worksheet.write('B8:C8', address1, col)
        worksheet.write('B9:C9', address2, col)

        worksheet.write('G%s' % (6), 'ABN:', col)
        worksheet.merge_range('H6:I6', obj.partner_id.vat, col_right)

        worksheet.write('G%s' % (7), 'Invoice Date', col)
        worksheet.merge_range('H7:I7', str(obj.date_invoice), col_right)

        worksheet.write('G%s' % (8), 'Invoice No.', col)
        invoice_number = obj.number if obj.number else ''
        worksheet.merge_range('H8:I8', invoice_number, col_right)

        row = 10
        # worksheet.merge_range('A%s:C%s' % (row,row), 'Description', col)
        # worksheet.write('D%s' % (row), 'Customer Product', col_right)
        # worksheet.write('E%s' % (row), 'Unit', col_right)
        # worksheet.write('F%s' % (row), 'Rate', col_right)
        # worksheet.write('G%s' % (row), 'Amount', col_right)
        # worksheet.write('H%s' % (row), 'GST', col_right)
        # worksheet.write('I%s' % (row), 'Gross', col_right)
        # row+=1
        #
        # amt_tot = 0
        # tax_tot = 0
        # total = 0
        # inv_data = obj.get_data()
        # for rec in inv_data:
        #
        #     worksheet.merge_range('A%s:I%s' % (row, row), rec.get('tpartner_name'), col)
        #     row += 1
        #     # worksheet.merge_range('A%s:I%s' % (row, row), '')
        #     # row += 1
        #     worksheet.write('A%s' % (row), 'SR No.', col)
        #     worksheet.write('B%s' % (row), 'Job No.', col)
        #     worksheet.write('C%s' % (row), 'Serial No.', col)
        #     row += 1
        #
        #
        #     worksheet.write('A%s' % (row), rec.get('s_no'), col)
        #     worksheet.write('B%s' % (row), rec.get('job'), col)
        #     worksheet.write('C%s' % (row), rec.get('c_name'), col)
        #     row = row + 2
        #     for line_rec in rec.get('val'):
        #         worksheet.write('D%s' % (row), line_rec.get('product_name'))
        #         worksheet.write('E%s' % (row), line_rec.get('qty'))
        #         worksheet.write('F%s' % (row),line_rec.get('price'))
        #         worksheet.write('G%s' % (row), line_rec.get('amt'))
        #         worksheet.write('H%s' % (row),line_rec.get('tax'))
        #         worksheet.write('I%s' % (row), line_rec.get('total'))
        #         tax_tot += line_rec.get('tax')
        #         amt_tot += line_rec.get('amt')
        #         total += line_rec.get('total')
        #         row +=1
        #     row += 1
        #
        # col = workbook.add_format({'align': 'right', 'bold': 1, })
        # worksheet.merge_range('A%s:H%s' % (row,row), 'Total (EX GST)', col)
        # worksheet.write('I%s' % (row), amt_tot, col)
        # row +=1
        # worksheet.merge_range('A%s:H%s' % (row,row), 'GST Amount', col)
        # worksheet.write('I%s' % (row), tax_tot, col)
        # row += 1
        # worksheet.merge_range('A%s:H%s' % (row, row), 'Total Payable Amount', col)
        # worksheet.write('I%s' % (row), total, col)

        worksheet.write('A%s' % (row), 'SR No', col)
        worksheet.write('B%s' % (row), 'Ref', col)
        worksheet.write('C%s' % (row), 'Serial No', col)
        worksheet.write('D%s' % (row), 'Product Code', col)
        worksheet.write('E%s' % (row), 'Unit', col)
        worksheet.write('F%s' % (row), 'Rate', col)
        worksheet.write('G%s' % (row), 'Amount', col)
        worksheet.write('H%s' % (row), 'GST', col)
        worksheet.write('I%s' % (row), 'Gross', col)

        row+=1

        total_amt_tot = 0
        total_tax_tot = 0
        total_total = 0
        inv_data = obj.invoice_line_ids
        ticket_inv_line_ids = obj.ticket_inv_line_ids
        for rec in inv_data:

            tkt_inv_line_id = ticket_inv_line_ids.filtered(lambda self:self.helpdesk_inv_ids.ticket_no == rec.name)[0]

            amt_tot = rec.quantity*rec.price_unit
            tax_tot = ((sum([tax.amount for tax in rec.invoice_line_tax_ids])) *rec.quantity* rec.price_unit)/100
            total = (rec.quantity * rec.price_unit) + tax_tot

            worksheet.write('A%s' % (row), tkt_inv_line_id.helpdesk_inv_ids.ticket_no, col)
            worksheet.write('B%s' % (row), tkt_inv_line_id.tref, col)
            worksheet.write('C%s' % (row), tkt_inv_line_id.serial_no, col)
            worksheet.write('D%s' % (row), rec.product_id.name, col)
            worksheet.write('E%s' % (row), rec.quantity, col)
            worksheet.write('F%s' % (row), rec.price_unit, col)
            worksheet.write('G%s' % (row), amt_tot, col)
            worksheet.write('H%s' % (row), tax_tot, col)
            worksheet.write('I%s' % (row), total, col)

            total_amt_tot += amt_tot
            total_tax_tot += tax_tot
            total_total += total

            row += 1

        row+=1
        col = workbook.add_format({'align': 'left', 'bold': 1, })
        worksheet.merge_range('E%s:H%s' % (row,row), 'Total (EX GST)', col)
        worksheet.write('I%s' % (row), total_amt_tot, col)
        row +=1
        worksheet.merge_range('E%s:H%s' % (row,row), 'GST Amount', col)
        worksheet.write('I%s' % (row), total_tax_tot, col)
        row += 1
        worksheet.merge_range('E%s:H%s' % (row, row), 'Total Payable Amount', col)
        worksheet.write('I%s' % (row), total_total, col)