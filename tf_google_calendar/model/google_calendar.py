# -*- coding: utf-8 -*-

from odoo import models, tools, fields, api, _

class CalendarContacts(models.Model):
    _inherit = "calendar.contacts"

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        res = super(CalendarContacts, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit,
                                                      order=order)



        return res