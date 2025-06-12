# -*- coding: utf-8 -*-
{
    'name': "ICONOFFICE - Customization",

    'summary': """Customization""",

    'description': """
         ICON API CUSTOMIZATION
    """,

    'author': "Sachin Burnawal",
    'website': "http://www.insabhi.com",
    #https://www.freelancer.in/u/sachinburnawal?w=f
    #https://www.linkedin.com/in/sachin-burnawal-a29590129/
    #https://www.linkedin.com/in/ayush-gupta-802007133/

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'gt_helpdesk_support_ticket', 'l10n_au', 'portal', 'stock', 'google_calendar', 'contacts','account','web'],

    # always loaded
    'data': [
    ],
    
}