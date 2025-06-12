# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import operator
from odoo import api, fields, models, modules, tools, _
from odoo.modules import get_module_resource
from os.path import isfile


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    theme_icon = fields.Char(string='Theme Icon Path')
    theme_icon_data = fields.Binary(string='Theme Icon Image', attachment=True)

    @api.model_create_multi
    def create(self, vals_list):
        icon_type = self.env['ir.config_parameter'].sudo().get_param("base_menu_icon")
        self.clear_caches()
        if icon_type == '3d_icon':
            for values in vals_list:
                icon_path = ''
                if values.get('web_icon'):
                    icon = values.get('web_icon').split(',')
                    module_name = icon[0]
                    icon_path = "allure_backend_theme,static/src/img/menu/%s.png" % (module_name)
                if 'web_icon' in values:
                    values['theme_icon_data'] = self._compute_web_icon_data(icon_path or values.get('web_icon'))
        elif icon_type == '2d_icon':
            for values in vals_list:
                icon_path = ''
                if values.get('web_icon'):
                    icon = values.get('web_icon').split(',')
                    module_name = icon[0]
                    icon_path = "allure_backend_theme,static/src/img/menu_2d/%s.png" % (module_name)
                if 'web_icon' in values:
                    values['theme_icon_data'] = self._compute_web_icon_data(icon_path or values.get('web_icon'))
        else:
            for values in vals_list:
                values['theme_icon_data'] = self._compute_web_icon_data(values.get('web_icon'))
        return super(models.Model, self).create(vals_list)

    @api.multi
    def write(self, values):
        self.clear_caches()
        if 'theme_icon' in values:
            values['theme_icon_data'] = self._compute_web_icon_data(values['theme_icon'])
        return super(models.Model, self).write(values)

    @api.model
    @tools.ormcache_context('self._uid', keys=('lang',))
    def load_menus_root(self):
        fields = ['name', 'sequence', 'parent_id', 'action', 'web_icon_data', 'theme_icon_data']
        menu_roots = self.get_user_roots()
        menu_roots_data = menu_roots.read(fields) if menu_roots else []

        menu_root = {
            'id': False,
            'name': 'root',
            'parent_id': [-1, ''],
            'children': menu_roots_data,
            'all_menu_ids': menu_roots.ids,
        }

        menu_roots._set_menuitems_xmlids(menu_root)

        return menu_root

    @api.model
    @tools.ormcache_context('self._uid', 'debug', keys=('lang',))
    def load_menus(self, debug):
        """ Loads all menu items (all applications and their sub-menus).

        :return: the menu root
        :rtype: dict('children': menu_nodes)
        """
        fields = ['name', 'sequence', 'parent_id', 'action', 'web_icon', 'web_icon_data', 'theme_icon_data']
        menu_roots = self.get_user_roots()
        menu_roots_data = menu_roots.read(fields) if menu_roots else []
        menu_root = {
            'id': False,
            'name': 'root',
            'parent_id': [-1, ''],
            'children': menu_roots_data,
            'all_menu_ids': menu_roots.ids,
        }

        if not menu_roots_data:
            return menu_root

        # menus are loaded fully unlike a regular tree view, cause there are a
        # limited number of items (752 when all 6.1 addons are installed)
        menus = self.search([('id', 'child_of', menu_roots.ids)])
        menu_items = menus.read(fields)

        # add roots at the end of the sequence, so that they will overwrite
        # equivalent menu items from full menu read when put into id:item
        # mapping, resulting in children being correctly set on the roots.
        menu_items.extend(menu_roots_data)
        menu_root['all_menu_ids'] = menus.ids  # includes menu_roots!

        # make a tree using parent_id
        menu_items_map = {menu_item["id"]: menu_item for menu_item in menu_items}
        for menu_item in menu_items:
            parent = menu_item['parent_id'] and menu_item['parent_id'][0]
            if parent in menu_items_map:
                menu_items_map[parent].setdefault(
                    'children', []).append(menu_item)

        # sort by sequence a tree using parent_id
        for menu_item in menu_items:
            menu_item.setdefault('children', []).sort(key=operator.itemgetter('sequence'))

        (menu_roots + menus)._set_menuitems_xmlids(menu_root)

        return menu_root

    @api.multi
    def icon_menu_chnange(self, form_values):
        modules = self.env['ir.module.module'].sudo().search([])
        menu_ids = self.sudo().get_user_roots().mapped('id')
        board_id = self.env.ref('base.menu_board_root').id
        menu_ids.append(board_id)
        menus = self.sudo().browse(menu_ids)
        if form_values['base_menu_icon'] == '3d_icon':
            for module in modules:
                if module.name:
                    icon_path = 'static/src/img/menu/' + module.name + '.png'
                    module_path = get_module_resource('allure_backend_theme', icon_path)
                    if isfile(module_path):
                        module.write({'theme_icon': '/allure_backend_theme/' + icon_path})
                    elif module.icon == '/base/static/description/icon.png':
                        module.write({'theme_icon': '/allure_backend_theme/static/src/img/menu/custom.png'})
                    else:
                        module.write({'theme_icon': module.icon})
            for menu in menus:
                if menu.web_icon:
                    path_info = menu.web_icon.split(',')
                    module_name = path_info[0]
                    icon_path = 'static/src/img/menu/' + module_name + '.png'
                    module_path = get_module_resource('allure_backend_theme', icon_path)
                    if isfile(module_path):
                        menu.write({'theme_icon': 'allure_backend_theme,' + icon_path,
                                    'theme_icon_data': self._compute_web_icon_data(
                                        'allure_backend_theme,' + icon_path)})
                    elif path_info[1] == '/base/static/description/icon.png':
                        menu.write({'theme_icon': 'allure_backend_theme,static/src/img/menu/custom.png',
                                    'theme_icon_data': self._compute_web_icon_data(
                                        'allure_backend_theme,static/src/img/menu/custom.png')})
                    else:
                        menu.write({'theme_icon': menu.web_icon,
                                    'theme_icon_data': self._compute_web_icon_data(menu.web_icon)})
                    if path_info[0] == 'base':
                        icon_name = path_info[1].split('/')
                        if icon_name and icon_name[-1:][0]:
                            icon = icon_name[-1:][0]
                            icon_path = "allure_backend_theme,static/src/img/menu/%s" % (icon)
                            menu.write({'theme_icon': icon_path,
                                        'theme_icon_data': self._compute_web_icon_data(icon_path)})
        elif form_values['base_menu_icon'] == '2d_icon':
            for module in modules:
                if module.name:
                    icon_path = 'static/src/img/menu_2d/' + module.name + '.png'
                    module_path = get_module_resource('allure_backend_theme', icon_path)
                    if isfile(module_path):
                        module.write({'theme_icon': '/allure_backend_theme/' + icon_path})
                    elif module.icon == '/base/static/description/icon.png':
                        module.write({'theme_icon': '/allure_backend_theme/static/src/img/menu_2d/custom.png'})
                    else:
                        module.write({'theme_icon': module.icon})
            for menu in menus:
                if menu.web_icon:
                    path_info = menu.web_icon.split(',')
                    module_name = path_info[0]
                    icon_path = 'static/src/img/menu_2d/' + module_name + '.png'
                    module_path = get_module_resource('allure_backend_theme', icon_path)
                    if isfile(module_path):
                        menu.write({'theme_icon': 'allure_backend_theme,' + icon_path,
                                    'theme_icon_data': self._compute_web_icon_data(
                                        'allure_backend_theme,' + icon_path)})
                    elif path_info[1] == '/base/static/description/icon.png':
                        menu.write({'theme_icon': 'allure_backend_theme,static/src/img/menu_2d/custom.png',
                                    'theme_icon_data': self._compute_web_icon_data(
                                        'allure_backend_theme,static/src/img/menu_2d/custom.png')})
                    else:
                        menu.write({'theme_icon': menu.web_icon,
                                    'theme_icon_data': self._compute_web_icon_data(menu.web_icon)})
                    if path_info[0] == 'base':
                        icon_name = path_info[1].split('/')
                        if icon_name and icon_name[-1:][0]:
                            icon = icon_name[-1:][0]
                            icon_path = "allure_backend_theme,static/src/img/menu_2d/%s" % (icon)
                            menu.write({'theme_icon': icon_path,
                                        'theme_icon_data': self._compute_web_icon_data(icon_path)})
        else:
            for module in modules:
                path_info = module.icon
                module.write({'theme_icon': path_info})
            for menu in menus:
                if menu.web_icon:
                    path_info = menu.web_icon
                    menu.write({'theme_icon': path_info,
                                'theme_icon_data': self._compute_web_icon_data(path_info)})
