# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    backend_name = fields.Char(string='Nom affiché')
