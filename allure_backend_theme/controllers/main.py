# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import odoo
from odoo import http
from odoo.addons.web.controllers.main import *
from odoo.http import request


class MenuSearch(http.Controller):

    @http.route('/all/menu/search', auth='user', type='json')
    def all_visible_menu(self):
        all_menu_ids = request.env['ir.ui.menu'].search([('action', '!=', 'false')])
        menu_ids = []
        for menu in all_menu_ids:
            parent_path = menu.parent_path
            parent_menu_list = list(map(int, parent_path.split('/')[:-1]))
            parent_menu_ids = request.env['ir.ui.menu'].browse(parent_menu_list)
            if len(parent_menu_list) == len(parent_menu_ids._filter_visible_menus()):
                menu_ids.append(menu.id)
        menu_datas = request.env['ir.ui.menu'].search_read([
            ('id', 'in', menu_ids),
            ('action', '!=', 'false')],
            ['name', 'action', 'complete_name','parent_path'])

        return menu_datas

    def get_view_ids(self, xml_ids):
        ids = []
        for xml_id in xml_ids:
            if "." in xml_id:
                record_id = request.env.ref(xml_id).id
            else:
                record_id = int(xml_id)
            ids.append(record_id)
        return ids

    @http.route(['/web/theme_customize_backend_get'], type='json', website=True, auth="public")
    def theme_customize_backend_get(self, xml_ids):
        enable = []
        disable = []
        ids = self.get_view_ids(xml_ids)
        for view in request.env['ir.ui.view'].with_context(
                active_test=True).browse(ids):
            if view.active:
                enable.append(view.xml_id)
            else:
                disable.append(view.xml_id)
        return [enable, disable]