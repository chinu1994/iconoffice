from odoo import models, tools, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class HelpDeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    @api.multi
    def write(self, vals):
        res = super(HelpDeskTicket, self).write(vals)
        if vals.get('state') == 'assigned':
            notification_vals = {
                'name': self.display_name or 'Ticket',
                'partner_id': self.customer.id if self.customer else False,
            }
            if notification_vals:
                self.env['notification.list'].create(notification_vals)
        return res