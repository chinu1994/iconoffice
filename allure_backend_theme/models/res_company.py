# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo import tools


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.depends('partner_id', 'partner_id.image')
    def _compute_logo_web(self):
        for company in self:
            if company.theme_logo:
                company.logo_web = tools.image_resize_image(company.theme_logo, (180, None))
            else:
                company.logo_web = tools.image_resize_image(company.partner_id.image, (180, None))

    logo_web = fields.Binary(compute='_compute_logo_web', store=True)
    theme_logo = fields.Binary(string='Theme Logo')
    theme_icon = fields.Binary(string='Theme Icon')
