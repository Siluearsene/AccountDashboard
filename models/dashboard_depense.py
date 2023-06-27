from odoo import models, fields, api, _


class DepenseDashboard(models.Model):
    _name = 'depense.dashboard'
    _order='create_date DESC'
    _check_company_auto = True

    date = fields.Date(string="date transaction")
    type_transaction = fields.Selection(
        [('in', 'Entrée'), ('out', 'Sortie')],
        string='Type de transaction',
        default='in',
        required=True
    )
    account_statement_line_id = fields.Many2one('account.bank.statement.line')
    depense = fields.Many2one('account.label', string='Dépense')
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        compute='_compute_journal_id', store=True,
        check_company=True,
    )
    payment_ref = fields.Char(string='intitulé de depense')
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partenaire', ondelete='restrict',
        domain="['|', ('parent_id','=', False), ('is_company','=',True)]",
        check_company=True)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Journal Currency',
        check_company=True,
        compute='_compute_currency_id', store=True,
    )
    amount = fields.Monetary(string="montant")
    solde = fields.Monetary(string="solde")

    


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    def action_save_close(self):
        new_line = self.env['depense.dashboard'].create({
            "account_statement_line_id": self.id,
            'date': self.date,
            'type_transaction': self.transaction_type,
            'depense': self.depense.id,
            'journal_id': self.journal_id.id,
            'payment_ref': self.payment_ref,
            'partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'amount': self.amount,
        })
        return super().action_save_close()

    def action_save_new(self):
        new_line = self.env['depense.dashboard'].create({
            "account_statement_line_id": self.id,
            'date': self.date,
            'type_transaction': self.transaction_type,
            'depense': self.depense.id,
            'journal_id': self.journal_id.id,
            'payment_ref': self.payment_ref,
            'partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'amount': self.amount,
        })
        return super().action_save_new()
    def unlink(self):
        res = super().unlink()
        depense_dashboard = self.env['depense.dashboard'].search([('account_statement_line_id','=',self.id)])
        if depense_dashboard:
            depense_dashboard.unlink()  
        return res

        

