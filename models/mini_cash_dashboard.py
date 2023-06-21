# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MiniCashDashboard(models.Model):
    _name = 'mini.cash.dashboard'

    journal_id = fields.Many2one('account.journal', 'Journal')
    name = fields.Char(string='Nom', related='journal_id.backend_name')
    amount = fields.Integer(string='Montant')
    account_dashboard_id = fields.Many2one('mini.account.dashboard', 'Dashboard')
    state = fields.Selection([('draft', 'En cours'), ('done', 'Terminer')])
    company_id = fields.Many2one('res.company', string='Entreprises')
