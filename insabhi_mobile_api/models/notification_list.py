
from odoo import models, fields

class NotificationList(models.Model):
    _name = 'notification.list'
    _description = 'Push Notification List'

    name = fields.Char('Title', required=True)
    body = fields.Text('Body')
    token = fields.Char('Device Token')
    state = fields.Selection([
        ('sent', 'Sent'),
        ('received', 'Received'),
        ('seen', 'Seen')
    ], string='State', default='sent')
    message_id = fields.Many2one('mail.message', 'Related Message')
    partner_id = fields.Many2one('res.partner', 'Recipient')
