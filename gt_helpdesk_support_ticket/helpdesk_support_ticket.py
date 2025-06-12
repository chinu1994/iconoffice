# -*- coding: utf-8 -*-
##############################################################################
#
#    Globalteckz Pvt Ltd
#    Copyright (C) 2013-Today(www.globalteckz.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime, timedelta
import time
from openerp.exceptions import UserError, ValidationError
#from datetime import  timedelta
from dateutil.relativedelta import relativedelta
from datetime import date
from calendar import monthrange
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import models, tools, fields, api, _
from odoo.exceptions import UserError, AccessError
import json, sys, base64, pytz
from odoo.osv import expression

AVAILABLE_PRIORITIES = [
    ('0', 'Normal'),
    ('1', 'Low'),
    ('2', 'High'),
    ('3', 'Very High'),
]

class ResUsers(models.Model):
    _inherit = "res.users"

    tf_user_code = fields.Char('User Code')

    # @api.multi
    # def name_get(self):
    #     # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
    #     # self.browse(self.ids).read(['name'])
    #     # return super(ResUsers, self).name_get()
    #     return [(template.id, '%s%s' % (template.tf_user_code and '[%s] ' % template.tf_user_code or '',
    #                                     template.name and '[%s] ' % template.name or ''))
    #             for template in self]

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        domain = args or []
        domain = expression.AND([domain, ['|', ('name', operator, name), ('tf_user_code', operator, name)]])
        rec = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(rec).name_get()



class PartnerTags(models.Model):
    _inherit = "res.partner.category"

    tf_ticket_title = fields.Char('Ticket Title')

