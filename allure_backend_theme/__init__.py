# -*- coding: utf-8 -*-
# Part of Synconics. See LICENSE file for full copyright and licensing details.

from . import models
from . import controllers

from odoo import api, SUPERUSER_ID, _


def post_init_check(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    modules = env['ir.module.module'].search([])
    menu_ids = env['ir.ui.menu'].get_user_roots().mapped('id')
    board_id = env.ref('base.menu_board_root').id
    menu_ids.append(board_id)
    menus = env['ir.ui.menu'].browse(menu_ids)
    for module in modules:
        path_info = module.icon
        module.write({'theme_icon': path_info})

    for menu in menus:
        if menu.web_icon:
            path_info = menu.web_icon
            menu.write({'theme_icon': path_info})
