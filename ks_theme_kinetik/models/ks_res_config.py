# Copyright 2016 Tecnativa - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class KsWebsiteConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ks_logo = fields.Binary(related='website_id.logo', readonly=False)
