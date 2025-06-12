from odoo import models, api, fields, tools
import odoo.addons.decimal_precision as dp
from odoo.tools.translate import _

class ProductAttribute(models.Model):
    _inherit = 'product.attribute'
    
    type = fields.Selection(selection_add=[('hidden','Hidden')])
    