class Helpedesk_Ticket(models.Model):
    _name = 'helpdesk.ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _inherit = ['mail.thread']
    _mail_mass_mailing = 'Helpdesk Ticket'
    _rec_name='ticket_no'

    ticket_no = fields.Char(string="Ticket No",readonly=True)
    ticket_title = fields.Char(string="Ticket Title")
    assi_to = fields.Many2one('res.users',string="Assigned to")
    # customer = fields.Many2one('res.users',string="Customer")
    customer = fields.Many2one('res.partner',string="Customer")
    email_id = fields.Char(related='assi_to.email',string="Email")
    phone = fields.Char(string="Phone")
    company = fields.Char(related='assi_to.company_name',string="Company")
    helpdesk_team = fields.Many2one('helpdesk.team',string="Helpdesk Team")
    team_leader = fields.Many2one(related='helpdesk_team.leader',relation='res.users',string="Team Leader")
    project = fields.Many2one('project.project',string="Project")
    analytic_account = fields.Many2one(related='project.analytic_account_id',relation='analytic.account', string="Analytic Account")
    category = fields.Char(string="Category")
    subject = fields.Char(string="Subject")
    description = fields.Text(string="Description")

    department = fields.Many2one('hr.department',string="Department")
    priority = fields.Selection([('0', 'Low'),
                                 ('1', 'Normal'),
                                 ('2', 'High')], string='Priority', default='1', required=True)
    create_date = fields.Datetime(string='Create Date',index=True)
    close_date = fields.Datetime(string="Close Date")
    ticket_close = fields.Boolean(string="Is Ticket Closed")
    total_hours = fields.Float(string="Total Hours Spent",compute='get_hours',store=True)
    state = fields.Selection([
        ('new', 'New'),
        ('assigned', 'Assigned'),
        ('work_in', 'Work in Progress'),
        ('need_info', 'Needs More Info'),
        ('needs_reply', 'Needs Reply'),
        ('reopend', 'Reopened'),
        ('solution', 'Solution Suggested'),
        ('closed', 'Closed'),
    ], string='Status', track_visibility='onchange', default='new')

    tf_created_by = fields.Char('Created By')

    def tf_get_exact_status_name(self, state):
        for type_new in self._fields['state'].selection:
            if state == type_new[0]:
                return type_new[1]

    tsk_id = fields.Many2one('project.task')
    sheet_ids = fields.One2many('helpdesk.timesheet','helpdesk_ids')
    tsk_inv_line_ids = fields.One2many('helpdesk.invoice.line','helpdesk_inv_ids', track_visibility='onchange')
    invoice_id = fields.Many2one('account.invoice')

    attachment_number = fields.Integer(compute='_get_attachment_no', string="Number of Attachments")
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'helpdesk.ticket')],
                                     string='Attachments')
    # feedback_ids = fields.One2many("feed.back",'cust_id')
    rating_val = fields.Integer(string="Ratings")
    rating_msg = fields.Char(string="Rating Message")

    def compute_website_datetime_string(self, website_date):
        if website_date:
            return datetime.strptime(website_date, '%Y-%m-%d %H:%M:%S')+timedelta(hours=5)+timedelta(minutes=30)
        return website_date

    def compute_website_datetime(self, website_date):
        if website_date:
            return website_date+timedelta(hours=5)+timedelta(minutes=30)
        return website_date
        # if self.env.ref('base.partner_admin').sudo().tz:
        #     return datetime.strptime(website_date.strftime(
        #         tools.DEFAULT_SERVER_DATETIME_FORMAT), '%Y-%m-%d %H:%M:%S')
        # else:
        #     return date.today()

    @api.multi
    def _get_attachment_no(self):
        read_group_res = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'helpdesk.ticket'), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attach_data = dict((res['res_id'], res['res_id_count']) for res in read_group_res)
        for record in self:
            record.attachment_number = attach_data.get(record.id, 0)

    @api.model
    def create(self, vals):
        if not vals.get('parent_ticket', False):
            vals['ticket_no'] = self.env['ir.sequence'].next_by_code('ticket.no') or '0'
        ticket = super(Helpedesk_Ticket, self).create(vals)
        # if vals.get('ticket_no', '0') == '0':
        child_email = vals.get('email_id')
        if vals.get('parent_ticket', False):
            child_email = ticket.customer.email

        #Group Email Picking
        email_cc = ""
        if ticket.customer:
            if ticket.customer.category_id:
                child_email = ticket.customer.category_id[0].name

                count = 1
                for categ_cc in ticket.customer.category_id:
                    if count == 2:
                        email_cc += categ_cc.name
                    elif count > 2:
                        email_cc += "," + categ_cc.name

                    count+=1


        mail_template_id = self.env.ref('gt_helpdesk_support_ticket.ticket_created_mail_customer', False)
        mail_template_id.with_context({'email_to': child_email, 'ticket_nm': vals.get('ticket_no'), 'email_cc': email_cc}).send_mail(
            ticket.id, force_send=True)
        return ticket

    # remove mail from state before close
    @api.multi
    def write(self,vals):
        for rec_wr in self:
            res = super(Helpedesk_Ticket, self).write(vals)

            # #change helpdesk invoice line done by srinath
            # if vals.get('sheet_ids'):
            #     product_id = vals.get('sheet_ids')[1][2].get('product_id') if vals.get('sheet_ids')[1][2] else False
            #     description = vals.get('sheet_ids')[1][2].get('timesheet_description') if vals.get('sheet_ids')[1][2] else ''
            #     resolution = vals.get('sheet_ids')[1][2].get('sh_resolution') if vals.get('sheet_ids')[1][2] else ''
            #     hours = vals.get('sheet_ids')[1][2].get('hours') if vals.get('sheet_ids')[1][2] else 0.0
            #     helpdesk_invoice_line = self.tsk_inv_line_ids.filtered(lambda obj: obj.timesheet_id.id == vals.get('sheet_ids')[1][1])
            #     if helpdesk_invoice_line:
            #         if product_id:
            #             helpdesk_invoice_line.product_id = product_id
            #         if description:
            #             helpdesk_invoice_line.description = description
            #         if hours:
            #             helpdesk_invoice_line.qty = hours
            #         if resolution:
            #             helpdesk_invoice_line.sltech_resolution = resolution
            #
            # # end

            # Group Email Picking
            cust_email_to = rec_wr.customer.email
            email_cc = ""
            if rec_wr.customer:
                if rec_wr.customer.category_id:
                    cust_email_to = rec_wr.customer.category_id[0].name

                    count = 1
                    for categ_cc in rec_wr.customer.category_id:
                        if count == 2:
                            email_cc += categ_cc.name
                        elif count > 2:
                            email_cc += "," + categ_cc.name

                        count += 1






            if vals.get('state') == 'assigned':
                vals.update({'state':'assigned'})
                # mail_template_id = self.env.ref('gt_helpdesk_support_ticket.ticket_assigned_devloper', False)
                # mail_template_id.with_context({'email_to': rec_wr.customer.email, 'ticket_nm': vals.get('ticket_title')}).send_mail(rec_wr.id,force_send=True)

                mail_template_id = self.env.ref('gt_helpdesk_support_ticket.ticket_devloper_inform', False)
                mail_template_id.with_context({'email_to': rec_wr.email_id, 'ticket_nm': vals.get('ticket_title'), }).send_mail(
                    rec_wr.id, force_send=True)

                # event_id = self.env['calendar.event'].create(dict(
                #     name=rec_wr.ticket_no,
                #     start=rec_wr.create_date,
                #     stop=rec_wr.assigned_date,
                #     ticket_id=rec_wr.id,
                # ))
                # self.create_an_event(event_id)

            # elif vals.get('state') == 'work_in':
            #     vals.update({'state': 'work_in'})
            #     mail_template_id = self.env.ref('gt_helpdesk_support_ticket.ticket_work_in', False)
            #     mail_template_id.with_context({'email_to': rec_wr.email_id, 'ticket_nm': vals.get('ticket_title')}).send_mail(
            #         rec_wr.id, force_send=True)
            #
            # elif vals.get('state') == 'need_info':
            #     vals.update({'state': 'need_info'})
            #     mail_template_id = self.env.ref('gt_helpdesk_support_ticket.ticket_need_info', False)
            #     mail_template_id.with_context({'email_to': rec_wr.email_id, 'ticket_nm': vals.get('ticket_title')}).send_mail(
            #         rec_wr.id, force_send=True)
            #
            # elif vals.get('state') == 'needs_reply':
            #     vals.update({'state': 'needs_reply'})
            #     mail_template_id = self.env.ref('gt_helpdesk_support_ticket.ticket_needs_reply', False)
            #     mail_template_id.with_context({'email_to': rec_wr.email_id, 'ticket_nm': vals.get('ticket_title')}).send_mail(
            #         rec_wr.id, force_send=True)
            #
            # elif vals.get('state') == 'reopend':
            #     vals.update({'state': 'reopend'})
            #     mail_template_id = self.env.ref('gt_helpdesk_support_ticket.ticket_reopend', False)
            #     mail_template_id.with_context({'email_to': rec_wr.email_id, 'ticket_nm': vals.get('ticket_title')}).send_mail(
            #         rec_wr.id, force_send=True)
            #
            #
            # elif vals.get('state') == 'solution':
            #     vals.update({'state': 'solution'})
            #     mail_template_id = self.env.ref('gt_helpdesk_support_ticket.ticket_solution', False)
            #     mail_template_id.with_context({'email_to': rec_wr.email_id, 'ticket_nm': vals.get('ticket_title')}).send_mail(
            #         rec_wr.id, force_send=True)

            elif vals.get('state') == 'closed':
                vals.update({'state': 'closed'})
                #### this code is commented by sltech

                # mail_template_id = self.env.ref('gt_helpdesk_support_ticket.ticket_closed', False)
                #
                # mail_template_id.with_context({'email_to': cust_email_to, 'ticket_nm': vals.get('ticket_title'),
                #                                'email_cc': email_cc}).send_mail(
                #     rec_wr.id, force_send=True)

                ### ============ end ================


                # mail_template_id.with_context({'email_to': rec_wr.email_id, 'ticket_nm': vals.get('ticket_title')}).send_mail(
                #     rec_wr.id, force_send=True)

                rec_wr.close_date = datetime.today()
            elif vals.get('state') == 'work_in':
                vals.update({'state': 'work_in'})
                mail_template_id = self.env.ref('gt_helpdesk_support_ticket.ticket_work_in', False)
                mail_template_id.with_context({'email_to': cust_email_to, 'ticket_nm': vals.get('ticket_title'),
                                               'email_cc': email_cc}).send_mail(
                    rec_wr.id, force_send=True)
            return res

