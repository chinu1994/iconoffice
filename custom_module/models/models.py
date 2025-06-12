from odoo import models, fields, api, _

class CountryState(models.Model):
    _inherit = "res.country.state"

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.code))
        return result
