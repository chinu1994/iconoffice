import xmlrpc.client

import math

import ssl
ssl._create_default_https_context = ssl._create_unverified_context
# code

url14 = 'http://localhost:8069'
db14 = 'icon_office'
username14 = 'admin@iconofficesolutions.com.au'
password14 = 'admin'


common14 = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url14))
common14.version()
uid14 = common14.authenticate(db14, username14, password14, {})
models14 = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url14))


helpdesk_ticket_ids = models14.execute_kw(db14, uid14, password14,
                                                 'helpdesk.ticket', 'search_read',
                                                 [[['close_date','>','01/01/2024'],['close_date','<','01/02/2024'],['state', '=', 'closed']]],
                                                 {'fields': ['id', 'ticket_no', 'tsk_inv_line_ids']})

for helpdesk in helpdesk_ticket_ids:
    invoice_line = models14.execute_kw(db14, uid14, password14,
                                                 'helpdesk.invoice.line', 'search_read',
                                                 [[['id', '=', helpdesk['tsk_inv_line_ids']]]],
                                                 {'fields': ['id', 'product_id', 'unit_price']})
    for inv in invoice_line:
        product_id = models14.execute_kw(db14, uid14, password14,
                                                 'product.product', 'search_read',
                                                 [[['id', '=', inv['product_id'][0]]]],
                                                 {'fields': ['id', 'lst_price']})

        invoice_line_write = models14.execute_kw(db14, uid14, password14,
                                                     'helpdesk.invoice.line', 'write',
                                                     [[inv['id']], {'unit_price': product_id[0]['lst_price']}])
