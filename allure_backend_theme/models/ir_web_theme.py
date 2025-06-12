# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import re
import os
from odoo import _, api, fields, models
from odoo.exceptions import UserError

static_dict_theme = {
    '$brand-primary': '#072635;',
    '$brand-secondary': '#1983a4;',
    '$button-box': '#0b3a49;',
    '$heading': '#1983a4;',
    '$Label': '#0b3a49;',
    '$Label-value': '#0b3a49;',
    '$link': '#1983a4;',
    '$notbook': '#0b3a49;',
    '$tooltip': '#072630;',
    '$border': '#e6e9ea;',
    '$menu-main-title': '#0b3a49;'
}

tag_dict_theme = {
    '$brand-tag-info': '#00b3e5;',
    '$brand-tag-danger': '#ca0c05;',
    '$brand-tag-success': '#00aa00;',
    '$brand-tag-warning': '#e47e01;',
    '$brand-tag-primary': '#005ba9;',
    '$brand-tag-muted': '#717171;'
}


class IrWebTheme(models.Model):
    _name = "ir.web.theme"
    _description = "Theme Configuration"

    leftbar_color = fields.Char(string='Custom Color', required=True, default="#875a7b")
    menu_color = fields.Char(string='Menu', required=True, default="#666666")
    border_color = fields.Char(string='Border', required=True, default="#cccccc")
    buttons_color = fields.Char(string='Buttons Color', required=True, default="#00a09d")
    button_box = fields.Char(string='Button Box', required=True, default="#666666")
    heading_color = fields.Char(string='Heading Color', required=True, default="#2f3136")
    label_color = fields.Char(string='Label', required=True, default="#666666")
    label_value_color = fields.Char(string='Label Value Color', required=True, default="#666666")
    link_color = fields.Char(string='Link Color', required=True, default="#00a09d")
    panel_title_color = fields.Char(string='Panel Title Color', required=True, default="#2f3136")
    tooltip_color = fields.Char(string='Tooltip Color', required=True, default="#875a7b")
    tag_info = fields.Char(string="Tag Info", default="#00b3e5")
    tag_danger = fields.Char(string="Tag Danger", default="#ca0c05")
    tag_success = fields.Char(string="Tag Success", default="#00aa00")
    tag_warning = fields.Char(string="Tag Warning", default="#e47e01")
    tag_primary = fields.Char(string="Tag Primary", default="#005ba9")
    tag_muted = fields.Char(string="Tag Muted", default="#717171")

    base_form_tabs = fields.Selection([
        ('horizontal_tabs', 'Horizontal'),
        ('vertical_tabs', 'Vertical',),
    ], default='vertical_tabs')
    font_type_values = fields.Selection([
        ('roboto', 'Roboto'),
        ('open_sans', 'Open Sans'),
        ('alice', 'Alice'),
        ('abel', 'Abel'),
        ('montserrat', 'Montserrat'),
        ('lato', 'Lato'),
    ], default='roboto')
    tab_configration = fields.Selection([
        ('open_tabs', 'Open'),
        ('close_tabs', 'Close',),
    ], default='open_tabs')
    base_menu_icon = fields.Selection([
        ('base_icon', 'Base'),
        ('3d_icon', '3d'),
        ('2d_icon', '2d'),
    ], default='base_icon')
    base_menu = fields.Selection([
        ('base_menu', 'Horizontal'),
        ('theme_menu', 'Vertical'),
    ], default='theme_menu')
    mode = fields.Selection([
        ('light_mode_on', 'Light'),
        ('night_mode_on', 'Night'),
        ('normal_mode_on', 'Normal'),
    ], default='normal_mode_on')

    def replace_file(self, file_path, static_dict):
        try:
            with open(file_path, 'w+') as new_file:
                for key, value in static_dict.items():
                    line = ''.join([key, ': ', value, ';\n'])
                    new_file.write(line)
            new_file.close()
        except Exception as e:
            raise UserError(_("Please follow the readme file. Contact to Administrator."
                              "\n %s") % e)

    @api.model
    def get_icon_state(self):
        base_menu_icon = self.env['ir.config_parameter'].sudo().get_param("base_menu_icon")
        return base_menu_icon

    @api.model
    def get_current_theme(self):
        theme_id = self.env['ir.config_parameter'].sudo().get_param("allure_backend_theme.selected_theme")
        return theme_id

    @api.multi
    def set_customize_theme(self, theme_id, form_values):
        self.env['ir.config_parameter'].sudo().set_param("allure_backend_theme.selected_theme", theme_id)
        self.env['ir.config_parameter'].sudo().set_param("base_form_tabs", form_values['base_form_tabs'])
        self.env['ir.config_parameter'].sudo().set_param("font_type_values", form_values['font_type_values'])
        self.env['ir.config_parameter'].sudo().set_param("base_menu_icon", form_values['base_menu_icon'])
        self.env['ir.config_parameter'].sudo().set_param("tab_configration", form_values['tab_configration'])
        self.env['ir.config_parameter'].sudo().set_param("base_menu", form_values['base_menu'])
        self.env['ir.config_parameter'].sudo().set_param("mode", form_values['mode'])
        is_backend_module_install = self.env['ir.config_parameter'].sudo().get_param("is_login_install")
        is_tag_module_install = self.env['ir.config_parameter'].sudo().get_param("is_tag_install")
        try:
            path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            theme_path = path + "/allure_backend_theme/static/src/scss/variables.scss"
            backend_login = path + "/backend_login/static/src/scss/variable.scss"
            status_tag = path + "/web_status_tags/static/src/scss/variable.scss"
        except Exception as e:
            raise UserError(_("Please Contact to Administrator. \n %s") % e)

        # Backend Theme Changes
        if form_values.get('leftbar_color', False):
            static_dict_theme.update({'$brand-primary': form_values['leftbar_color']})

        if form_values.get('buttons_color', False):
            static_dict_theme.update({'$brand-secondary': form_values['buttons_color']})

        if form_values.get('button_box', False):
            static_dict_theme.update({'$button-box': form_values['button_box']})

        if form_values.get('heading_color', False):
            static_dict_theme.update({'$heading': form_values['heading_color']})

        if form_values.get('label_color', False):
            static_dict_theme.update({'$Label': form_values['label_color']})

        if form_values.get('label_value_color', False):
            static_dict_theme.update({'$Label-value': form_values['label_value_color']})

        if form_values.get('link_color', False):
            static_dict_theme.update({'$link': form_values['link_color']})

        if form_values.get('panel_title_color', False):
            static_dict_theme.update({'$notbook': form_values['panel_title_color']})

        if form_values.get('tooltip_color', False):
            static_dict_theme.update({'$tooltip': form_values['tooltip_color']})

        if form_values.get('menu_color', False):
            static_dict_theme.update({'$menu-main-title': form_values['menu_color']})

        if form_values.get('border_color', False):
            static_dict_theme.update({'$border': form_values['border_color']})

        self.replace_file(theme_path, static_dict_theme)

        # Backend Login Changes
        if is_backend_module_install and form_values.get('leftbar_color', False):
            self.replace_file(backend_login, {'$brand-primary': form_values.get['leftbar_color']})

        # Web Status Tag Changes
        if is_tag_module_install:
            if form_values.get('tag_info', False):
                tag_dict_theme.update({'$brand-tag-info': form_values['tag_info']})

            if form_values.get('tag_danger', False):
                tag_dict_theme.update({'$brand-tag-danger': form_values['tag_danger']})

            if form_values.get('tag_success', False):
                tag_dict_theme.update({'$brand-tag-success': form_values['tag_success']})

            if form_values.get('tag_warning', False):
                tag_dict_theme.update({'$brand-tag-warning': form_values['tag_warning']})

            if form_values.get('tag_primary', False):
                tag_dict_theme.update({'$brand-tag-primary': form_values['tag_primary']})

            if form_values.get('tag_muted', False):
                tag_dict_theme.update({'$brand-tag-muted': form_values['tag_muted']})

            self.replace_file(status_tag, tag_dict_theme)
