# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import time
from odoo.exceptions import UserError, ValidationError
# from datetime import  timedelta
from dateutil.relativedelta import relativedelta
from datetime import date
from calendar import monthrange
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import models, tools, fields, api, _
from odoo.exceptions import UserError, AccessError
import json, sys, base64, pytz
import logging
_logger = logging.getLogger(__name__)

class HelpDeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    @api.multi
    def write(self, vals):
        res= super(HelpDeskTicket, self).write(vals)
        if vals.get('state') == 'assigned':


            email = self.env.user.email
            if email:
                for meeting in self.event_id:
                    meeting.sudo().attendee_ids._send_mail_to_attendees('calendar.calendar_template_meeting_invitation', force_send=True)


        return res