# from gt_helpdesk_support_ticket.controllers.main import Helpdesk_Data
from openerp import http, SUPERUSER_ID
from openerp.http import request
import werkzeug
from dateutil import tz
from datetime import datetime, tzinfo
from odoo.http import Response

class MainController(http.Controller):

    @http.route('/page/helpdesk_tickets/', auth='public', website=True)
    def helpdesk_tickets(self, **kw):
        if not request.session.uid:
            return request.redirect('/web/login')
        login_user = request.env.user
        my_tickets = request.env['helpdesk.ticket'].search([('customer', '=', login_user.id)])
        total_tickets = len(my_tickets)
        result = http.request.render('gt_helpdesk_support_ticket.helpdesk_tickets',
                                     {'count_tickets': total_tickets, 'partners': login_user})
        return result

    @http.route('/page/helpdesk_tickets.html', auth='public', website=True)
    def helpdesk_tickets_pass(self, **kw):
        return http.request.render('custom_module.qwerty')

    @http.route('/iconmobileverify', auth='public', website=True)
    def helpdesk_iconmobileverify(self, **kw):
        # Define your HTML content
        html_content = """
                google-site-verification: googlef2b408ca7c1f7526.html
                """

        # Return the HTML file as a downloadable attachment
        return Response(
            html_content,
            content_type='text/html',
            headers=[
                ('Content-Disposition', 'attachment; filename="googlef2b408ca7c1f7526.html"')
            ]
        )
        return http.request.render('custom_module.iconmobileverify')



from odoo.addons.website_form.controllers.main import WebsiteForm
import json
from psycopg2 import IntegrityError
from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError

class WebsiteFormInherit(WebsiteForm):
    # Check and insert values from the form on the model <model>
    @http.route('/website_form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True)
    def website_form(self, model_name, **kwargs):
        model_record = request.env['ir.model'].sudo().search(
            [('model', '=', model_name), ('website_form_access', '=', True)])
        if not model_record:
            return json.dumps(False)

        try:
            data = self.extract_data(model_record, request.params)
        # If we encounter an issue while extracting data
        except ValidationError as e:
            # I couldn't find a cleaner way to pass data to an exception
            return json.dumps({'error_fields': e.args[0]})

        try:
            if model_name == 'helpdesk.ticket':
                # if kwargs.get('tpartner_name'):
                #     partner_id = request.env['res.partner'].sudo().search([('name', '=', kwargs.get('tpartner_name'))])
                #     if partner_id:
                #         partner_id = partner_id
                #     else:
                #         partner_id = request.env['res.partner'].sudo().create({'name':kwargs.get('tpartner_name'),
                #                                                            'property_account_payable_id':request.env.ref('l10n_au.1_au_11200').id,
                #                                                            'property_account_receivable_id':request.env.ref('l10n_au.1_au_21200').id})
                data['record'].update({
                    'assi_to': request.env.ref('base.user_admin').sudo().id,
                    # 'temail_from': kwargs.get('temail_from', ''),
                    'temail_from': kwargs.get('tf_user_email', ''),
                    'email_id': kwargs.get('email_id', ''),
                    'serial_no': kwargs.get('serial_no', ''),
                    'fault_area': kwargs.get('fault_area', ''),
                    'description': kwargs.get('description', ''),
                    'tref': kwargs.get('tref', ''),
                    'tpartner_name': kwargs.get('tpartner_name', ''),
                    'ticket_title': kwargs.get('tf_ticket_title', ''),
                    'tf_created_by': kwargs.get('tf_created_by', ''),
                    'ticket_state_created': 'web_ticket',
                    'customer': request.env.user.partner_id.id,
                    'model_no': kwargs.get('model_no'),
                    'sltech_state_id': int(kwargs.get('sltech_state_id')) if kwargs.get('sltech_state_id') else False,
                })
            id_record = self.insert_record(request, model_record, data['record'], data['custom'], data.get('meta'))
            if id_record:
                self.insert_attachment(model_record, id_record, data['attachments'])


                if model_name == 'helpdesk.ticket':
                    ticket_id = request.env[model_name].sudo().browse(id_record)
                    if ticket_id.ticket_state_created == 'web_ticket':
                        attachment_ids = request.env['ir.attachment'].sudo().search([('res_model', '=', 'helpdesk.ticket'),
                                                                           ('res_id', '=', ticket_id.id),
                                                                           ('res_name', '=', ticket_id.ticket_no)])
                        attachment_link = "\n"
                        if attachment_ids:
                            url_domain = request.env['ir.config_parameter'].sudo().search(
                                [('key', '=', 'web.base.url')]).value
                            attachment_link = "\n"

                            for atttach in attachment_ids:
                                attachment_link += url_domain + "/web/content/" + str(atttach.id) + "/" + atttach.name + "\n"

                        mail_template_id = request.env.ref('custom_module.ticket_website_ticket_email_template', False).sudo()
                        mail_template_id.with_context({'email_to': ticket_id.assi_to.login,
                                                       'email_from': ticket_id.customer.email,
                                                       'attachment_link': attachment_link,
                                                       'user_name': ticket_id.customer.name}).sudo().send_mail(
                            ticket_id.id, force_send=True)

        # Some fields have additional SQL constraints that we can't check generically
        # Ex: crm.lead.probability which is a float between 0 and 1
        # TODO: How to get the name of the erroneous field ?
        except IntegrityError:
            return json.dumps(False)

        request.session['form_builder_model_model'] = model_record.model
        request.session['form_builder_model'] = model_record.name
        request.session['form_builder_id'] = id_record

        return json.dumps({'id': id_record})
