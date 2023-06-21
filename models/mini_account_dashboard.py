# -*- coding: utf-8 -*-
from datetime import datetime, date

from odoo import models, fields, api, _


class MiniAccountDashboard(models.Model):
    _name = 'mini.account.dashboard'
    _rec_name = 'start_date'

    @api.model
    def get_company(self):
        return self.env['res.company'].sudo().search([('entrepot_centrale', '=', True)]).ids

    start_date = fields.Date(string='Date debut',
                             default=lambda self: datetime(fields.Datetime.now().year, 1, 1).strftime("%Y-%m-%d"))
    end_date = fields.Date(string='Date fin',
                           default=lambda self: datetime(fields.Datetime.now().year, 12, 1).strftime("%Y-%m-%d"))
    company_ids = fields.Many2many('res.company', string='Entreprises', default=get_company)
    mini_cash_dashboard_ids = fields.One2many('mini.cash.dashboard', 'account_dashboard_id', 'Cash dashboard')
    mini_customer_dashboard_ids = fields.One2many('mini.customer.dashboard', 'account_dashboard_customer_id',
                                                  'Customer dashboard')
    mini_vendor_dashboard_ids = fields.One2many('mini.vendor.dashboard', 'account_dashboard_vendor_id',
                                                'Vendor dashboard')
    state = fields.Selection([('draft', 'En cours'), ('done', 'Terminer')], default='draft')

    @api.model
    def default_get(self, fields_list):
        company = tuple(self.env.context['allowed_company_ids'])
        state = False
        res = super(MiniAccountDashboard, self).default_get(fields_list)
        search_data = {'is_search': False}
        data = self.get_information(state, search_data)
        cash = [(0, 0, rec) for rec in data.get('cash_data')]
        customer = [(0, 0, record) for record in data.get('customer_data')]
        vendor = [(0, 0, record) for record in data.get('vendor_data')]
        res.update({'mini_cash_dashboard_ids': cash})
        res.update({'mini_customer_dashboard_ids': customer})
        res.update({'mini_vendor_dashboard_ids': vendor})
        return res

    @api.model
    def get_information(self, state, search_data):
        companies = self.env['res.company'].sudo().search([])
        company = None
        data = dict()
        print('search data ...............', search_data)
        if search_data['is_search']:
            data = {
                'start_date': search_data['start_date'],
                'end_date': search_data['end_date']
            }
        else:
            data = {
                'start_date': datetime(fields.Datetime.now().year, 1, 1).strftime("%Y-%m-%d"),
                'end_date': datetime(fields.Datetime.now().year, 12, 1).strftime("%Y-%m-%d")
            }
        if state:
            company = tuple(companies.ids)
        else:
            company = tuple(companies.filtered(lambda c: c.entrepot_centrale).ids)
        # info tresorerie
        query = '''select account_move.journal_id as journal_id,account_journal.backend_name as name, 
        sum(account_bank_statement_line.amount) as amount from account_move inner join account_bank_statement_line on 
        account_bank_statement_line.id = account_move.statement_line_id inner join account_journal on 
        account_journal.id = account_move.journal_id where account_move.company_id in %(company)s and 
        account_move.date >= %(start_date)s and account_move.date <= %(end_date)s GROUP BY account_move.journal_id,
        account_journal.backend_name ORDER BY amount DESC; '''
        self._cr.execute(query, {'company': company, 'start_date': data['start_date'], 'end_date': data['end_date']})
        cash_data = self._cr.dictfetchall()
        self._cr.flush()
        # client data
        customer_data = self.get_customer_data(data)
        vendor_data = self.get_vendor_data(data)
        # stock_value = self.get_stock_amount_qty()
        return dict(cash_data=cash_data, customer_data=customer_data, vendor_data=vendor_data)

    def get_customer_data(self, data):
        now_date = datetime.now()
        account_move = self.env['account.move'].search([
            ('invoice_date', '>=', data['start_date']),
            ('invoice_date', '<=', data['end_date']),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
        ])

        account_payment = self.env['account.payment'].search([
            ('date', '>=', data['start_date']),
            ('date', '<=', data['end_date']),
            ('payment_type', '=', 'inbound'),
            ('partner_type', '=', 'customer'),
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
        customer_data = [
            {'start_date': data['start_date'], 'end_date': data['end_date'], 'amount': debit - credit, 'journal_id': journal_id}]
        return customer_data

    def get_vendor_data(self, data):
        now_date = datetime.now()
        account_move = self.env['account.move'].search([
            ('invoice_date', '>=', data['start_date']),
            ('invoice_date', '<=', data['end_date']),
            ('move_type', '=', 'in_invoice'),
            ('state', '=', 'posted'),
        ])

        account_payment = self.env['account.payment'].search([
            ('date', '>=', data['start_date']),
            ('date', '<=', data['end_date']),
            ('payment_type', '=', 'outbound'),
            ('partner_type', '=', 'supplier'),
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
        vendor_data = [
            {'start_date': data['start_date'], 'end_date': data['end_date'], 'amount': - debit + credit, 'journal_id': journal_id}]
        return vendor_data

    # avoir la montant du stock avec le prix de revient
    def get_stock_amount_qty(self):
        product_templates = self.env['product.template'].search([])
        amount_total = sum(tmpl.standard_price * tmpl.qty_available for tmpl in product_templates)
        stock = [{'name': 'Valeur du stock', 'amount': amount_total}]
        return stock

    @api.model
    def _action_open_dashboard_view(self):

        self.env['mini.account.dashboard'].search([]).unlink()
        return {
            "type": "ir.actions.act_window",
            "res_model": "mini.account.dashboard",
            "views": [[self.env.ref('account_dashboard.mini_account_dashboard_form_view').id, "form"], [False, "tree"],
                      [False, "kanban"]],
            'view_mode': 'form',
            "domain": [],
            "name": _("Dashboard")
        }

    def action_search_data(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'search.popup.wizard',
            'views': [[self.env.ref('account_dashboard.search_popup_wizard_view').id, 'form']],
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'name': 'Rapport',
            # 'context': {'default_partner_id': self.partner_id.id}
        }

    def action_print_reports(self):
        data = {'active_id': self.env.context.get('active_id')}
        return self.env.ref('account_dashboard.report_account_dashboard').report_action(self, data=data)
