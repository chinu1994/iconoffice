# -*- coding: utf-8 -*-
{
    'name': "ICONOFFICE - Customization",

    'summary': """Customization""",

    'description': """
         Customization
    """,

    'author': "Sachin Burnawal",
    'website': "http://www.yourcompany.com",
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
        'security/ir_rule.xml',
        'security/ir.model.access.csv',

        'data/time_set.xml',

        'views/templates.xml',
        'views/custom_views.xml',
        'views/res_partner_views.xml',
        'views/res_users.xml',
        'views/invoice_report_template.xml',
        'views/acccount_payment.xml',
        'static/src/views/assets.xml',
        'qweb_view/qweb_pdf.xml',
        'views/custom_popup.xml',
        'views/privacy_policy.xml'
    ],
    
}