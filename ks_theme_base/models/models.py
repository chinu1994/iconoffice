# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ks_product_manager(models.Model):
    _inherit = 'product.template'

    """
    This model is used to place a option to select brand for product 
        at the time of creation of product
    """

    ks_product_tags = fields.Many2many("ks_theme.tags", 'products_track_tags_rel',
                                       'product_template_id', 'ks_theme_tags_id',
                                       string='Featured Tags')


class ks_brand(models.Model):
    _inherit = ["product.brand", "website.seo.metadata", 'website.published.multi.mixin']
    _name = 'product.brand'

    """This model is create brand and their info"""

    ks_image = fields.Binary(string='Image')
    ks_brand_discount = fields.Integer(string='Discount Percentage')
    ks_brand_url = fields.Char(invisible=True)
    ks_is_checked_on_shop = fields.Boolean(default=False)
    website_id = fields.Many2one('website', 'Website')

    @api.multi
    def ks_get_brand_url(self, name):
        for rec in self:
            base_url = rec.env['ir.config_parameter'].sudo().get_param('web.base.url')
            if rec.name:
                return 'shop?filter=' + str(name)
            else:
                return ""


class ks_Tags(models.Model):
    _name = "ks_theme.tags"
    _description = 'Ks Model'

    name = fields.Char()
    ks_state = fields.Boolean(default=True)
    brand_name = fields.Many2many('product.template', relation='ks_products_track_tags_rel',
                                  string='Available Products Tags')


class ks_products_track_tags_rel(models.Model):
    _name = "ks_products_track_tags_rel"
    _description = 'Ks Model'

    name = fields.Char()
    ks_source = fields.Char()


class ks_trending_style(models.Model):
    _inherit = 'product.public.category'

    ks_product_category_slogan = fields.Char(string='Slogan')
    ks_categ_tag = fields.Boolean(string='Trendy')
    child_id = fields.One2many('product.public.category', 'parent_id', string='Child Category')
    category_url = fields.Char(help="So each category can have their urls")
    ks_categ_background = fields.Binary(string='Breadcrumb Image', widget='binary')
