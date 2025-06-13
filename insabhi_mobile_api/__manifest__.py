{
    'name': 'Insabhi API Authentication',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Login and Signup API for Mobile App',
    'author': 'Aditya Kumar Harijan',
    'depends': ['base', 'gt_helpdesk_support_ticket'],
    'installable': True,
    'application': False,

    'data': [
            'security/ir.model.access.csv',
            'views/privacy_policy.xml',
            'views/notification_list.xml',
        ],
}
