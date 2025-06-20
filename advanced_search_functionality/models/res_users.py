# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class User(models.Model):

    _inherit = 'res.users'

    group_search_date_range = fields.Boolean("Odoo Advance Date Range search",default=True)