# -*- coding: utf-8 -*-
from datetime import datetime, date

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SearchPopup(models.TransientModel):
    _name = 'search.popup.wizard'

    @api.model
    def get_company(self):
        return self.env['res.company'].sudo().search([('entrepot_centrale', '=', True)]).ids

    start_date = fields.Date(string='Date debut', default=lambda self: date.today())
    end_date = fields.Date(string='Date fin', default=lambda self: date.today())
    company_ids = fields.Many2many('res.company', string='Entreprises', default=get_company)
    is_customer = fields.Boolean(string='Clients')
    is_vendor = fields.Boolean(string='Fournisseurs')
    is_cash = fields.Boolean(string='Tresorerie')

    def action_update_information(self):
        company = tuple(self.company_ids.ids)
        active_id = self.env.context.get('active_id')
        active_dashboard = self.env['mini.account.dashboard'].browse(active_id)
        if self.is_cash:

            self.env['mini.cash.dashboard'].search([]).unlink()
            query = '''select account_move.journal_id as journal_id,account_move.company_id as company_id,account_journal.backend_name as name,
                    sum(account_bank_statement_line.amount) as amount from account_move inner join account_bank_statement_line on 
                    account_bank_statement_line.id = account_move.statement_line_id inner join account_journal on 
                    account_journal.id = account_move.journal_id where account_move.company_id in %(company)s GROUP BY 
                    account_move.journal_id,account_journal.backend_name,account_move.company_id ORDER BY amount DESC; '''
            self._cr.execute(query, {'company': company})
            cash_data = self._cr.dictfetchall()
            self._cr.flush()
            cash = [(0, 0, rec) for rec in cash_data]
            active_dashboard.update({'mini_cash_dashboard_ids': cash, 'start_date': self.start_date,
                                     'end_date': self.end_date, 'company_ids': self.company_ids.ids})
        elif self.is_vendor:
            first_month = self.start_date
            last_month = self.end_date
            account_move = self.env['account.move'].sudo().search([
                ('invoice_date', '>=', first_month),
                ('invoice_date', '<=', last_month),
                ('move_type', '=', 'in_invoice'),
                ('company_id', 'in', self.company_ids.ids),
                ('state', '=', 'posted'),
            ])

            account_payment = self.env['account.payment'].search([
                ('date', '>=', first_month),
                ('date', '<=', last_month),
                ('payment_type', '=', 'outbound'),
                ('partner_type', '=', 'supplier'),
                ('company_id', 'in', self.company_ids.ids),
                ('state', '=', 'posted'),
            ])
            debit = 0
            credit = 0
            journal_id = None
            if account_move:
                debit = sum(account_move.mapped('amount_total'))
                journal_id = account_move.journal_id.id
            if account_payment:
                credit = sum(account_payment.mapped('amount'))
            vendor_data = [(0, 0, {'start_date': first_month, 'end_date': last_month, 'amount': - debit + credit, 'journal_id': journal_id})]
            self.env['mini.vendor.dashboard'].search([('account_dashboard_vendor_id', '!=', active_id)]).unlink()
            active_dashboard.update({'mini_vendor_dashboard_ids': vendor_data, 'start_date': self.start_date,
                                     'end_date': self.end_date, 'company_ids': self.company_ids.ids})
        elif self.is_customer:
            first_month = self.start_date
            last_month = self.end_date
            account_move = self.env['account.move'].search([
                ('invoice_date', '>=', first_month),
                ('invoice_date', '<=', last_month),
                ('move_type', '=', 'out_invoice'),
                ('company_id', 'in', self.company_ids.ids),
                ('state', '=', 'posted'),
            ])

            account_payment = self.env['account.payment'].search([
                ('date', '>=', first_month),
                ('date', '<=', last_month),
                ('payment_type', '=', 'inbound'),
                ('partner_type', '=', 'customer'),
                ('company_id', 'in', self.company_ids.ids),
                ('state', '=', 'posted'),
            ])
            debit = 0
            credit = 0
            journal_id = None
            if account_move:
                debit = sum(account_move.mapped('amount_total'))
                journal_id = account_move.journal_id.id
            if account_payment:
                credit = sum(account_payment.mapped('amount'))
            customer_data = [(0, 0, {'start_date': first_month, 'end_date': last_month, 'amount': debit - credit, 'journal_id': journal_id})]
            self.env['mini.customer.dashboard'].search([('account_dashboard_customer_id', '!=', active_id)]).unlink()
            active_dashboard.update({'mini_customer_dashboard_ids': customer_data, 'start_date': self.start_date,
                                     'end_date': self.end_date, 'company_ids': self.company_ids.ids})
        else:
            raise ValidationError("Veuillez cochez un type de recherche")
