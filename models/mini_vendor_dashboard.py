# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MiniVendorDashboard(models.Model):
    _name = 'mini.vendor.dashboard'

    name = fields.Char(string='Reference')
    start_date = fields.Date(string='Date debut')
    end_date = fields.Date(string='Date fin')
    amount = fields.Integer(string='Montant')
    account_dashboard_vendor_id = fields.Many2one('mini.account.dashboard', 'Dashboard')
    state = fields.Selection([('draft', 'En cours'), ('done', 'Terminer')], default='draft')
    journal_id = fields.Many2one('account.journal', 'Journal')
