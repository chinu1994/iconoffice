from odoo import api,models,fields,_

class Invoiceinherit(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def default_get(self, fields):
        rec = super(Invoiceinherit, self).default_get(fields)
        rec.update(dict(
            payment_term_id=self.env.ref('account.account_payment_term_15days').id,
        ))
        return rec

    def get_data(self):
        result = []
        final_ticket_ids = list(set([res.helpdesk_inv_ids for res in self.ticket_inv_line_ids]))
        for ticket_rec in final_ticket_ids:
            data = {'val':[]}
            for line in ticket_rec:
                for rec in line.sparepart_ids:
                    data['val'].append({
                        'product_name':rec.product_id.name,
                        'qty':rec.qty_used,
                        'price':rec.product_id.list_price,
                        'tax':((sum([tax_rec.amount for tax_rec in rec.product_id.taxes_id])) * rec.product_id.list_price * rec.qty_used)/100,
                        'amt': rec.qty_used * rec.product_id.list_price,
                        'total': (rec.qty_used * rec.product_id.list_price) + ((sum([tax_rec.amount for tax_rec in rec.product_id.taxes_id])) *rec.qty_used* rec.product_id.list_price)/100
                    })
                for rec1 in line.tsk_inv_line_ids:
                    if rec1.id in self.ticket_inv_line_ids.ids:
                        data['val'].append({
                            'product_name':rec1.product_id.name,
                            'qty':rec1.qty,
                            'price':rec1.product_id.list_price,
                            'tax':((sum([tax_rec.amount for tax_rec in rec1.product_id.taxes_id])) * rec1.product_id.list_price * rec1.qty)/100,
                            'amt': rec1.qty * rec1.product_id.list_price,
                            'total': (rec1.qty * rec1.product_id.list_price) + ((sum([tax_rec.amount for tax_rec in rec1.product_id.taxes_id])) * rec1.product_id.list_price*rec1.qty)/100
                        })
                data.update({'s_no': line.serial_no, 'job': line.tref, 'c_name': line.tpartner_name, 'tpartner_name': line.tpartner_name})
            result.append(data)
        return result


