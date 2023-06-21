# -*- coding: utf-8 -*-
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
        print("......date_day",date_day)
        
        # recherche 
        # pour afficher le solde fournisseur 
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
        # recherche 
        # pour afficher le solde client
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
        return {
            'docs': account_data,
            'cash_data': account_data.mini_cash_dashboard_ids.read(),
            'customer_data': account_data.mini_customer_dashboard_ids.read(),
            'vendor_data': account_data.mini_vendor_dashboard_ids.read(),
            'date_day':date_day
        }

