# -*- coding: utf-8 -*-
from odoo import models, tools, fields, api, _


class ResUsers(models.Model):
    _inherit = "res.users"

    insabhi_access_token = fields.Char('ICON API USER TOKEN')
