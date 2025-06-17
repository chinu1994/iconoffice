# -*- coding: utf-8 -*-
##############################################################################
#
#    INSABHI
#    Copyright (C) 2025-Today(www.insabhi.com).
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
    'name': "ICONOFFICE - Website Inventory Customization",

    'summary': """Website Inventory Customization""",

    'description': """
         Website Inventory Customization
    """,

    'author': "Sachin Burnawal",
    'website': "http://www.insabhi.com",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'stock', 'gt_helpdesk_support_ticket'],

    # always loaded
    'data': [
        'views/assets.xml',
        'views/templates.xml',
    ],
    
}