# --------------------------29 May 2019 changes -------------------------
    @api.onchange('state')
    def onchange_of_state(self):
        if self.state =='closed':
            self.update({'ticket_close': True})
# ------------------------------------------------------
    @api.one
    @api.depends('sheet_ids.hours','sheet_ids')
    def get_hours(self):
        count_hours=0
        for line in self.sheet_ids:
            count_hours += line.hours
        self.total_hours = count_hours


    @api.one
    def task_create(self):

        task_obj = self.env['project.task']
        tsk_fields = task_obj.fields_get()
        default_value = task_obj.default_get(tsk_fields)

        task_line = self.env['account.analytic.line']
        line_f = task_line.fields_get()
        default_line = task_line.default_get(line_f)


        ticket_title=self.ticket_title
        ticket_no = self.ticket_no
        title_no = ticket_title +'('+ticket_no+')'

        task_obj_id= task_obj.create({
            'name': title_no,
            'project_id': self.project.id,
            'user_id': self.assi_to.id,
            'description_pad': self.description,
        })
        self.write({'tsk_id': task_obj_id.id})

        # print "::::::idddd:::::",task_obj_id
        for task_lst in self.sheet_ids:
            default_line.update({
                'account_id': self.analytic_account.id,
                'task_id': task_obj_id.id,
                'date': task_lst.timesheet_date,
                'user_id': task_lst.users.id,
                'name': task_lst.timesheet_description,
                'unit_amount': task_lst.hours,
            })
            task_line.create(default_line)

            # print ":::::::::::::::sheet_ids:::::",task_obj_id.id
            # print ":::::::::::::::task_lst.timesheet_date:::::",task_lst.timesheet_date
            # print ":::::::::::::::task_lst.users.id:::::",task_lst.users.id
            # print ":::::::::::::::task_lst.timesheet_description:::::",task_lst.timesheet_description
            # print ":::::::::::::::task_lst.hours:::::",task_lst.hours
            # print ":::::::::::::::task_id:::::",task_obj_id.id
            # print ":::::::::::::::default_line:::::",default_line

        return True





    @api.multi
    def view_created_task(self):

        pro_tsk_id = self.tsk_id
        # print ":::::::::::::::::::::::::::::::::::::::::::invoice id",pro_tsk_id
        view_ref = self.env['ir.model.data'].get_object_reference('project', 'view_task_form2')
        view_id = view_ref[1] if view_ref else False
        res = {
            'type': 'ir.actions.act_window',
            'name': _('Project Task'),
            'res_model': 'project.task',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_id': pro_tsk_id.id,
            'target': 'current'
        }

        return res

    @api.one
    def helpdesk_invoice(self):
        dt_date = str(self.create_date)
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


        for invoice_lst in self.tsk_inv_line_ids:
            tax_ids = [tax.id for tax in invoice_lst.inv_tax]
            # print "::::::::::::::::::::::::::::::::::::taxess:::::::",tax_ids
            default_line.update({
                'invoice_id': inv_id.id,
                'product_id': invoice_lst.product_id.id,
                'name': invoice_lst.description,
                'account_analytic_id': invoice_lst.ac_analytic_id.id,
                'quantity': invoice_lst.qty,
                'price_unit': invoice_lst.unit_price,
                # 'account_analytic_id': invoice_lst.ac_analytic_id.id,
                'invoice_line_tax_ids': [(6, 0, tax_ids)],
            })
            inv_line = invoice_line.new(default_line)
            inv_line._onchange_product_id()
            default_line.update({'invoice_id': inv_id.id,
                                 'account_id': inv_line.with_context(
                                 {'journal_id': inv_id.journal_id.id})._default_account()})

            invoice_line.create(default_line)
            # inv_id.action_invoice_open()
            #
            # template_obj = self.env.ref('account.email_template_edi_invoice', False)
            # template_obj.send_mail(inv_id.id)
        self.invoice_id = inv_id.id
        return True


    @api.multi
    def view_helpdesk_invoice(self):
        invoice_id = self.invoice_id
        view_ref = self.env['ir.model.data'].get_object_reference('account', 'invoice_form')
        view_id = view_ref[1] if view_ref else False
        res = {
            'type': 'ir.actions.act_window',
            'name': _('Customer Invoice'),
            'res_model': 'account.invoice',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_id': invoice_id.id,
            'target': 'current'
        }

        return res

    @api.model
    def message_get_reply_to(self, ids, default=None):
        """ Override to get the reply_to of the parent project. """
        tickets = self.sudo().browse(ids)
        return dict((ticket.id, ticket.email_id) for ticket in
                    tickets)

    @api.multi
    def message_get_suggested_recipients(self):
        recipients = super(Helpedesk_Ticket, self).message_get_suggested_recipients()
        for ticket in self:
            if ticket.customer:
                email_cc = ""
                email = ticket.customer.email
                if ticket.customer.category_id:
                    email = ticket.customer.category_id[0].name

                    count = 1
                    for categ_cc in ticket.customer.category_id:
                        if count == 2:
                            email_cc += categ_cc.name
                        elif count > 2:
                            email_cc += "," + categ_cc.name

                        count += 1







                # ticket._message_add_suggested_recipient(recipients, partner = ticket.customer,
                #                                         reason=_('Customer'))
                ticket._message_add_suggested_recipient(recipients, email=email,
                                                        reason=_('Customer'))
            elif ticket.email_id:
                ticket._message_add_suggested_recipient(recipients, email=ticket.email_id,
                                                           reason=_('Contact Email'))
        return recipients

    @api.multi
    def reopen_ticket(self):
        self.write({"state": "reopend"})





