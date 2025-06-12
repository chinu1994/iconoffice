
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
import xlrd, logging, base64

_logger = logging.getLogger(__name__)

class ImportFile(models.TransientModel):
    _name = "sltech.import.excel"

    xls_file = fields.Binary('File')
    xlsx_filename = fields.Binary('File')
    limit_rec = fields.Integer('Limit Record')
    categ_id = fields.Many2one('product.category', 'Category')


    def get_actual_string_without_decimal(self, check_str):
        if check_str and isinstance(check_str, float):
            check_str = int(check_str)
        return check_str

    @api.multi
    def import_parts_stock(self):
        book = xlrd.open_workbook(file_contents=base64.decodestring(self.xls_file))
        max_nb_row = book.sheet_by_index(0).nrows
        f_row = []
        for row in range(max_nb_row):
            if row == 0:
                f_row = book.sheet_by_index(0).row_values(row)
                continue
            else:
                header = f_row
                i = 0
                return_val = {}
                header_name = ''
                for rec in book.sheet_by_index(0).row_values(row):
                    if len(header) >= i and header[i] != '':
                        header_name = str(header[i])

                    if header_name == 'Description':
                        return_val['name'] = self.get_actual_string_without_decimal(rec)
                    if header_name == 'Serial number':
                        return_val['serial_no'] = self.get_actual_string_without_decimal(rec)
                    if header_name == 'Status':
                        return_val['status'] = self.get_actual_string_without_decimal(rec)
                    if header_name == 'BAY NUMBER':
                        return_val['location'] = self.get_actual_string_without_decimal(rec)
                    if header_name == 'MONO':
                        return_val['mono'] = self.get_actual_string_without_decimal(rec)
                    if header_name == 'COLOUR':
                        return_val['colour'] = self.get_actual_string_without_decimal(rec)


                    i += 1


                #  product
                self.env.cr.execute("select * from product_template where name = \'%s\'"% return_val['name'])
                pro_res = self.env.cr.dictfetchall()

                product_id = self.env['product.product']

                if not pro_res:
                    pro_tmpl_id = self.env['product.template'].create({
                        'name': return_val['name'],
                        'tracking': 'serial',
                        'type': 'product',
                        'categ_id': self.categ_id.id
                    })

                    product_id = product_id.search([('product_tmpl_id', '=', pro_tmpl_id.id)])
                else:

                    product_id = product_id.search([('product_tmpl_id', '=', pro_res[0]['id'])])

                lot_id = self.env['stock.production.lot'].search([('product_id', '=', product_id.id),
                                                                  ('name', '=', return_val['serial_no'])])
                if not lot_id:
                    lot_id = lot_id.create({
                        'product_id': product_id.id,
                        'name': return_val['serial_no'],
                    })

                lot_id.write(dict(
                    sltech_mono=return_val['mono'],
                    sltech_color=return_val['colour'],
                    sltech_product_categ_id=self.categ_id.id,
                    vendor_id=self.env['stock.inventory'].browse(self._context.get('active_id')).vendor_id.id,
                ))

                #  end


                #   location

                self.env.cr.execute("select * from stock_location where name = \'%s\'" % return_val['location'])
                location_res = self.env.cr.dictfetchall()

                location_id = False
                if not location_res:
                    location_id = self.env['stock.location'].create({
                        'name': return_val['location'],
                        'location_id': self.env.ref('stock.stock_location_stock').id,
                    }).id
                else:
                    location_id = location_res[0]['id']

                #   end


                inventory_id = self.env['stock.inventory'].browse(self._context.get('active_id'))
                if return_val['status'] == 'AVAILABLE':
                    inventory_id.line_ids = [(0, 0, {
                        'location_id': location_id,
                        'product_id': product_id.id,
                        'product_uom_id': product_id.uom_id.id,
                        'prod_lot_id': lot_id.id,
                        'product_qty': 1
                    })]