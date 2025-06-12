from odoo import fields, models, api


class KsResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_ks_fitness_page = fields.Boolean(string='Fitness')
    module_ks_corporate_page = fields.Boolean(string='Corporate')
    module_ks_pet_shop_page = fields.Boolean(string='Pet Shop')
    module_ks_furniture_page = fields.Boolean(string='Furniture')
    module_ks_food_shop_page = fields.Boolean(string='Food Shop')
    module_ks_jewellery_page = fields.Boolean(string='Jewellery')
    module_ks_book_shop_page = fields.Boolean(string='Book Shop')
    module_ks_hotel_page = fields.Boolean(string='Hotel')
    module_ks_christmas_page = fields.Boolean(string='Christmas')
    module_ks_new_year_page = fields.Boolean(string='New Year')
    module_ks_home_decor_page = fields.Boolean(string='Home Decor')
