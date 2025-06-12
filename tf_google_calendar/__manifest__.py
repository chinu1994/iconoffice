# -*- coding: utf-8 -*-
{
    'name': "ICONOFFICE - Custom Invoice",



    'author': "Sachin Burnawal",
    'website': "http://www.theerpstoe.com",
    # https://www.freelancer.in/u/sachinburnawal?w=f
    # https://www.linkedin.com/in/sachin-burnawal-a29590129/
    # https://www.linkedin.com/in/ayush-gupta-802007133/

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Google Calendar',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'calendar', 'custom_module'],

    # always loaded
    'data': [
        'static/src/views/assets.xml',
    ],
    'qweb': [
        # 'static/src/xml/web_calendar.xml',
    ]

}