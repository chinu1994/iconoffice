# -*- coding: utf-8 -*-
from odoo import http, SUPERUSER_ID
from odoo.http import request
import json
from dateutil import tz
from datetime import datetime, tzinfo


class MainController(http.Controller):

    @http.route('/icon/api/ticket/create', type='http', auth='public', methods=['POST'], csrf=False)
    def insabhi_icon_api_ticket_create(self, **kwargs):
        access_token = kwargs.get('access_key')
        user_email = kwargs.get('user_email')
        try:
            request.session.authenticate(request.db, user_email, access_token)
            user = request.env.user
            env = request.env(user=user.id)
            try:
                ticket_id = env['helpdesk.ticket'].sudo().create(
                    {
                        'temail_from': user_email,
                        'tpartner_name': kwargs.get("customer_name", ""),
                        'tref': kwargs.get("reference", ""),
                        'serial_no': kwargs.get("serial_number", ""),
                        'fault_area': kwargs.get("fault_section", ""),
                        'description': kwargs.get("description", ""),
                        # 'create_uid': user.id
                    })
            except:
                return http.Response(
                    json.dumps({
                        "status": "error",
                        "message": "key error, please check all the keys and its values from the documentation provided!"
                    }),
                    status=200,
                    content_type='application/json'
                )
            return http.Response(
                json.dumps({
                    "status": "success",
                    "icon_ticket_id": ticket_id.id
                }),
                status=200,
                content_type='application/json'
            )
        except:
            return http.Response(
                json.dumps({
                    "status": "error",
                    "message": "Invalid login credentials"
                }),
                status=200,
                content_type='application/json'
            )