class Helpedesk_Team(models.Model):
    _name = 'helpdesk.team'


    name = fields.Char(string="Name")
    leader = fields.Many2one('res.users',string="Leader")
    is_default = fields.Boolean(string="Is Default Team?")
    help_members_line = fields.One2many('helpdesk.team.lines','help_team_ids')


class Helpedesk_Team_Members(models.Model):
    _name = 'helpdesk.team.lines'

    help_team_ids = fields.Many2one('helpdesk.team')
    name = fields.Char(string="Name")
    login_user = fields.Many2one('res.users',string="Login")
    language = fields.Many2one('res.lang',string="Language")
    last_conn = fields.Date(string="Last Connection")




class Helpedesk_Team_Timesheet(models.Model):
    _name = 'helpdesk.timesheet'

    helpdesk_ids = fields.Many2one('helpdesk.ticket',string='Helpdesk Id')
    timesheet_date = fields.Date(string='Date')
    users = fields.Many2one('res.users',string="User",default= lambda self: self.env.user.id, domain="[('share','=',False)]")
    project = fields.Many2one('project.project',string="Project")
    timesheet_description = fields.Char(string="Description")
    bil_lable = fields.Boolean(string="Billable",default=True)
    hours = fields.Float(string="Units", default=0.0)
    sltech_resolution = fields.Text(string='Resolution')

    @api.constrains('hours')
    def compute_hours(self):
        for rec in self:
            if rec.hours < 1.0:
                raise ValidationError('Please set hours!')

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        fields = super(Helpedesk_Team_Timesheet, self).fields_get(allfields=allfields, attributes=attributes)
        if not self.user_has_groups('gt_helpdesk_support_ticket.hd_support_manager_access') and \
                not self.user_has_groups('custom_module.hd_support_team_leader_access') and \
                self.user_has_groups('custom_module.hd_support_contractor_access') and \
                self.user_has_groups('gt_helpdesk_support_ticket.hd_support_user_access') and \
                not self.user_has_groups('base.group_system'):
            if 'users' in fields:
                fields['users']['readonly'] = True

        return fields





