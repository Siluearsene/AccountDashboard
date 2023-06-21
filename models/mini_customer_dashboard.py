# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MiniCustomerDashboard(models.Model):
    _name = 'mini.customer.dashboard'

    name = fields.Char(string='Reference')
    start_date = fields.Date(string='Date debut')
    end_date = fields.Date(string='Date fin')
    amount = fields.Integer(string='Montant')
    account_dashboard_customer_id = fields.Many2one('mini.account.dashboard', 'Dashboard')
    state = fields.Selection([('draft', 'En cours'), ('done', 'Terminer')], default='draft')
    journal_id = fields.Many2one('account.journal', 'Journal')
