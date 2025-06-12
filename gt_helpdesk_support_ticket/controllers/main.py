from openerp import http, SUPERUSER_ID
from openerp.http import request
import werkzeug
from dateutil import tz
from datetime import datetime, tzinfo
import json,base64
from odoo.tools.translate import _

# QueryURL Class Call
class QueryURL(object):
    def __init__(self, path='', **args):
        self.path = path
        self.args = args

    def __call__(self, path=None, **kw):
        if not path:
            path = self.path
        for k,v in self.args.items():
            kw.setdefault(k,v)
        l = []
        for k,v in kw.items():
            if v:
                if isinstance(v, list) or isinstance(v, set):
                    l.append(werkzeug.url_encode([(k,i) for i in v]))
                else:
                    l.append(werkzeug.url_encode([(k,v)]))
        if l:
            path += '?' + '&'.join(l)
        return path

class Helpdesk_Data(http.Controller):

    # SachinBurnawal
    def tag_id_list_tickets(self, login_user):
        email = login_user.partner_id.email

        tag_id = request.env['res.partner.category'].sudo().search([('name', '=', email)])

        my_tickets = request.env['helpdesk.ticket'].sudo().search([('customer', '=', login_user.partner_id.id)])
        if tag_id:
            customer_ids = request.env['res.partner'].sudo().search([]).filtered(
                lambda self: tag_id.id in self.category_id.ids)
            my_tickets = request.env['helpdesk.ticket'].sudo().search([('customer', 'in', customer_ids.ids)])
        else:
            if login_user.partner_id.category_id:
                customer_ids = request.env['res.partner'].sudo().search([]).filtered(
                    lambda self: login_user.partner_id.category_id.id in self.category_id.ids)
                my_tickets = request.env['helpdesk.ticket'].sudo().search([('customer', 'in', customer_ids.ids)])
        return  my_tickets
    # End


    @http.route('/page/helpdesk_detail/', auth='public', website=True)
    def helpdesk_detail(self, **kw):
        login_user=request.env.user
        login_partner_id = login_user.partner_id
        tf_ticket_title = ""
        if login_partner_id.category_id:
            tf_ticket_title = login_partner_id.category_id[0].tf_ticket_title
        result = http.request.render('gt_helpdesk_support_ticket.helpdesk_detail',{'partners': login_partner_id,
                                                                                   'tf_ticket_title': tf_ticket_title,
                                                                                   'tf_users': login_user})
        return result


    @http.route('/page/helpdesk_tickets/', auth='public', website=True)
    def helpdesk_tickets(self, **kw):
        login_user = request.env.user
        # my_tickets = request.env['helpdesk.ticket'].sudo().search([('customer', '=', login_user.partner_id.id)])
        my_tickets = self.tag_id_list_tickets(login_user=login_user)
        total_tickets = len(my_tickets)
        result = http.request.render('gt_helpdesk_support_ticket.helpdesk_tickets',{'count_tickets':total_tickets,'partners':login_user})
        return result


    @http.route('/page/support_tickets/', auth='public', website=True)
    def support_tickets(self, **kw):

        login_user = request.env.user

        my_tickets = self.tag_id_list_tickets(login_user=login_user)
        # my_tickets = request.env['helpdesk.ticket'].sudo().search([('customer', '=', login_user.partner_id.id)])
        total_tickets = len(my_tickets)
        result = http.request.render('gt_helpdesk_support_ticket.support_tickets',{'ticket_lines':my_tickets,'count_tickets':total_tickets,'partners':login_user})
        return result



    @http.route('/page/support_tickets/<int:tc_line>', auth='public', website=True)
    def support_tickets_box(self,tc_line, **kw):
        login_user = request.env.user
        my_tickets = request.env['helpdesk.ticket'].sudo().search([('id', '=', int(tc_line))])

        messages = request.env['mail.message'].sudo().search([('res_id', '=', int(tc_line)), ('model', '=', 'helpdesk.ticket')])

        data_message = []
        for msg in messages:
            data_message.append(dict(
                body=msg.body,
                attachments='' if not msg.attachment_ids else [attch.datas for attch in msg.attachment_ids],
                email_from=msg.email_from,
                create_date=str(msg.date),
            ))

        url_domain = request.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')]).value
        attachment_ids = request.env['ir.attachment'].sudo().search([('res_model', '=', 'helpdesk.ticket'),
                                                                     ('res_id', '=', my_tickets.id),
                                                                     ('res_name', '=', my_tickets.ticket_no)])
        attachment_link = []

        for res in attachment_ids:
            attachment_link.append(url_domain + "/web/content/" + str(res.id) + "/" + res.name)

        data_message.sort(key=lambda self: self['create_date'], reverse=True)
        result = http.request.render('gt_helpdesk_support_ticket.support_tickets_box',{'ticket_lines':my_tickets,
                                                                                       'data_message': data_message,
                                                                                       'attachment_links': attachment_link})
        return result






    @http.route('/page/support_tickets_list/', auth='public', website=True)
    def support_tickets_list(self, **kw):
        print ("::::::::::::::::::::::::::support_tickets_list 11111")
        login_user = request.env.user
        # my_tickets = request.env['helpdesk.ticket'].sudo().search([('customer', '=', login_user.partner_id.id)])
        my_tickets = self.tag_id_list_tickets(login_user=login_user)
        total_tickets = len(my_tickets)
        result = http.request.render('gt_helpdesk_support_ticket.support_tickets_list',
                                     {'ticket_lines': my_tickets, 'count_tickets': total_tickets,
                                      'partners': login_user})
        return result



    @http.route('/page/support_tickets_list/<int:tc_line>', auth='public', website=True)
    def issue_temp(self,tc_line, **kw):
        print (":::::::::::::::::::::::::::issue_tickets_list",tc_line)
        login_user = request.env.user
        my_tickets = request.env['helpdesk.ticket'].sudo().search([('id', '=', int(tc_line))])
        total_tickets = len(my_tickets)
        result = http.request.render('gt_helpdesk_support_ticket.issue_temp',
                                     {'ticket_lines': my_tickets, 'count_tickets': total_tickets,
                                      'partners': login_user})
        return result




    # @http.route(['/page/tickets_msg/'], methods=['POST'], type='http', auth="user", website=True)
    # def tickets_msg(self,**kwargs):
    #     rc_id = kwargs.get("rc_id")
    #     cust_id = kwargs.get("cust_id")
    #     dev_msg = kwargs.get("msg")
    #
    #     my_tickets = request.env['helpdesk.ticket'].search([('id', '=', rc_id)])
    #     chat_obj= request.env['customer.chat'].create({'cust_id':rc_id,'cust_num':cust_id,'msg':dev_msg})
    #     print "::::::::::::::::::::::::::::::Ticket Messages::::::::::::::::::::::::",chat_obj
    #
    #     result = http.request.render('gt_helpdesk_support_ticket_v11.tickets_msg')
    #     return result





    @http.route('/page/feedback_msg/<int:id>', auth='public', website=True)
    def feedback_msg(self, id,**kw):
        my_tickets = request.env['helpdesk.ticket'].sudo().search([('id', '=', int(id))]).id
        print ("::::::::::::::::::::::::::::::::::::::::::Called Feedback:::::::::::",my_tickets)
        result = http.request.render('gt_helpdesk_support_ticket.feedback_msg',{'id': my_tickets})
        return result

    @http.route('/page/feedback_thanks/',methods=['POST'], auth='public', website=True, type='json')
    def feedback_thanks(self, rate,rc_id,rate_msg, **kw):
        print ("::::::::::::::::::::::::::::::::::::::::::rating value:::::::::::", rate)
        print ("::::::::::::::::::::::::::::::::::::::::::rating Msg:::::::::::", rate_msg)
        print ("::::::::::::::::::::::::::::::::::::::::::recored ID:::::::::::", rc_id)


        my_tickets = request.env['helpdesk.ticket'].sudo().search([('id', '=', rc_id)])
        my_tickets.write({'rating_val': rate, 'rating_msg': rate_msg})
        print (":::::::::::::::::check Data:::::",my_tickets)
        return http.request.env['ir.ui.view'].render_template("gt_helpdesk_support_ticket.feedback_thanks")

    @http.route('/send/message', methods=['POST'], auth='public', website=True, type='json')
    def customer_send_message(self, **kw):

        # {body=dff, subtype='mail.mt_comment', partner_ids=[], message_type='comment',
        #  attachment_ids=[], canned_response_ids=[]}




        # {'default_model': 'helpdesk.ticket', 'lang': 'en_US', 'default_res_id': 8, 'uid': 2,
        #  'mail_post_autofollow': True, 'tz': 'Australia/Melbourne'}
        ticket_id = request.env['helpdesk.ticket'].sudo().search([('id', '=', int(kw.get('ticket_id')))])
        ticket_id = ticket_id.with_context(default_model='helpdesk.ticket', default_res_id=ticket_id.id, mail_post_autofollow=True)
        ticket_id.message_post(body=kw.get('sendMessage'), subtype='mail.mt_comment', partner_ids=ticket_id.assi_to.partner_id.ids, message_type='comment',
         attachment_ids=[], canned_response_ids=[])

        last_message = request.env['mail.message'].sudo().search([('res_id', '=', int(kw.get('ticket_id'))), ('model', '=', 'helpdesk.ticket')], order='id desc')[0]

        return json.dumps({'last_message': dict(message=last_message.body,
                                                date=str(last_message.date),
                                                email_from=last_message.email_from)})

    @http.route('/send/attachment', methods=['POST'], auth='public', website=True, type='http')
    def customer_send_message_attachment(self, **kw):
        ticket_id = request.env['helpdesk.ticket'].sudo().search([('id', '=', int(kw.get('res_id')))])
        attch_id = request.env['ir.attachment'].sudo().create(dict(
            res_id=ticket_id.id,
            datas=base64.encodestring(kw['datas'].read()),
            res_model='helpdesk.ticket',
            res_name=ticket_id.ticket_no,
            name=kw.get('datas').filename,
            datas_fname=kw.get('datas').filename,
            mimetype=kw.get('datas').mimetype,
            type='binary',
            file_size=len(kw.get('datas').filename),
            public=True
        ))
        values = {
            'body': _('<p>Attached files : </p>'),
            'model': 'helpdesk.ticket',
            'message_type': 'comment',
            'no_auto_thread': False,
            'res_id': ticket_id.id,
            'attachment_ids': [(6, 0, attch_id.ids)],
        }
        mail_id = request.env['mail.message'].sudo().create(values)
        return request.redirect('/page/support_tickets/'+str(ticket_id.id))
