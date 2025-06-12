# -*- coding: utf-8 -*-
{
    'name': 'ICONOFFICE - Advanced Search Functionality && Header Fixed Tools',
    'version': '12.0',
    'category': 'Search Functionality with Header Fixed Tools',
    'summary': 'Added searchbar for every field in list view. Fixed table header and horizontal scrollable for multiple columns in tree view. Updated by Manisha on 02/08/2019',
    'description': """This module provide functionality of search on individual column and fixed column """,
    'website': "http://theerpstore.com/",
    'author': "Sachin Burnawal",
    'depends': ['web','rowno_in_tree'],
    'data': [
        'views/template_path.xml',
        'static/src/xml/res_users_form_view.xml',
    ],
    'qweb': [
        # 'static/src/xml/base_inherit.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
