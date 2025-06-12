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
from odoo.addons import decimal_precision as dp
_logger = logging.getLogger(__name__)

class HelpDeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    _order = 'ticket_no desc'

    active = fields.Boolean(default=True)

    hide_action_button = fields.Selection([('resolution', 'Resolution'), ('timesheet', 'Timesheet')], default='resolution')
    model_no = fields.Char(string='Model No.')
    sltech_state_id = fields.Many2one('res.country.state', domain="[('country_id.code', '=', 'AU')]", string='State')

    @api.multi
    def _delete_archive_tickets(self):
        sixty_back_day_datetime = datetime.now()-timedelta(days=60)
        ticket_ids = self.search([('create_date', '<', sixty_back_day_datetime),
                                  ('state', 'in', ['new']),
                                  ('active', '=', False)])
        for ticket in ticket_ids:
            ticket.unlink()

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if self.env.user.has_group('gt_helpdesk_support_ticket.hd_support_user_access') and \
                not self.env.user.has_group('base.group_system') and \
                not self.env.user.has_group('base.group_erp_manager') and \
                not self.env.user.has_group('gt_helpdesk_support_ticket.hd_support_team_leader_access') and \
                not self.env.user.has_group('gt_helpdesk_support_ticket.hd_customer_access') and \
                not self.env.user.has_group('gt_helpdesk_support_ticket.hd_support_manager_access'):
            domain.append(['state', 'in', ['assigned','work_in', 'closed']])
        res = super(HelpDeskTicket, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
        return res

    # customer = fields.Many2one('res.users', string="Customer")
    parent_ticket = fields.Many2one('helpdesk.ticket', string="Parent Ticket", readonly=True)
    sparepart_ids = fields.One2many('use.spareparts', 'sparepart_id')

    temail_from = fields.Char(string="Email From")
    tpartner_name = fields.Char(string="Customer Name")
    tref = fields.Char(string="Ref")
    serial_no = fields.Char(string="Serial No")
    t_email = fields.Boolean(string="Email Ticket")
    resolution = fields.Text(string="Resolution",  track_visibility='onchange', compute='_get_resolution_name', store=True)
    sh_resolution = fields.Text(string="Resolution",  track_visibility='onchange')
    sltech_state = fields.Selection([
        ('new', 'New'),
        ('assigned', 'Assigned'),
        ('work_in', 'Work in Progress'),
        ('need_info', 'Needs More Info'),
        ('needs_reply', 'Needs Reply'),
        ('reopend', 'Reopened'),
        ('solution', 'Solution Suggested'),
        ('closed', 'Closed'),
    ],compute='_get_state_name',)

    @api.multi
    @api.depends('state')
    def _get_state_name(self):
        self.sltech_state = self.state

    @api.multi
    @api.depends('sheet_ids')
    def _get_resolution_name(self):
        # if not self.resolution:
        #     self = self.search([])
        for rec in self:
            rec.resolution = '\n'.join([x.sh_resolution for x in rec.sheet_ids if x.sh_resolution])

            if len(rec.sheet_ids) != len(rec.tsk_inv_line_ids):
                rec = rec.with_context(write_from_invoice_line=False)
            else:
                for x in rec.tsk_inv_line_ids:
                    if x.timesheet_id.id not in rec.sheet_ids.ids:
                        rec = rec.with_context(write_from_invoice_line=False)
                        break


    # assigned_date = fields.Datetime('Assigned Date')
    event_id = fields.Many2one('calendar.event', 'Event')

    date_time_assigned_date = fields.Datetime('Assigned Date')  #, compute='tf_compute_event_id_start_datetime', store=True)

    fault_area = fields.Char('Fault Area')
    unallocated = fields.Boolean(default=False)

    assigned_date_from = fields.Datetime('Assigned Date')
    assigned_date_to = fields.Datetime('Assigned Date')
    event_button_show = fields.Boolean(default=False)
    invoice_id = fields.Many2one('account.invoice', 'Invoice Number')

    ticket_state_created = fields.Selection([('odoo_ticket', 'Odoo Ticket'),
                                             ('web_ticket', 'Web Ticket'),
                                             ('email_ticket', 'Email Ticket')], 'Ticket Created', default='odoo_ticket')

    # @api.onchange('assi_to')
    def _custom_ticket_domain_assigned_users(self):
        user_ids = self.env['res.users'].search([])
        record = []
        for user in user_ids:
            if user.has_group('base.group_user'):
                record.append(user.id)
        return [('id', 'in', record)]

    assi_to = fields.Many2one('res.users', string="Assigned to", domain=lambda self:self._custom_ticket_domain_assigned_users())

    @api.multi
    def unlink(self):
        for rec in self:
            _logger.info('%s ticket is being deleted ------------------!' % rec.ticket_no)
            message_information = 'Closed Tickets' if len(self)>1 else rec.ticket_no
            if rec.state in ['closed']:
                raise ValidationError('%s can\'t be deleted'%message_information)
        return super(HelpDeskTicket, self).unlink()

    def open_calendarEvent_form(self):
        ir_config_parameter = self.env['ir.config_parameter']
        attachment = self.env['ir.attachment']
        if self.user_has_groups('custom_module.hd_support_team_leader_access'):
            ir_config_parameter = self.env['ir.config_parameter'].sudo()
            attachment = self.env['ir.attachment'].sudo()
        url_domain = ir_config_parameter.search([('key', '=', 'web.base.url')]).value
        attachment_ids = attachment.search([('res_model', '=', 'helpdesk.ticket'),
                                                          ('res_id', '=', self.id),
                                                          ('res_name', '=', self.ticket_no)])
        attachment_link = "\n"

        for res in attachment_ids:
            attachment_link += url_domain + "/web/content/" + str(res.id) + "/" + res.name + "\n"

        return {
            'name': 'Calendar Event',
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.event',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('calendar.view_calendar_event_form').id,
            'target': 'new',
            'context': {'default_ticket_id': self.id,
                        'default_description': self.description + "\n" + attachment_link,
                        'default_event_time': True,
                        'default_duration': 1.0,
                        'tf_open_poup': True,
                        'default_name': self.ticket_no}
        }

    @api.constrains('state')
    def apply_status_contrains(self):
        if not (self.env.user.has_group('base.group_system') or self.env.user.has_group('custom_module.hd_support_team_leader_access')):
            if self.state == 'reopend':
                raise ValidationError('%s has no access right to change the status Reopen!\n Please Contact Administrator for this!'%self.env.user.name)

        if self.state == 'closed':
            if not len(self.sheet_ids):
                raise ValidationError('Please fill Timesheet!')

    @api.multi
    def write(self, vals):
        for rec_wr in self:
            if rec_wr.unallocated and vals.get('assi_to', False):
                mail_template_id = rec_wr.env.ref('custom_module.ticket_unallocated_email_template', False)
                mail_template_id.with_context(
                    {'email_to': rec_wr.assi_to.email,
                     'ticket_nm': vals.get('ticket_title'),
                     'username': rec_wr.assi_to.name}).send_mail(
                    rec_wr.id, force_send=True)
            vals['unallocated'] = True

            result = super(HelpDeskTicket, rec_wr).write(vals)

            # if vals.get('state') == 'assigned':
            #     if rec_wr.event_id:
            #         rec_wr.env['google.calendar'].with_context(rec_wr._context).synchronize_events()


            if not rec_wr._context.get('stop_update_event_field', False):
                # for rec in self:
                rec_wr = rec_wr.with_context(stop_update_event_field=True)
                tf_event_id = self.env['calendar.event'].sudo().search([('ticket_id', '=', rec_wr.id)])
                for evnt in tf_event_id:
                    if evnt.start_datetime:
                        rec_wr.date_time_assigned_date = str(evnt.start_datetime)


            if not rec_wr._context.get('stop_update_event_field1', False):
                rec_wr = rec_wr.with_context(stop_update_event_field1=True)
                if 'event_id' in vals.keys() and vals.get('event_id') == False:
                    rec_wr.date_time_assigned_date = ""

            invoice_data = []
            rec_wr = rec_wr.with_context(write_from_invoice_line=True)

            if len(rec_wr.sheet_ids) != len(rec_wr.tsk_inv_line_ids):
                rec_wr = rec_wr.with_context(write_from_invoice_line=False)
            else:
                for x in rec_wr.tsk_inv_line_ids:
                    if x.timesheet_id.id not in rec_wr.sheet_ids.ids:
                        rec_wr = rec_wr.with_context(write_from_invoice_line=False)
                        break

            if rec_wr._context.get('write_from_invoice_line', False):
                for sheet in rec_wr.sheet_ids:
                    price_unit = sheet.product_id.lst_price
                    line = rec_wr.tsk_inv_line_ids.filtered(lambda obj: obj.timesheet_id.id == sheet.id)
                    if line:

                        # if sheet line product is changed then we need to change the invoice line unit price
                        if line.product_id.id != sheet.product_id.id:
                            line.unit_price = price_unit

                        price_unit = line.unit_price
                    invoice_data.append((0, 0, dict(
                        helpdesk_inv_ids=rec_wr.id,
                        product_id=sheet.product_id.id,
                        description=sheet.timesheet_description,
                        qty=sheet.hours,
                        unit_price=price_unit,
                        uom=sheet.product_id.uom_id.id,
                        amt=sheet.product_id.lst_price * sheet.hours,
                        inv_tax=sheet.product_id.taxes_id and sheet.product_id.taxes_id[0].id,
                        sltech_resolution=sheet.sh_resolution,
                        timesheet_id=sheet.id,
                    )))
            else:
                for sheet in rec_wr.sheet_ids:
                    price_unit = sheet.product_id.lst_price
                    line = rec_wr.tsk_inv_line_ids.filtered(lambda obj: obj.timesheet_id.id == sheet.id)
                    if line:
                        price_unit = line.unit_price
                    invoice_data.append((0, 0, dict(
                        helpdesk_inv_ids=rec_wr.id,
                        product_id=sheet.product_id.id,
                        description=sheet.timesheet_description,
                        qty=sheet.hours,
                        unit_price=price_unit,
                        uom=sheet.product_id.uom_id.id,
                        amt=sheet.product_id.lst_price * sheet.hours,
                        inv_tax=sheet.product_id.taxes_id and sheet.product_id.taxes_id[0].id,
                        sltech_resolution=sheet.sh_resolution,
                        timesheet_id=sheet.id,
                    )))

            if invoice_data and not rec_wr._context.get('stop_update', False):
                if not rec_wr._context.get('stop_delete_update', False):
                    rec_wr = rec_wr.with_context(stop_delete_update=True)
                    invoice_data.insert(0, (5, 0, 0))

                rec_wr = rec_wr.with_context(stop_update=True)
                # if len(rec_wr.sheet_ids) != len(rec_wr.tsk_inv_line_ids):
                rec_wr.tsk_inv_line_ids = invoice_data
                for line in rec_wr.tsk_inv_line_ids:
                    line.compute_price()
            return result

    @api.one
    def helpdesk_invoice(self):
        # dt_date = str(self.create_date)
        dt_date = datetime.now()
        rec_date = dt_date.replace(second=0, microsecond=0)
        final_date = datetime.strptime(str(rec_date), "%Y-%m-%d %H:%M:%S").date()
        invoice_obj = self.env['account.invoice']
        inv_fields = invoice_obj.fields_get()
        default_value = invoice_obj.default_get(inv_fields)

        invoice_line = self.env['account.invoice.line']
        line_f = invoice_line.fields_get()
        default_line = invoice_line.default_get(line_f)

        default_value.update({'partner_id': self.customer.id, 'date_invoice': final_date,
                              'user_id': self.assi_to.id})
        invoice = invoice_obj.new(default_value)
        invoice._onchange_partner_id()
        default_value.update({'account_id': invoice.account_id.id, 'date_due': invoice.date_due})
        inv_id = invoice.create(default_value)

        invoicing_lines = []
        for invce_lst in self.tsk_inv_line_ids:
            tax_ids = [tax.id for tax in invce_lst.inv_tax]
            invoicing_lines.append({
                'invoice_id': inv_id.id,
                'product_id': invce_lst.product_id.id,
                'name': invce_lst.description,
                'account_analytic_id': invce_lst.ac_analytic_id.id,
                'quantity': invce_lst.qty,
                'price_unit': invce_lst.unit_price,
                # 'account_analytic_id': invoice_lst.ac_analytic_id.id,
                'invoice_line_tax_ids': tax_ids,
                'resolution': invce_lst.sltech_resolution,
            })
        for parts_line in self.sparepart_ids:
            tax_ids = [tax.id for tax in parts_line.product_id.taxes_id]
            invoicing_lines.append({
                'invoice_id': inv_id.id,
                'product_id': parts_line.product_id.id,
                'name': parts_line.product_id.name,
                'account_analytic_id': False,
                'quantity': parts_line.qty_used,
                'price_unit': parts_line.product_id.list_price,
                # 'account_analytic_id': invoice_lst.ac_analytic_id.id,
                'invoice_line_tax_ids': tax_ids,
            })

        for invoice_lst in invoicing_lines:
            # tax_ids = [tax.id for tax in invoice_lst.inv_tax]
            # print "::::::::::::::::::::::::::::::::::::taxess:::::::",tax_ids
            default_line.update({
                'invoice_id': inv_id.id,
                'product_id': invoice_lst['product_id'],
                'name': invoice_lst['name'],
                'account_analytic_id': invoice_lst['account_analytic_id'],
                'quantity': invoice_lst['quantity'],
                'price_unit': invoice_lst['price_unit'],
                # 'account_analytic_id': invoice_lst.ac_analytic_id.id,
                'invoice_line_tax_ids': [(6, 0, invoice_lst['invoice_line_tax_ids'])],
            })
            inv_line = invoice_line.new(default_line)
            inv_line._onchange_product_id()
            default_line.update({'invoice_id': inv_id.id,
                                 'account_id': inv_line.with_context(
                                     {'journal_id': inv_id.journal_id.id})._default_account()})

            invoice_line.create(default_line)
        inv_id.amount_tax = sum(
            [sum([(sum([tax.amount for tax in line.invoice_line_tax_ids]) * line.price_subtotal) / 100]) for line in
             inv_id.invoice_line_ids])
        inv_id.amount_total = inv_id.amount_tax + sum([line.price_subtotal for line in inv_id.invoice_line_ids])
            # inv_id.action_invoice_open()
            #
            # template_obj = self.env.ref('account.email_template_edi_invoice', False)
            # template_obj.send_mail(inv_id.id)
        self.invoice_id = inv_id.id
        return True

    # resolution fill validationerror
    @api.onchange('state')
    def onchange_state(self):
        ticket_id = self.browse(self._origin.id)
        if self.state == 'closed' and not self.resolution:
            raise ValidationError('Please fill resolution!')
        if not (self.env.user.has_group('base.group_system') or self.env.user.has_group('custom_module.hd_support_team_leader_access')):
            if ticket_id.state == 'work_in' and self.state == 'assigned':
                raise ValidationError("Yon can't change state from WORK IN PROGRESS to ASSIGNED!")
            # if ticket_id.state == 'work_in' and self.state == 'closed':
            #     raise ValidationError("Yon can't change state from WORK IN PROGRESS to CLOSED!")
            if ticket_id.state == 'work_in' and self.state == 'reopend':
                raise ValidationError("Yon can't change state from WORK IN PROGRESS to REOPENED!")
            if ticket_id.state == 'assigned' and self.state == 'reopend':
                raise ValidationError("Yon can't change state from ASSIGNED to REOPENED!")
            if ticket_id.state == 'new' and self.state == 'reopend':
                raise ValidationError("Yon can't change state from NEW to REOPENED!")
            if ticket_id.state == 'reopend' and self.state == 'new':
                raise ValidationError("Yon can't change state from REOPENED to NEW!")
            if ticket_id.state == 'reopend' and self.state == 'assigned':
                raise ValidationError("Yon can't change state from REOPENED to ASSIGNED!")
            if ticket_id.state == 'reopend' and self.state == 'work_in':
                raise ValidationError("Yon can't change state from REOPENED to WORK IN PROGRESS!")
            if ticket_id.state == 'reopend' and self.state == 'closed':
                raise ValidationError("Yon can't change state from REOPENED to CLOSED!")
            if ticket_id.state == 'work_in' and self.state == 'new':
                raise ValidationError("Yon can't change state from WORK IN PROGRESS to NEW!")
            if ticket_id.state == 'assigned' and self.state == 'new':
                raise ValidationError("Yon can't change state from ASSIGNED to NEW!")
            if ticket_id.state == 'reopend' and self.state == 'new':
                raise ValidationError("Yon can't change state from REOPENED to NEW!")
            if ticket_id.state == 'closed' and self.state == 'new':
                raise ValidationError("Yon can't change state from CLOSED to NEW!")
        # if self.state == 'assigned' and not self.assigned_date:
        #     raise ValidationError('Please fill Assigned Date ')
        # return super(HelpDeskTicket, self).write(vals)

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        fields = super(HelpDeskTicket, self).fields_get(allfields=allfields, attributes=attributes)
        if not self.user_has_groups('gt_helpdesk_support_ticket.hd_support_manager_access'):
            if 'assi_to' in fields:
                fields['assi_to']['readonly'] = True
        if self.user_has_groups('custom_module.hd_support_team_leader_access'):
            if 'assi_to' in fields:
                fields['assi_to']['readonly'] = False
        if self.user_has_groups('custom_module.hd_support_contractor_access'):
            if 'customer' in fields:
                fields['customer']['readonly'] = True
        if not self.user_has_groups('base.group_system'):
            # if 'assi_to' in fields:
            #     fields['assi_to']['readonly'] = True
            if 'tf_created_by' in fields:
                fields['tf_created_by']['readonly'] = True
            if 'ticket_title' in fields:
                fields['ticket_title']['readonly'] = True
            if 'helpdesk_team' in fields:
                fields['helpdesk_team']['readonly'] = True
            if 'customer' in fields:
                fields['customer']['readonly'] = True
            if 'phone' in fields:
                fields['phone']['readonly'] = True
            if 'priority' in fields:
                fields['priority']['readonly'] = True
            if 'close_date' in fields:
                fields['close_date']['readonly'] = True
            if 'description' in fields:
                fields['description']['readonly'] = True
            if 't_email' in fields:
                fields['t_email']['readonly'] = True
            if 'ticket_close' in fields:
                fields['ticket_close']['readonly'] = True
            if 'sheet_ids' in fields:
                fields['sheet_ids']['readonly'] = True
            if 'sparepart_ids' in fields:
                fields['sparepart_ids']['readonly'] = True
            if 'temail_from' in fields:
                fields['temail_from']['readonly'] = True
            if 'tpartner_name' in fields:
                fields['tpartner_name']['readonly'] = True
            if 'tref' in fields:
                fields['tref']['readonly'] = True
            if 'serial_no' in fields:
                fields['serial_no']['readonly'] = True
            if 'fault_area' in fields:
                fields['fault_area']['readonly'] = True
        return fields

    @api.model
    def message_new(self, msg, custom_values=None):
        """ Create new support ticket upon receiving new email"""

        defaults = {
            'ticket_title': msg.get('subject')}  # {'support_email': msg.get('to'), 'ticket_title': msg.get('subject')}

        # Extract the name from the from email if you can
        if "<" in msg.get('from') and ">" in msg.get('from'):
            start = msg.get('from').rindex("<") + 1
            end = msg.get('from').rindex(">", start)
            from_email = msg.get('from')[start:end]
            from_name = msg.get('from').split("<")[0].strip()
            # defaults['person_name'] = from_name
            # part_id = self.env['res.partner'].sudo().search([('email', '=', from_email)])
            part_id = self.env['res.partner'].sudo().search([]).filtered(lambda self:self.email and
                                                                                     from_email and
                                                                                     self.email.upper() == from_email.upper())
            if not part_id:
                part_id = self.env['res.partner'].sudo().create({'name': from_name, 'email': from_email})
            if part_id:
                part_id = part_id[0]


            # take title from category
            login_partner_id = part_id
            tf_ticket_title = ""
            if login_partner_id.category_id:
                tf_ticket_title = login_partner_id.category_id[0].tf_ticket_title
                defaults = {
                    'ticket_title': tf_ticket_title}
            # end

            defaults['customer'] = part_id.id
        else:
            from_email = msg.get('from')

        defaults['temail_from'] = from_email
        defaults['email_id'] = from_email
        defaults['t_email'] = True
        defaults['assi_to'] = self.env.ref('base.user_admin').id
        defaults['ticket_state_created'] = 'email_ticket'
        # #Sachin Burnawal
        # from bs4 import BeautifulSoup as bs
        # html = msg['body']
        # soup = bs(html)
        # tds = soup.find_all('span')
        # defaults['tpartner_name'] = tds[0].contents[0].split('\n')[0]

        # Try to find the partner using the from email
        # search_partner = self.env['res.partner'].sudo().search([('email', '=', from_email)])
        # if len(search_partner) > 0:
        #     defaults['partner_id'] = search_partner[0].id
        #     defaults['person_name'] = search_partner[0].name

        # defaults['description'] = tools.html_sanitize(msg.get('body'))
        import html2text
        defaults['description'] = html2text.html2text(msg.get('body'))
        cnt = 0
        for line in html2text.html2text(msg.get('body')).split('\n'):
            cnt += 1
            # if cnt == 3:
            print('gottttttttttt----%s' % line)
            print('line---cnt-%s' % cnt)
            if line.find('Serial No.:') != -1:
                defaults['serial_no'] = line.split('Serial No.:')[1]
            # if line.find('Serial No.: ') != 1:
            #     defaults['serial_no'] = line.find('Serial No.: ')[1]

            if line.find('Ref.:') != -1:
                defaults['tref'] = line.split('Ref.:')[1]
            elif line.find('Ref.: ') != -1:
                defaults['tref'] = line.split('Ref.: ')[1]
            if line.find('Fault Area:') != -1:
                # defaults['fault_area'] = line.split('Fault Area:')[
                #     1]  # '' if line.split('Fault Area:')[1] == '-' else line.split('Fault Area:')[1]
                temp_f = defaults['description'].find('Fault Area:')
                temp_fault_area = defaults['description'][temp_f:]
                if len(temp_fault_area.split('.')) > 0:
                    defaults['fault_area'] = temp_fault_area.split('.')[0].replace('\n', ' ')[11:]
                else:
                    defaults['fault_area'] = ''
            if cnt == 6:
                defaults['tpartner_name'] = line
        # defaults['description']= html2text.html2text(msg.get('body').rindex( "ref" ))

        # #Assign to default category
        # setting_email_default_category_id = self.env['ir.default'].get('website.support.settings', 'email_default_category_id')
        #
        # if setting_email_default_category_id:
        #     defaults['category_id'] = setting_email_default_category_id

        return super(HelpDeskTicket, self).message_new(msg, custom_values=defaults)

    @api.multi
    def create_sub_ticket(self):
        existed_child_id = self.sudo().search([('parent_ticket', '=', self.id)])
        if len(existed_child_id):
            child_no = int(len(existed_child_id)) + 1
        else:
            child_no = 1
        ticket_no = self.ticket_no + '-' + str(child_no)
        tid = self.create(
            {'parent_ticket': self.id,
             'ticket_no': ticket_no,
             'assi_to': self.assi_to.id,
             # 'email_to': self.assi_to.partner_id.email,
             'customer': self.customer.id})
        tid.ticket_no = ticket_no
        view_ref = self.env['ir.model.data'].get_object_reference('gt_helpdesk_support_ticket', 'helpdesk_form_views')
        view_id = view_ref[1] if view_ref else False
        res = {
            'type': 'ir.actions.act_window',
            'name': _('Project Task'),
            'res_model': 'helpdesk.ticket',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_id': tid.id,
            'target': 'current'
        }

        return res

    def open_resolution(self):
        return {
            'name': 'Resolution',
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.ticket.resolution',
            'view_mode': 'form',
            'view_type': 'form',
            # 'view_id': self.env.ref('calendar.view_calendar_event_form').id,
            'target': 'new',
            'context': {'ticket_id': self.id}
        }

    def open_timesheet(self):
        return {
            'name': 'Timesheet & Resolution',
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.timesheet',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('custom_module.helpdesk_timesheet_form').id,
            'target': 'new',
            'context': {'default_helpdesk_ids': self.id}
        }

    is_email_send = fields.Boolean(default=False, string='Is Submitted')
    email_send_count = fields.Integer(default=1, string='Email Send Count')

    def action_closed_ticket_email_send(self):
        for rec_wr in self:
            cust_email_to = rec_wr.customer.email
            email_cc = ""
            if rec_wr.customer:
                if rec_wr.customer.category_id:
                    cust_email_to = rec_wr.customer.category_id[0].name

                    count = 1
                    for categ_cc in rec_wr.customer.category_id:
                        if count == 1:
                            email_cc += categ_cc.name
                        elif count > 1:
                            email_cc += "," + categ_cc.name

                        count += 1
            if rec_wr.state == 'closed':
                mail_template_id = self.env.ref('gt_helpdesk_support_ticket.ticket_closed', False)

                mail_template_id.with_context({'email_to': cust_email_to, 'ticket_nm': rec_wr.ticket_title,
                                               'email_cc': email_cc}).send_mail(rec_wr.id, force_send=True)
                rec_wr.update({
                    'is_email_send': True,
                    'email_send_count': rec_wr.email_send_count + 1,
                })

    def action_closed_ticket_email(self):
        for rec_wr in self:
            if rec_wr.email_send_count > 1:
                email_send_count_char = self.ordinal_suffix(rec_wr.email_send_count)
                return {
                    'name': 'Warning',
                    'type': 'ir.actions.act_window',
                    'res_model': 'custom.popup',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'view_id': self.env.ref('custom_module.custom_view_popup').id,
                    'target': 'new',
                    'context': {'default_helpdesk_ticket_id': self.id,
                                'default_email_send_count_char': email_send_count_char,
                                'default_email_send_count': self.email_send_count}
                }
            else:
                self.action_closed_ticket_email_send()

    def action_closed_ticket_email_mobile(self):
        return self.action_closed_ticket_email()

    def ordinal_suffix(self, number):
        if 10 <= number % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(number % 10, 'th')
        return str(number) + suffix


class CustomPopup(models.Model):
    _name = 'custom.popup'

    email_send_count_char = fields.Char(string='Email Send Count')
    email_send_count = fields.Integer(related='helpdesk_ticket_id.email_send_count')
    helpdesk_ticket_id = fields.Many2one('helpdesk.ticket', string='Helpdesk Ticket')

    def action_ok(self):
        if self.helpdesk_ticket_id:
            self.helpdesk_ticket_id.action_closed_ticket_email_send()




class Helpedesk_Team_Members(models.Model):
    _inherit = 'helpdesk.timesheet'

    def compute_datetime_now(self):
        if self.env.ref('base.partner_admin').sudo().tz:
            return datetime.strptime(datetime.now(pytz.timezone(self.env.ref('base.partner_admin').sudo().tz)).strftime(
                tools.DEFAULT_SERVER_DATETIME_FORMAT), '%Y-%m-%d %H:%M:%S').date()
        else:
            return date.today()

    timesheet_date = fields.Date(string='Date', default=compute_datetime_now)
    product_id = fields.Many2one('product.product', string="Product")
    sh_resolution = fields.Text('Resolution')

    @api.onchange('product_id')
    def domain_product_id(self):
        for rec in self:
            if rec.product_id:
                rec.timesheet_description = rec.product_id.name
        # record = self.env['product.product'].search(
        #     [('categ_id', '!=', self.env.ref('custom_module.spareparts_product_category').id)])
        return {
            'domain': {
                'product_id': [('categ_id', '!=', self.env.ref('custom_module.spareparts_product_category').id)]
            }}

    def common_function_ticket(self):
        # res = super(Resolution, self).create(vals)
        ticket_id = self._context.get('active_id')
        if ticket_id:
            # ticket_id = self.env['helpdesk.ticket'].browse(ticket_id)
            # ticket_id.hide_action_button = 'timesheet'

            ticket_id = self.env['helpdesk.ticket'].browse(ticket_id)
            ticket_id.sh_resolution = self.sh_resolution

    # @api.model
    def save_record(self):
        self.common_function_ticket()
        return {'type': 'ir.actions.act_window_close'}
        # return res

    def add_another(self):
        self.common_function_ticket()
        return {
            'name': 'Timesheet & Resolution',
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.timesheet',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('custom_module.helpdesk_timesheet_form').id,
            'target': 'new',
            'context': {
                'default_helpdesk_ids': self._context.get('active_id'),
                'default_sh_resolution': self.sh_resolution,
                'active_id': self._context.get('active_id')
            }
        }

class use_spareparts(models.Model):
    _name = 'use.spareparts'

    product_id = fields.Many2one('product.product', string="Part Number")

    @api.onchange('product_id')
    def domain_spare_parts(self):
        # record = self.env['product.product'].search(
        #     [('categ_id', '=', self.env.ref('custom_module.spareparts_product_category').id)])
        return {
            'domain': {
                'product_id': [('categ_id', '=', self.env.ref('custom_module.spareparts_product_category').id)]
            }}

    qty_used = fields.Float(string="Qty Used")
    state = fields.Selection([
        ('used', 'used'),
        ('unused', 'Unused'),
        ('returned', 'Returned'),
        ('required', 'Required')
    ], string='Status')
    sparepart_id = fields.Many2one('helpdesk.ticket')

class SparepartsProduct(models.Model):
    _inherit = "product.product"

    lst_price = fields.Float(
        'Sale Price', compute='_compute_product_lst_price',
        digits=dp.get_precision('Product Price'), inverse='_set_product_lst_price', track_visibility='onchange',
        help="The sale price is managed from the product template. Click on the 'Configure Variants' button to set the extra attribute prices.")

    @api.model
    def default_get(self, fields):
        rec = super(SparepartsProduct, self).default_get(fields)
        if self._context.get('spareparts', False):
            rec.update(dict(
                categ_id = self.env.ref('custom_module.spareparts_product_category').id,
            ))
        return rec

class SparepartsProductTemplate(models.Model):
    _inherit = "product.template"

    lst_price = fields.Float(
        'Public Price', related='list_price', readonly=False,
        digits=dp.get_precision('Product Price'), track_visibility='onchange')

class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    ticket_id = fields.Many2one('helpdesk.ticket')

    @api.multi
    def unlink(self):
        res = super(CalendarEvent, self).unlink()

        return res

    # @api.multi
    # @api.depends('allday', 'start', 'stop')
    # def _compute_dates(self):
    #     rec = super(CalendarEvent, self)._compute_dates()
    #     for meeting in self:
    #         if meeting._context.get('default_event_time', False):
    #             meeting.start_datetime = datetime.now()+timedelta(days=1)
    #             meeting.duration = 1.0

    @api.model
    def create(self, vals):
        res = super(CalendarEvent, self).create(vals)
        if res.ticket_id:
            res.ticket_id.event_button_show = True
            res.ticket_id.event_id = res.id
            res.ticket_id.assigned_date_from = res.start
            res.ticket_id.assigned_date_to = res.stop
            # self.env['google.calendar'].with_context(self._context).synchronize_events()
        return res

    @api.multi
    def write(self, vals):
        res = super(CalendarEvent, self).write(vals)
        for rec in self:
            if rec.ticket_id:
                if rec.start:
                    rec.ticket_id.assigned_date_from = rec.start
                if rec.stop:
                    rec.ticket_id.assigned_date_to = rec.stop
            # self.env['google.calendar'].with_context(self._context).synchronize_events()
        return res

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.ticket_id:
                rec.ticket_id = rec.ticket_id.with_context(stop_update_event_field=True)
                rec.ticket_id.write(dict(event_button_show = False,event_id=False))
        return super(CalendarEvent, self).unlink()

    @api.onchange('start_datetime', 'duration')
    def _onchange_duration(self):
        res = super(CalendarEvent, self)._onchange_duration()
        if self._context.get('tf_open_poup'):
            self.duration = self._context.get('default_duration')
        return res

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    ticket_title = fields.Char('Ticket Title')
    send_and_print = fields.Boolean()
    ticket_inv_line_ids = fields.Many2many('helpdesk.invoice.line')
    consolidated_invoice_line = fields.Char(string='Consolidated Invoice Line')
    consolidated_invoice_note = fields.Text(string='Consolidated Invoice Note')
    sltech_months = fields.Selection([
        ('jan', 'January'),
        ('feb', 'February'),
        ('mar', 'March'),
        ('apr', 'April'),
        ('may', 'May'),
        ('jun', 'June'),
        ('jul', 'July'),
        ('aug', 'August'),
        ('sep', 'September'),
        ('oct', 'October'),
        ('nov', 'November'),
        ('dec', 'December'),
    ],string='Month')

    sltech_years = fields.Char(string='Year')
    active = fields.Boolean(string='Active',default=True)
    helpdesk_inv_ids = fields.One2many('helpdesk.invoice.line','invoice_id',string='Helpdesk Invoice Line')
    due_amount = fields.Monetary(string='Due Amount', compute='get_invoice_due_amount')

    def generate_invoice_xlsx(self):
        return self.env.ref('custom_module.sltech_pos_excel_report_invoice_xlsx_helpdesk').report_action(self)

    def consolidated_invoice_report(self):
        return self.env.ref('custom_module.custom_account_invoices_without_payment').report_action(self)

    def get_invoice_due_amount(self):
        for rec in self:
            amount = rec.amount_total - sum(rec.payment_ids.mapped('amount'))
            rec.due_amount = amount


class ActionInvoiceSend(models.TransientModel):
    _inherit = 'account.invoice.send'

    @api.multi
    def send_and_print_action(self):
        self.invoice_ids.send_and_print = True
        return super(ActionInvoiceSend, self).send_and_print_action()


class HelpedeskTeamMemberslines(models.Model):
    _inherit = 'helpdesk.invoice.line'

    ticket_create_date = fields.Datetime('Create Date', related='helpdesk_inv_ids.create_date')
    ticket_fault_area = fields.Char('Fault Area', related='helpdesk_inv_ids.fault_area')
    serial_no = fields.Char('Serial No', related='helpdesk_inv_ids.serial_no')
    tref = fields.Char('Ref', related='helpdesk_inv_ids.tref')
    tpartner_name = fields.Char('Customer Name', related='helpdesk_inv_ids.tpartner_name')
    resolution = fields.Text('Resolution', related='helpdesk_inv_ids.resolution')
    state = fields.Selection('Status', related='helpdesk_inv_ids.state')
    close_date = fields.Datetime('Close Date', related='helpdesk_inv_ids.close_date')
    assi_to = fields.Many2one('res.users', 'Assigned To', related='helpdesk_inv_ids.assi_to')
    sltech_resolution = fields.Text('Ticket Line Resolution', store=True)
    ticket_title = fields.Char('Ticket Title', related='helpdesk_inv_ids.ticket_title', store=True)

    status = fields.Boolean(default=False, help='To check whether the line is invoiced or not!')

    invoice_id = fields.Many2one('account.invoice',string='Invoice')
    timesheet_id = fields.Many2one('helpdesk.timesheet',string='Timesheet')
    is_email_send = fields.Boolean(related='helpdesk_inv_ids.is_email_send', store=True)




class Resolution(models.TransientModel):
    _name = "helpdesk.ticket.resolution"
    _description = "Resolution"

    name = fields.Text('Resolution', required=True)

    # @api.model
    def save_record(self):
        # res = super(Resolution, self).create(vals)
        ticket_id = self._context.get('active_id')
        if ticket_id:
            ticket_id = self.env['helpdesk.ticket'].browse(ticket_id)
            ticket_id.resolution = self.name
            invoice_line_ids = self.env['helpdesk.invoice.line'].search([('helpdesk_inv_ids', '=', ticket_id.id)],order='id desc',limit=1)
            timesheet_ids = self.env['helpdesk.timesheet'].search([('helpdesk_ids', '=', ticket_id.id)],order='id desc',limit=1)
            print(invoice_line_ids)
            if invoice_line_ids:
                invoice_line_ids.sltech_resolution = self.name
            if timesheet_ids:
                timesheet_ids.sltech_resolution = self.name

            ticket_id.hide_action_button = 'resolution'

            return {'type': 'ir.actions.act_window_close'}
        # return res



class PartnerXlsxoiu7(models.AbstractModel):
    _name = 'report.custom_module.print_sample_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):

        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': 1})
        line_index = 2
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 32)
        worksheet.set_column('C:C', 18)
        worksheet.set_column('D:D', 12)
        worksheet.set_column('E:E', 45)
        worksheet.set_column('F:F', 16)
        worksheet.set_column('G:G', 16)
        worksheet.set_column('H:H', 10)
        worksheet.set_column('I:I', 25)
        worksheet.set_column('J:J', 25)
        worksheet.set_column('K:K', 25)
        worksheet.set_column('L:L', 25)
        worksheet.set_column('M:M', 25)
        worksheet.set_column('N:N', 25)
        worksheet.set_column('O:O', 25)
        worksheet.write('A1', _('Invoice No'))
        worksheet.write('B1', _('Ref'))
        worksheet.write('C1', _('Helpdesk Inv/Ticket No'))
        worksheet.write('D1', _('Helpdesk Inv/Ticket Title'))
        worksheet.write('E1', _('Customer Name'))
        worksheet.write('F1', _('Serial No'))
        worksheet.write('G1', _('Description'))
        worksheet.write('H1', _('Create Date'))
        worksheet.write('I1', _('Close Date'))
        worksheet.write('J1', _('Unit Price'))
        worksheet.write('K1', _('Quantity'))
        worksheet.write('L1', _('Net Amount'))
        worksheet.write('M1', _('Tax Amount'),)
        worksheet.write('N1', _('Amount'),)
        worksheet.write('O1', _('Status'),)
        worksheet.write('P1', _('Fault Area'),)
        worksheet.write('Q1', _('Resolution'),)
        # total_price_unit = 0
        total_net_amount = 0
        total_tax_amount = 0
        total_amount = 0
        temp = {}
        for helpdesk in obj.helpdesk_inv_ids:
            if helpdesk.timesheet_id:
                timesheet_date = str(helpdesk.timesheet_id.timesheet_date.strftime("%d-%m-%Y %H:%M:%S"))
            else:
                # timesheet_id = self.env['helpdesk.timesheet'].sudo().search([('product_id','=',helpdesk.product_id.id),
                #                                                              ('timesheet_description','=',helpdesk.description),
                #                                                              ('hours','=',helpdesk.qty),
                #                                                              ('sltech_resolution','=',helpdesk.sltech_resolution),
                #                                                              ('create_uid','=',helpdesk.create_uid.id),
                #                                                              ('helpdesk_ids','=',helpdesk.helpdesk_inv_ids.id)])
                timesheet_id = self.env['helpdesk.timesheet'].sudo().search([('product_id','=',helpdesk.product_id.id),
                                                                            ('helpdesk_ids','=',helpdesk.helpdesk_inv_ids.id)])
                if helpdesk.helpdesk_inv_ids.id not in temp:
                    temp[(str(helpdesk.helpdesk_inv_ids.id) + str(helpdesk.product_id.id))] = timesheet_id.ids




                if timesheet_id:
                    try:
                        timesheet_id_x = timesheet_id.filtered(
                            lambda obj: obj.id == temp[(str(helpdesk.helpdesk_inv_ids.id) + str(helpdesk.product_id.id))][0])
                        timesheet_date = str(timesheet_id_x[0].timesheet_date.strftime("%d-%m-%Y %H:%M:%S"))
                        del temp[(str(helpdesk.helpdesk_inv_ids.id) + str(helpdesk.product_id.id))][0]
                        if not temp[(str(helpdesk.helpdesk_inv_ids.id) + str(helpdesk.product_id.id))]:
                            del temp[(str(helpdesk.helpdesk_inv_ids.id) + str(helpdesk.product_id.id))]

                    except:
                        pass
                else:
                    timesheet_date = ''
                # for timesheet in helpdesk.helpdesk_inv_ids.sheet_ids:
            worksheet.write('A%s' % line_index, str(helpdesk.invoice_id.number or ''))
            worksheet.write('B%s' % line_index, str(helpdesk.tref or ''))
            worksheet.write('C%s' % line_index, str(helpdesk.helpdesk_inv_ids.display_name or ''))
            worksheet.write('D%s' % line_index, str(helpdesk.ticket_title or ''))
            worksheet.write('E%s' % line_index, str(helpdesk.helpdesk_inv_ids.tpartner_name or ''))
            worksheet.write('F%s' % line_index, str(helpdesk.serial_no or ''))
            worksheet.write('G%s' % line_index, str(helpdesk.description or ''))
            worksheet.write('H%s' % line_index, helpdesk.helpdesk_inv_ids.create_date and str(helpdesk.helpdesk_inv_ids.create_date.strftime("%d-%m-%Y %H:%M:%S") or ''))
            worksheet.write('I%s' % line_index, timesheet_date)
            worksheet.write('J%s' % line_index, '$'+str(("{0:.2f}".format(helpdesk.unit_price)) or 0))
            worksheet.write('K%s' % line_index, str(helpdesk.qty or 0.00))
            worksheet.write('L%s' % line_index, '$'+str(("{0:.2f}".format(helpdesk.sltech_net_amount)) or 0.00))
            worksheet.write('M%s' % line_index, '$'+str(("{0:.2f}".format(helpdesk.tax_amt)) or 0.00))
            worksheet.write('N%s' % line_index, '$'+str(("{0:.2f}".format(helpdesk.amt)) or 0.00))
            worksheet.write('O%s' % line_index, str(dict(helpdesk.helpdesk_inv_ids._fields['state'].selection).get(helpdesk.helpdesk_inv_ids.state) or ''))
            worksheet.write('P%s' % line_index, str(helpdesk.ticket_fault_area or ''))
            worksheet.write('Q%s' % line_index, str(helpdesk.sltech_resolution or ''))
            # total_price_unit += helpdesk.unit_price
            total_net_amount += helpdesk.sltech_net_amount
            total_tax_amount += helpdesk.tax_amt
            total_amount += helpdesk.amt
            line_index +=1
        worksheet.write(line_index-1, 0, 'Total', bold)
        # worksheet.write(line_index-1, 9, '$'+str(("{0:.2f}".format(total_price_unit))))
        worksheet.write(line_index-1, 11, '$'+str(("{0:.2f}".format(total_net_amount))))
        worksheet.write(line_index-1, 12, '$'+str(("{0:.2f}".format(total_tax_amount))))
        worksheet.write(line_index-1, 13, '$'+str(("{0:.2f}".format(total_amount))))

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_validate_invoice_payment(self):
        res = super(AccountPayment, self).action_validate_invoice_payment()
        for rec in self:
            for inv_id in rec.invoice_ids:
                inv_id.send_and_print = False
        return res

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.register.payments'

    def create_payments(self):
        res = super(AccountPaymentRegister, self).create_payments()
        for rec in self:
            for inv_id in rec.invoice_ids:
                inv_id.send_and_print = False
        return res