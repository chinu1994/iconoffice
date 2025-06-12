# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, modules, tools, _


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.multi
    def get_attachments(self, model, domain, context):
        values = {}
        if self.user_has_groups('allure_backend_theme.group_display_density'):
            resIDs = self.env[model].search(domain).ids
            values.update(
                {'group_display_density': True, 'displayDensity': {'display_density': self.env.user.display_density}})
            if self.env.user.display_density == 'default':
                values.update({
                    'nbAttahments': self.get_nbattachments(resIDs, model),
                    'attachmentsData': self.search_attechment(resIDs, model)
                })
        return values

    @api.model
    def get_nbattachments(self, resIDs, resModel):
        nb_attachments = []
        for resId in resIDs:
            records = self.search_count([('res_id', '=', resId), ('res_model', '=', resModel)])
            nb_attachments.append({resId: records})
        return nb_attachments

    @api.model
    def search_attechment(self, resIDs, resModel):
        attachment_data = []
        for resID in resIDs:
            records = self.search_read(
                [('res_id', '=', resID), ('res_model', '=', resModel)],
                ['id', 'name', 'res_id', 'mimetype'], limit=3
            )
            if records:
                attachment_data.append({resID: records})
        return attachment_data
