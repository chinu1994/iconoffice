from odoo import models, api, fields, _


class SaleOrder(models.TransientModel):
    _name = "invoice.wizard"

    from_date = fields.Datetime(string='From Date')
    to_date = fields.Datetime(string='To Date')

    def generate_service_lines(self):
        cust_inv = [('close_date', '>', str(self.from_date)),
                     ('close_date', '<', str(self.to_date)),
                     ('is_email_send', '=', True)]

        helpdesk_invoice_line_ids = self.env['helpdesk.invoice.line'].sudo().search(cust_inv)
        filtered_helpdesk_invoice_line_ids = helpdesk_invoice_line_ids.filtered(lambda obj: obj.product_id.id not in obj.invoice_id.invoice_line_ids.mapped('product_id').ids)
        print(len(helpdesk_invoice_line_ids))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Service Ticket Invoice Line'),
            'view_mode': 'tree',
            'res_model': 'helpdesk.invoice.line',
            'limit': 10000,
            'domain':[('id', 'in', filtered_helpdesk_invoice_line_ids.ids)]
        }


