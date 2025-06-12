# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class FavoriteUiMenu(models.Model):
    _name = 'ir.favorite.menu'
    _order = "sequence"
    _description = "Favorite Menu"

    favorite_menu_id = fields.Many2one('ir.ui.menu', 'Favorite Menu', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', 'User Name')
    sequence = fields.Integer(string="sequence")
    favorite_menu_xml_id = fields.Char(string="Favorite Menu Xml")
    favorite_menu_action_id = fields.Integer(string="Favorite Menu Action")

    @api.model
    def create(self, vals):
        vals['sequence'] = self.env['ir.sequence'].next_by_code('ir.favorite.menu') or 0
        return super(FavoriteUiMenu, self).create(vals)

    @api.multi
    def unlink_menu_id(self, user, data):
        value = self.search([('favorite_menu_id', '=', data), ('user_id', '=', user)])
        value.unlink()
