# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    favorite_menu_ids = fields.One2many('ir.favorite.menu', 'user_id', 'Favorite Menu')
    display_density = fields.Selection([
        ('default', 'Default'),
        ('comfortable', 'Comfortable'),
        ('compact', 'Compact'),
    ], string="Display Density", default='default')
    tab_type = fields.Selection([
        ('horizontal_tabs', 'Horizontal Tabs'),
        ('vertical_tabs', 'Vertical Tabs'),
    ], string="Tab Type", default='vertical_tabs')
    tab_configration = fields.Selection([
        ('open_tabs', 'Open Tabs'),
        ('close_tabs', 'Close Tabs',),
    ], default='open_tabs')
    base_menu = fields.Selection([
        ('base_menu', 'Horizontal Menu'),
        ('theme_menu', 'Vertical Menu'),
    ], default='theme_menu')
    font_type_values = fields.Selection([
        ('roboto', 'Roboto'),
        ('open_sans', 'Open Sans'),
        ('alice', 'Alice'),
        ('abel', 'Abel'),
        ('montserrat', 'Montserrat'),
        ('lato', 'Lato'),
    ], default='roboto')
    base_menu_icon = fields.Selection([
        ('base_icon', 'Base Icon'),
        ('3d_icon', '3d Icon'),
        ('2d_icon', '2d Icon'),
    ], default='base_icon')
    mode = fields.Selection([
        ('light_mode_on', 'Light Mode'),
        ('night_mode_on', 'Night Mode'),
        ('normal_mode_on', 'Normal Mode'),
    ], default='normal_mode_on')
