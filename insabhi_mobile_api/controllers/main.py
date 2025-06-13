import base64
from odoo import http
from odoo.http import request
import json
import logging
from datetime import datetime


logger = logging.getLogger(__name__)

class AuthApiController(http.Controller):

    @http.route('/api/signup', auth='public', type='http', csrf=False, methods=['POST'])
    def signup(self, **kwargs):
        name = kwargs.get('name')
        email = kwargs.get('email')
        password = kwargs.get('password')

        if not all([name, email, password]):
            return {"error": "Missing fields"}

        existing_user = request.env['res.users'].sudo().search([('login', '=', email)])
        if existing_user:
            return {"error": "User already exists"}

        user = request.env['res.users'].sudo().create({
            'name': name,
            'login': email,
            'password': password,
        })

        return {"success": True, "user_id": user.id}

    @http.route('/api/app/login', type='http', auth="public", methods=['POST'], website=True, sitemap=True,
                csrf=False)
    def login(self, **kwargs):
        json_data  = {'success': False}
        email = kwargs.get('login')
        password = kwargs.get('password')

        if not email or not password:
            return {"error": "Missing email or password"}

        try:
            uid = request.session.authenticate(request.db, email, password)
            if uid:
                user_id = request.env.user.browse(uid)
                is_portal = user_id.has_group('base.group_portal')

                data = {
                    'name': user_id.name,
                    'login': user_id.login,
                    'password': user_id.password,
                    'email': user_id.email,
                    'phone': user_id.phone,
                    'partner_id': user_id.partner_id.id,
                    'is_portal': is_portal
                }
                json_data.update({'success': True, 'data': data})

            else:
                return {"error": "Invalid login credentials"}


        except Exception as e:

            print("====Login Failed====",e)
            return request.make_response(json.dumps({
                'status': 'error',
                'message': str(e)
            }), headers=[('Content-Type', 'application/json')])

        return json.dumps(json_data)

    @http.route('/api/app/profile', type='http', auth="public", methods=['GET'], csrf=False)
    def get_user_data(self, **kw):
        data_list = []

        partner_id = int(kw.get('partner_id'))
        sltech_users_ids = request.env['res.users'].sudo().search([('partner_id', '=', partner_id)])

        for users_data in sltech_users_ids:

            image_data = None
            if users_data.image:
                image_data = users_data.image.decode('utf-8')

            data = {
                'name': users_data.name,
                'email': users_data.email,
                'login': users_data.login,
                'phone': users_data.phone,
                'image': image_data,
            }
            data_list.append(data)
            print(data_list)

        data_json = json.dumps({'success': True, 'data': data_list, 'message': ''})
        return request.make_response(data_json, headers=[('Content-Type', 'application/json')])

    @http.route('/mobile/update/password', type='http', auth="public", methods=['POST'], website=True, sitemap=True,
                csrf=False)
    def update_password(self, **kwargs):

        new_password = kwargs.get('new_password')
        login = kwargs.get('login')

        if not new_password or not isinstance(new_password, str):
            return json.dumps({'error': 'Invalid or missing password'})
        if not login or not isinstance(login, str):
            return json.dumps({'error': 'Invalid or missing email'})

        print("Received data: new_password=%s, email=%s", new_password, login)

        user_id = http.request.env['res.users'].sudo().search([('login', '=', login)])
        if user_id:
            user_id.sudo().write({'password': new_password})
            return json.dumps({'success': True})
        else:
            return json.dumps({'error': 'User not found'})

    @http.route('/api/app/helpdesk/tickets', type='http', auth="public", methods=['GET'], csrf=False)
    def get_helpdesk_tickets(self, **kw):
        data_list = []

        partner_id = kw.get('partner_id')
        ticket_number = kw.get('ticket_number')
        page = int(kw.get('page', 1))
        limit = int(kw.get('limit', 20))
        offset = (page - 1) * limit

        user_id = request.env['res.users'].sudo().search([('partner_id', '=', int(partner_id))])

        domain = [('state', 'not in', ['closed'])]
        if user_id.has_group('gt_helpdesk_support_ticket.hd_support_user_access') and \
                not user_id.has_group('base.group_system') and \
                not user_id.has_group('base.group_erp_manager') and \
                not user_id.has_group('gt_helpdesk_support_ticket.hd_support_team_leader_access') and \
                not user_id.has_group('gt_helpdesk_support_ticket.hd_support_manager_access'):
            domain.append(('assi_to', '=', user_id.id))

        if user_id.has_group('gt_helpdesk_support_ticket.hd_customer_access') and \
                not user_id.has_group('base.group_system') and \
                not user_id.has_group('base.group_erp_manager') and \
                not user_id.has_group('gt_helpdesk_support_ticket.hd_support_team_leader_access') and \
                not user_id.has_group('gt_helpdesk_support_ticket.hd_support_user_access') and \
                not user_id.has_group('gt_helpdesk_support_ticket.hd_support_manager_access'):
            domain.append(('id', '=', 0))

        if user_id.has_group('base.group_portal'):
            domain.append(('customer', '=', user_id.partner_id.id))

        if ticket_number:
            domain.append(('ticket_no', '=', ticket_number))

        tickets = request.env['helpdesk.ticket'].sudo().search(domain, offset=offset, limit=limit)

        for ticket in tickets:
            data = {
                'id': ticket.id if ticket.id else '',
                'ticket_no': ticket.ticket_no if ticket.ticket_no else '',
                'priority': ticket.priority if ticket.priority else '',
                'ticket_title': ticket.ticket_title if ticket.ticket_title else '',
                'assi_to': ticket.assi_to.id if ticket.assi_to else '',
                'state': ticket.state if ticket.state else '',
                'customer': ticket.customer.display_name if ticket.customer else '',
                'team_leader': ticket.team_leader.name if ticket.team_leader else '',
                'temail_from': ticket.temail_from if ticket.temail_from else '',
                'tpartner_name': ticket.tpartner_name if ticket.tpartner_name else '',
                'tref': ticket.tref if ticket.tref else '',
                'serial_no': ticket.serial_no if ticket.serial_no else '',
                'fault_area': ticket.fault_area if ticket.fault_area else '',
                'description': ticket.description if ticket.description else '',
                'model_number': ticket.model_no if ticket.model_no else '',
                'resolution': ticket.resolution if ticket.resolution else '',
            }
            # Fetch Spare Parts Information
            spare_parts = []
            if ticket.sparepart_ids:
                for part in ticket.sparepart_ids:
                    spare_parts.append({
                        'product_name': part.product_id.name,
                        'qty_used': part.qty_used,
                        'state': part.state,
                    })
            data['spare_parts'] = spare_parts

            # Fetch Timesheet Information
            timesheets = []
            if ticket.sheet_ids:
                for timesheet in ticket.sheet_ids:
                    timesheets.append({
                        'timesheet_date': str(timesheet.timesheet_date),
                        'users': timesheet.users.id if timesheet.users else '',
                        'product_id': timesheet.product_id.name,
                        'timesheet_description': timesheet.timesheet_description,
                        'hours': timesheet.hours,
                    })
            data['timesheets'] = timesheets

            if ticket_number:
                pdf_docs = []
                attachments = request.env['ir.attachment'].sudo().search([
                    ('res_model', '=', 'helpdesk.ticket'),
                    ('res_id', '=', ticket.id),
                ])
                for att in attachments:
                    pdf_docs.append({
                        'name': att.name,
                        'url': f'/web/content/{att.id}?download=true',
                        'mimetype': att.mimetype,
                        'file_type': att.mimetype.split('/')[-1] if att.mimetype else '',
                        'attachment_id': att.id,
                    })
                data['pdf_documents'] = pdf_docs

            # Only append once, after all enrichment
            data_list.append(data)

        # Optional: Remove duplicates by ticket_no (or id)
        seen = set()
        unique_data_list = []
        for d in data_list:
            key = d.get('ticket_no') or d.get('id')
            if key not in seen:
                unique_data_list.append(d)
                seen.add(key)

        data_json = json.dumps({
            'success': True,
            'data': unique_data_list,
            'message': '',
            'total_ticket_count': len(unique_data_list)
        })

        return request.make_response(data_json, headers=[('Content-Type', 'application/json')])

    @http.route('/api/app/helpdesk/search_user', type='http', auth="public", methods=['GET'], csrf=False)
    def search_user(self, **kw):
        search_term = kw.get('query', '').strip()
        domain = [('name', 'ilike', search_term)] if search_term else []
        users = request.env['res.users'].sudo().search(domain, limit=10)

        result = [{
            'id': user.id,
            'name': user.name
        } for user in users]

        return request.make_response(json.dumps({
            'success': True,
            'results': result
        }), headers=[('Content-Type', 'application/json')])

    @http.route('/api/app/helpdesk/search_product', type='http', auth="public", methods=['GET'], csrf=False)
    def search_product(self, **kw):
        search_term = kw.get('query', '').strip()
        domain = [('name', 'ilike', search_term)] if search_term else []
        products = request.env['product.product'].sudo().search(domain, limit=10)

        result = [{
            'id': product.id,
            'name': product.name
        } for product in products]

        return request.make_response(json.dumps({
            'success': True,
            'results': result
        }), headers=[('Content-Type', 'application/json')])


    @http.route('/api/app/helpdesk/update_state', type='http', auth="public", methods=['POST'], csrf=False)
    def update_ticket_state(self, **kw):
        try:
            ticket_no = kw.get('ticket_no')
            new_state = kw.get('new_state')

            if not ticket_no or not new_state:
                return request.make_response(json.dumps({
                    'success': False,
                    'message': 'ticket_id and new_state are required.'
                }), headers=[('Content-Type', 'application/json')])

            ticket = request.env['helpdesk.ticket'].sudo().search([('ticket_no', '=', ticket_no)], limit=1)

            if not ticket.exists():
                return request.make_response(json.dumps({
                    'success': False,
                    'message': 'Ticket not found.'
                }), headers=[('Content-Type', 'application/json')])

            if not ticket.sheet_ids.exists():
                return request.make_response(json.dumps({
                    'success': False,
                    'message': 'Ticket timesheet not found.'
                }), headers=[('Content-Type', 'application/json')])


            allowed_states = ['assigned', 'work_in', 'closed']
            if new_state not in allowed_states:
                return request.make_response(json.dumps({
                    'success': False,
                    'message': f'Invalid state. Allowed: {allowed_states}'
                }), headers=[('Content-Type', 'application/json')])

            ticket.sudo().write({'state': new_state})

            return request.make_response(json.dumps({
                'success': True,
                'message': f'State updated to {new_state}.'
            }), headers=[('Content-Type', 'application/json')])

        except Exception as e:
            return request.make_response(json.dumps({
                'success': False,
                'message': f'Error: {str(e)}'
            }), headers=[('Content-Type', 'application/json')])


    @http.route('/api/app/helpdesk/timesheet', type='json', auth="public", methods=['POST'], csrf=False)
    def create_helpdesk_timesheet(self, **kw):
        try:
            body = request.jsonrequest

            ticket_id = body.get('ticket')
            product_name = body.get('product')
            timesheet_description = body.get('descrip')
            hours = body.get('hours')
            raw_date = body.get('date')  # ISO format expected
            user_name = body.get('user')
            enable = body.get('enable')
            product_id = body.get('id')
            resolution = body.get('resolution')

            try:
                hours = float(hours)
            except (TypeError, ValueError):
                hours = 0.0

            if isinstance(enable, str):
                enable = enable.lower() in ['true', '1', 'yes']

            # Parse date
            timesheet_date = None
            # if raw_date:
            #     try:
            timesheet_date = datetime.strptime(datetime.fromisoformat(raw_date).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d  %H:%M:%S').date()
                # except Exception:
                #     timesheet_date = None

            if not timesheet_date:
                timesheet_date = datetime.now().date()

            if not all([ticket_id, product_name, timesheet_description]):
                return {
                    'success': False,
                    'message': 'Missing required fields.'
                }

            # Search for records
            ticket = request.env['helpdesk.ticket'].sudo().search([('ticket_no', '=', ticket_id)], limit=1)
            product = request.env['product.product'].sudo().search([('name', '=', product_name)], limit=1)
            user = request.env['res.users'].sudo().search([('name', '=', user_name)], limit=1)

            if not ticket:
                return {'success': False, 'message': 'Ticket not found.'}
            if not product:
                return {'success': False, 'message': 'Product not found.'}
            if not user:
                return {'success': False, 'message': 'User not found.'}

            # Create timesheet entry
            ticket.write({
                'sheet_ids': [(0, 0, {
                    'product_id': product.id,
                    'bil_lable': enable,
                    'helpdesk_ids': ticket.id,
                    'hours': hours,
                    'timesheet_date': timesheet_date,
                    'users': user.id,
                    'timesheet_description': timesheet_description,
                    'sh_resolution': resolution
                })]
            })

            return {
                'success': True,
                'message': 'Timesheet entry created successfully.'
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }

    @http.route('/api/app/get-notifications', type='http', auth='public', methods=['GET'], csrf=False)
    def get_notifications(self, **kw):

        partner_id = kw.get('partner_id')
        page = int(kw.get('page', 1))
        limit = int(kw.get('limit', 20))
        offset = (page - 1) * limit

        domain = []
        if partner_id:
            domain.append(('partner_id', '=', int(partner_id)))

        notifications = request.env['notification.list'].sudo().search(domain,offset=offset,  order="create_date desc", limit=limit)
        data_list = []

        for notif in notifications:
            data = {
                "name": notif.name or '',
                "priority": notif.priority if hasattr(notif, 'priority') else '1',
                "ticket_no": notif.ticket_no if hasattr(notif, 'ticket_no') else '',
            }
            data_list.append(data)

        return request.make_response(
            json.dumps({
                'success': True,
                'data': data_list,
            }),
            headers=[('Content-Type', 'application/json')]
        )

    @http.route('/api/save/device/token', type='http', auth="public", methods=['POST'], csrf=False)
    def save_device_token(self, **kwargs):
        token = kwargs.get('token')
        partner_id = kwargs.get('partner_id')

        if not token:
            return request.make_response(json.dumps({
                'status': 'error',
                'statusCode': 404,
                'message': 'Device token is required'
            }), headers=[('Content-Type', 'application/json')])

        if not partner_id:
            return request.make_response(json.dumps({
                'status': 'error',
                'message': 'Partner ID is required'
            }), headers=[('Content-Type', 'application/json')])

        try:
            user = request.env['res.users'].sudo().search([('partner_id', '=', int(partner_id))], limit=1)
            if not user:
                return request.make_response(json.dumps({
                    'status': 'error',
                    'message': 'User not found'
                }), headers=[('Content-Type', 'application/json')])

            user.device_token = token

            logger.info(user.device_token)

            logger.info(f"Saved device token for user {user.id}")

            return request.make_response(json.dumps({
                'status': 'success',
                'message': 'Token saved successfully',
                'token': user.device_token
            }), headers=[('Content-Type', 'application/json')])

        except Exception as e:
            logger.exception("Error saving device token")
            return request.make_response(json.dumps({
                'status': 'error',
                'message': str(e)
            }), headers=[('Content-Type', 'application/json')])


    @http.route('/api/app/helpdesk/upload_signed_pdf', type='http', auth="public", methods=['POST'], csrf=False)
    def upload_signed_pdf(self, **kw):
        try:
            domain = []
            partner_id = kw.get('partner_id')
            ticket_no = kw.get('ticket_number')
            file = request.httprequest.files.get('file')

            #signed_pdf-sample_0.pdf
            if ticket_no:
                domain.append(('ticket_no', '=', ticket_no))

            ticket = request.env['helpdesk.ticket'].sudo().search(domain, limit=1)

            if not ticket_no or not file:
                return request.make_response(
                    json.dumps({'success': False, 'message': 'ticket_id and file are required.'}),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            file_content = file.read()
            file_name = file.filename

            existing_attachment = request.env['ir.attachment'].sudo().search([
                ('res_model', '=', 'helpdesk.ticket'),
                ('res_id', '=', ticket.id),
                ('name', '=', file_name),
                ('mimetype', '=', 'application/pdf')
            ])

            if existing_attachment:
                existing_attachment.unlink()

            attachment = request.env['ir.attachment'].sudo().create({
                'name': file_name,
                'datas': base64.b64encode(file_content),
                'res_model': 'helpdesk.ticket',
                'res_id': ticket.id,
                'mimetype': 'application/pdf',
            })

            return request.make_response(
                 json.dumps({
                     'success': True,
                     'message': 'PDF uploaded and attached successfully.',
                     'attachment_id': attachment.id
                 }),
                 headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            return request.make_response(
                json.dumps({
                    'success': False,
                    'message': f'Error: {str(e)}'
                }),
                headers=[('Content-Type', 'application/json')]
            )

    #Here is the API to POST ticket related messages (or send the messages from the mobile app)
    @http.route('/app/api/helpdesk/send_message', methods=['POST'], type='http', auth='public', csrf=False)
    def send_message_with_attachments_mobile_api(self, **post):
        try:
            ticket_id = int(post.get('ticket_id'))
            message_body = post.get('message')
            partner_id = int(post.get('partner_id', 0))

            if not ticket_id:
                return request.make_response(json.dumps({
                    'success': False,
                    'message': 'ticket_id and message are required'
                }), headers=[('Content-Type', 'application/json')])

            ticket = request.env['helpdesk.ticket'].sudo().browse(ticket_id)
            if not ticket.exists():
                return request.make_response(json.dumps({
                    'success': False,
                    'message': 'Ticket not found'
                }), headers=[('Content-Type', 'application/json')])

            # Handle uploaded files from request.httprequest.files
            attachment_ids = []
            for file_field in request.httprequest.files.getlist('documents'):
                file_data = file_field.read()
                attachment = request.env['ir.attachment'].sudo().create({
                    'name': file_field.filename,
                    'datas_fname': file_field.filename,
                    'datas': base64.b64encode(file_data).decode('utf-8'),
                    'res_model': 'helpdesk.ticket',
                    'res_id': ticket.id,
                    'public': True,
                })
                attachment_ids.append(attachment.id)

            # Post the message
            message = ticket.message_post(
                body=message_body,
                message_type='comment',
                subtype='mail.mt_comment',
                author_id=partner_id if partner_id else None,
                attachment_ids=attachment_ids  # Just a list of attachment record IDs

            )

            # Build response
            return request.make_response(json.dumps({
                'success': True,
                'message': 'Message sent',
                'data': {
                    'id': message.id,
                    'body': message.body,
                    'date': str(message.date),
                    'attachments': [
                        {
                            'id': att.id,
                            'name': att.name,
                            'url': f'/web/content/{att.id}?download=true'
                        } for att in message.attachment_ids
                    ]
                }
            }), headers=[('Content-Type', 'application/json')])

        except Exception as e:
            return request.make_response(json.dumps({
                'success': False,
                'message': str(e)
            }), headers=[('Content-Type', 'application/json')])


    @http.route('/app/api/helpdesk/receive_message', type='http', auth='public', methods=['GET'], csrf=False)
    def get_ticket_messages_mobile_api(self, **kwargs):
        try:
            domain = []
            ticket_id = int(kwargs.get('ticket_id'))

            if ticket_id:
                domain.append(('id', '=', ticket_id))

            ticket = request.env['helpdesk.ticket'].sudo().browse(domain)
            if not ticket.exists():  
                return request.make_response(json.dumps({
                    'success': False,
                    'message': 'Ticket not found'
                }), headers=[('Content-Type', 'application/json')])

            messages = request.env['mail.message'].sudo().search([
                ('model', '=', 'helpdesk.ticket'),
                ('res_id', '=', ticket_id),
            ], order='create_date desc', limit=10)

            message_data = []
            for msg in messages:
                attachments = [{
                    'id': att.id,
                    'name': att.name,
                    'url': f'/web/content/{att.id}?download=true'
                } for att in msg.attachment_ids]

                message_data.append({
                    'id': msg.id,
                    'author': msg.author_id.name if msg.author_id else msg.email_from,
                    'body': msg.body,  #This is the emoji supported api """HeHeHeHe..."""
                    'date': str(msg.date),
                    'attachments': attachments,
                })

            return request.make_response(json.dumps({
                'success': True,
                'data': message_data,
                'message': ''
            }), headers=[('Content-Type', 'application/json')])

        except Exception as e:
            return request.make_response(json.dumps({
                'success': False,
                'message': str(e)
            }), headers=[('Content-Type', 'application/json')])

    @http.route('/api/app/helpdesk/ticket/create', type='http', auth='public', methods=['POST'], csrf=False)
    def create_helpdesk_ticket(self, **kwargs):
        try:
            # Parse form fields
            data = request.params
            logger.info("Received form data: %s", data)

            # Create ticket
            ticket_vals = {
                'ticket_title': data.get('ticket_title'),
                'customer': int(data.get('partner_id')) if data.get('partner_id') else False,
                'temail_from': data.get('user_email'),
                'tpartner_name': data.get('customer_name'),
                'tref': data.get('customer_reference'),
                'serial_no': data.get('serial_no'),
                'fault_area': data.get('fault_area'),
                'description': data.get('description'),
                'model_no': data.get('model_no'),
                # 'state': data.get('state'),
            }
            ticket = request.env['helpdesk.ticket'].sudo().create(ticket_vals)

            # Handle uploaded documents
            files = request.httprequest.files.getlist('documents')
            attachment_ids = []
            for file_storage in files:
                file_content = file_storage.read()
                attachment = request.env['ir.attachment'].sudo().create({
                    'name': file_storage.filename,
                    'datas': base64.b64encode(file_content),
                    'res_model': 'helpdesk.ticket',
                    'res_id': ticket.id,
                    'mimetype': file_storage.mimetype,
                })
                attachment_ids.append(attachment.id)

            return request.make_response(
                data='{"success": true, "message": "Ticket created successfully", "ticket_id": %d, "ticket_no": "%s", "attachments": %s}' % (
                    ticket.id, getattr(ticket, 'ticket_no', ''), attachment_ids
                ),
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            logger.exception("Error in create_helpdesk_ticket")
            return request.make_response(
                data='{"success": false, "message": "%s"}' % str(e),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    @http.route('/app/api/helpdesk/delete_attachment', methods=['POST'], type='http', auth='public', csrf=False)
    def delete_attachment(self, **kwargs):
        try:
            attachment_id = kwargs.get('pdfDoc')
            if not attachment_id:
                return request.make_response(json.dumps({
                    'success': False,
                    'message': 'No attachment ID provided.'
                }), headers=[('Content-Type', 'application/json')])

            attachment = request.env['ir.attachment'].sudo().browse(int(attachment_id))
            if not attachment:
                return request.make_response(json.dumps({
                    'success': False,
                    'message': 'Attachment not found.'
                }), headers=[('Content-Type', 'application/json')])

            attachment.unlink()

            return request.make_response(json.dumps({
                'success': True,
                 'message': 'Attachment deleted successfully.'
            }), headers=[('Content-Type', 'application/json')])

        except Exception as e:
            return request.make_response(json.dumps({
                'success': False,
                'message': str(e)
            }), headers=[('Content-Type', 'application/json')])
