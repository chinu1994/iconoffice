# -*- coding: utf-8 -*-
##############################################################################
#
#    Globalteckz Pvt Ltd
#    Copyright (C) 2013-Today(www.globalteckz.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
{
    'name' : 'ICONOFFICE - Helpdesk Support Ticket & Issue Management from Website',
    'version' : '1.0',
    'author' : 'Globalteckz',
    'category' : 'Website',
    'description' : """ 
Helpdesk
helpdesk
desk help
helpdesk support
Helpdesk support
help desk
help desk support
Ticket
Issue Management 
Website with timesheets to track the number of hours used and pending with accounting.
helpdesk with accounting
heldesk with tracking 
helpdesk with hours 
helpdesk with tracking hours
Website Helpdesk Support Ticket
helpdesk support
customer helpdesk
customer Helpdesk support
Helpdesk support request
Helpdesk support ticket
ticket
Helpdesk customer query
Helpdesk customer help
Customer maintenance request
Customer service request
Website Helpdesk ticket
website request customer
Website Helpdesk Support Ticket
helpdesk support system
website_support
crm_helpdesk
Helpdesk Management
unique ticket number to customer automatically
being able to reply to incoming emails to communicate with customer
seeing all a customer's incoming help desk requests in context against customer object
unique ticket number per issue
print Helpdesk Ticket
Attachment on website Helpdesk Support
Message on website Helpdesk Support
Add attchment
Add message
Send Message Helpdesk Support
Attachment add Helpdesk Support
Multiple attachments Helpdesk Support
Add multiple attachments Helpdesk Support
Add attachments on website
App to manage your customer tickets and requests
Website Support Ticket- Support Detail
customer support
support request
support ticket
ticket
customer support Invoice
support request Invoice
support ticket Invoice
ticket Invoice
customer query 
customer help
customer maintenance request Invoice
customer service request Invoice
website support ticket Invoice
website request customer Invoice
ticket invoice 
customer invoice for support tickets
customer support Portal
support request Portal
support ticket Portal
ticket Portal
customer query 
customer help
customer maintenance request Portal
customer service request Portal
website support ticket Portal
website request customer Portal
ticket Portal 
customer Portal for support tickets
prepaid support hours
prepaid
prepaid support
prepaid customer
prepaid invoice
odoo 11 project issue
project issue 11 odoo
project issue odoo 11
project task
support
project support
support manager
issue manager
issue operator​
""",
    'summary': 'Website helpdesk support ticket & Issues system with billing based on the support provided',
    'website': 'https://www.globalteckz.com',
    'images': ['static/description/banner.png'],
    "license" : "Other proprietary",
    'website': 'https://www.globalteckz.com',
    "price": "40.00",
    "currency": "EUR",
    'depends' : ['website','portal','base', 'sale','account','hr_timesheet','website_sale','document','project'],
    'data': [
        'security/ir.model.access.csv',
        'security/helpdesk_security.xml',
        'view/helpdesk_website.xml',
        'view/sub_website.xml',
        'view/ticket_issue.xml',
        'view/feedback.xml',
        'report/helpdesk_template.xml',
        'report/report_view.xml',
        'helpdesk_support_view.xml',
        'email_notification.xml',

    ],
    'qweb' : [
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
