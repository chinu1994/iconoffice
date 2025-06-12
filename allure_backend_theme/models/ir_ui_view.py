# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    def get_view_ids(self, xml_ids):
        ids = []
        for xml_id in xml_ids:
            if "." in xml_id:
                record_id = self.env.ref(xml_id).id
            else:
                record_id = int(xml_id)
            ids.append(record_id)
        return ids

    @api.multi
    def set_night_mode(self):
        context = dict(self.env.context or {})

        def set_active(ids, active):
            if ids:
                real_ids = self.get_view_ids(ids)
                res = self.browse(real_ids).sudo().write({'active': active})

        set_active(context.get('disable'), False)
        set_active(context.get('enable'), True)

        if context.get('get_bundle'):
            context = dict(self._context, active_test=True)
            return self.env["ir.qweb"]._get_asset('web.assets_backend', options=context, debug='assets')
        return True
