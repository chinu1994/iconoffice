# -*- coding: utf-8 -*-
##############################################################################
#
#    SLTECH ERP SOLUTION
#    Copyright (C) 2022-Today(www.slecherpsolution.com).
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
    'name': 'ICONOFFICE - Generate Invoice',
    'summary': 'Generate Invoice',
    'version': '12.0.0.1.0',
    'category': 'crm',
    'author': 'Srinath Pal',
    'website': 'https://www.sltecherpsolution.com',
    'depends': [
        'account',
        'custom_module'
    ],
    'data': [
        'view/product_template.xml',
    ],
    'installable': True,
    'auto_install': False,
}