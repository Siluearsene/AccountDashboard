# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    amount_total = fields.Float(string='Montant total', readonly=True)
    name = fields.Char(string='name', readonly=True)

    def _select(self):
        return super()._select() + ", move.name as name , move.amount_total as amount_total"
