from odoo import http
from odoo.http import request

class PrivacyPolicyController(http.Controller):

    @http.route('/privacy/policy', type='http', auth='public', website=True)
    def privacy_policy(self, **kwargs):
        return request.render('insabhi_mobile_api.privacy_policy_template')
