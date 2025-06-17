# -*- coding: utf-8 -*-
##############################################################################
#
#    INSABHI
#    Copyright (C) 2025-Today(www.insabhi.com).
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
from openerp import http, SUPERUSER_ID
from openerp.http import request


class MainController(http.Controller):
    @http.route(['/products/list', '/products/list/page/<int:page>'], auth='user', website=True)
    def products_list(self, page=0, ppg=10, **kw):
        try:
            ppg = int(ppg)
        except Exception:
            ppg = 10  # fallback default

        Product = request.env['product.product'].sudo()
        domain = [('type', '=', 'product')]
        product_count = Product.search_count(domain)

        pager = request.website.pager(
            url='/products/list',
            total=product_count,
            page=page,
            step=ppg,
            scope=7,
            url_args=kw
        )

        offset = pager['offset']
        products = Product.search(domain, offset=offset, limit=ppg)

        return request.render('insabhi_website_inventory_module.products_list', {
            'products': products,
            'pager': pager,
            'ppg': ppg
        })

    @http.route(["/create/lot"], type='http', auth="user", methods=['POST'], website=True, csrf=False)
    def product_image_slider(self, **kw):
        product_id = int(kw.get('product_id', 0))
        location_id = int(kw.get('warehouse_id', 0))
        quantity = float(kw.get('quantity', 0.0))
        lot_name = kw.get('lot_id')

        if not product_id or not location_id or not quantity:
            return request.redirect('/products/list')  # You can add a flash message here if needed

        product = request.env['product.product'].sudo().browse(product_id)
        Lot = request.env['stock.production.lot'].sudo()
        Quant = request.env['stock.quant'].sudo()
        lot_id = False

        # CASE 1: If lot_name is provided
        if lot_name:
            existing_lot = Lot.search([
                ('name', '=', lot_name),
                ('product_id', '=', product.id)
            ], limit=1)

            if not existing_lot:
                lot_id = Lot.create({
                    'product_id': product.id,
                    'name': lot_name,
                    'product_qty': quantity,
                })
            else:
                existing_lot.product_qty += quantity
                lot_id = existing_lot

        # Merge or Create Quant (with or without lot)
        quant_domain = [
            ('product_id', '=', product.id),
            ('location_id', '=', location_id),
        ]
        if lot_id:
            quant_domain.append(('lot_id', '=', lot_id.id))
        else:
            quant_domain.append(('lot_id', '=', False))

        existing_quant = Quant.search(quant_domain, limit=1)

        if existing_quant:
            existing_quant.quantity += quantity
        else:
            Quant.create({
                'product_id': product.id,
                'location_id': location_id,
                'lot_id': lot_id.id if lot_id else False,
                'quantity': quantity,
            })

        return request.redirect('/products/list')