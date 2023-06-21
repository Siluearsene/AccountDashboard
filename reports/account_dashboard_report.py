# -*- coding: utf-8 -*-
from odoo import models, api, fields
from datetime import datetime


class AccountDashboardReport(models.AbstractModel):
    _name = 'report.dashboard_account.account_dashboard_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('data ........', data)
        active_id = data.get('context').get('active_id')
        print('active id ................', active_id)
        account_data = self.env['mini.account.dashboard'].search([('id', '=', active_id)])
        print('convert to dict .......', account_data.mini_cash_dashboard_ids.read())
        print('account data ......................', account_data)
        return {
            'docs': account_data,
            'cash_data': account_data.mini_cash_dashboard_ids.read(),
            'customer_data': account_data.mini_customer_dashboard_ids.read(),
            'vendor_data': account_data.mini_vendor_dashboard_ids.read()

        }