class Helpedesk_Team_Members_lines(models.Model):
    _name = 'helpdesk.invoice.line'

    helpdesk_inv_ids = fields.Many2one('helpdesk.ticket')
    product_id = fields.Many2one('product.product',string="product")


    @api.onchange('product_id')
    def domain_product_id(self):
        # if self.product_id:
        # record = self.env['product.product'].search(
        #     [('categ_id', '!=', self.env.ref('custom_module.spareparts_product_category').id)])
        return {
            'domain': {
                'product_id': [('categ_id', '=', self.env.ref('custom_module.spareparts_product_category').id)]
            }}

    description = fields.Char(string="Description")
    ac_analytic_id = fields.Many2one('account.analytic.account',string="Analytic Account")
    qty = fields.Float(string="Quantity", default=1.00)
    uom = fields.Many2one('uom.uom',string="Unit of Measure")
    unit_price = fields.Float(string="Unit Price")
    inv_tax = fields.Many2one('account.tax',string="Taxes")
    amt = fields.Float(string="Amount")
    tax_amt = fields.Float(compute='sltech_compute_tax', store=True, string="Tax Amount")
    sltech_net_amount = fields.Float(compute='sltech_compute_subtotal', store=True, string="Net Amount")

    @api.depends('amt', 'product_id', 'unit_price', 'qty')
    def sltech_compute_subtotal(self):
        for rec in self:
            amount = rec.unit_price * rec.qty
            rec.sltech_net_amount = amount


    @api.depends('amt', 'product_id', 'unit_price', 'qty')
    def sltech_compute_tax(self):
        for rec in self:
            amount = rec.unit_price * rec.qty
            rec.tax_amt = 0
            if rec.product_id.taxes_id:
                # rec.inv_tax = rec.product_id.taxes_id[0].id
                if rec.inv_tax:
                    rec.tax_amt = (amount * rec.inv_tax.amount) / 100

    @api.onchange('product_id')
    def my_product_price(self):
        # tot_amt = self.product_id.lst_price *self.qty
        self.description = self.product_id.name
        self.unit_price = self.product_id.lst_price
        self.qty = 1
        self.uom = self.product_id.uom_id.id
        amount = self.unit_price * self.qty
        if self.product_id.taxes_id:
            self.inv_tax = self.product_id.taxes_id[0].id
            amount += (amount * self.inv_tax.amount)/100
        self.amt = self.unit_price * self.qty

    @api.onchange('unit_price','qty')
    def compute_price(self):
        amount = self.unit_price * self.qty
        if self.inv_tax:
            amount += (amount * self.inv_tax.amount) / 100
        self.amt = amount




class Helpedesk_Task(models.Model):
    _inherit = 'project.task'

    # hepdesk_id = fields.Many2one("helpdesk")


#
#
# class Feed_Back(models.Model):
#     _name = 'feed.back'
#
#     cust_id = fields.Many2one("helpdesk.ticket")
#     cust_nm = fields.Char(string="Summary")
#     msg = fields.Integer(string="Ratings")

# class CalendarEvent(models.Model):
#     _inherit = "calendar.event"
#
#     ticket_id = fields.Many2one('helpdesk.ticket')