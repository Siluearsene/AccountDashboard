from odoo import models, api, fields
from datetime import datetime


class AccountDashboardReport(models.AbstractModel):
    _name = 'report.account_dashboard.account_dashboard_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('data ........', data)
        active_id = data.get('context').get('active_id')
        print('active id ................', active_id)
        account_data = self.env['mini.account.dashboard'].search([('id', '=', active_id)])
        print('convert to dict .......', account_data.mini_cash_dashboard_ids.read())
        print('account data ......................', account_data)
        date_day = fields.Datetime.now().strftime("%Y-%m-%d")
        print("......date_day", date_day)
        debit_customer = 0
        credit_supplier = 0
        debit_supplier = 0
        credit_customer = 0

        # recherche
        # pour afficher le solde fournisseur
        account_move_supplier = self.env['account.move'].search([
            ('invoice_date', '>=', account_data['start_date']),
            ('invoice_date', '<=', account_data['end_date']),
            ('move_type', '=', 'in_invoice'),
            ('state', '=', 'posted'),
        ])
        print("account_move_supplier", account_move_supplier)
        account_payment_supplier = self.env['account.payment'].search([
            ('date', '>=', account_data['start_date']),
            ('date', '<=', account_data['end_date']),
            ('payment_type', '=', 'outbound'),
            ('partner_type', '=', 'supplier'),
            ('state', '=', 'posted'),
        ])
        print("account_payment_supplier", account_payment_supplier)
        debit_supplier = sum(account_move_supplier.mapped('amount_total'))
        print('=========debit_supplier', debit_supplier)
        credit_supplier = sum(account_payment_supplier.mapped('amount'))
        print("=========credit supplier", credit_supplier)
        amount_supplier = debit_supplier - credit_supplier
        print('===amount supplier', amount_supplier)
        # recherche
        # pour afficher le solde client
        account_move_customer = self.env['account.move'].search([
            ('invoice_date', '>=', account_data['start_date']),
            ('invoice_date', '<=', account_data['end_date']),
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
        ])
        print('account_move_customer', account_move_customer)
        account_payment_customer = self.env['account.payment'].search([
            ('date', '>=', account_data['start_date']),
            ('date', '<=', account_data['end_date']),
            ('payment_type', '=', 'inbound'),
            ('partner_type', '=', 'customer'),
            ('state', '=', 'posted'),
        ])
        debit_customer = sum(account_move_customer.mapped('amount_total'))
        credit_customer = sum(account_payment_customer.mapped('amount'))
        amount_customer = - debit_customer + credit_customer
 
        amount_total_tresorerie = sum(record['amount'] for record in account_data.mini_cash_dashboard_ids.read())
        stock_amount = self.env['mini.account.dashboard'].get_stock_amount_qty()
        
        total_situation_nette = amount_total_tresorerie + amount_customer -(amount_supplier) + stock_amount

        return {
            'docs': account_data,
            'cash_data': account_data.mini_cash_dashboard_ids.read(),
            'customer_data': account_data.mini_customer_dashboard_ids.read(),
            'vendor_data': account_data.mini_vendor_dashboard_ids.read(),
            'date_day': date_day,
            'amount_supplier': amount_supplier,
            'amount_customer': amount_customer,
            'amount_total_tresorerie':amount_total_tresorerie,
            'stock_amount':stock_amount,
            'total_situation_nette': total_situation_nette
        }