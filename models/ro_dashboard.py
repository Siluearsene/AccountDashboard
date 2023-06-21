# -*- coding: utf-8 -*-

import logging
import pytz
from odoo import models, fields, api, _
from datetime import timedelta, datetime
from odoo.exceptions import ValidationError
from odoo.http import request
from datetime import date

_logger = logging.getLogger(__name__)


class RoDashboard(models.Model):
    _inherit = 'repair.order'

    @api.model
    def get_repair_order_details(self, la_data=None):
        """Cette méthode calcule les différentes valeurs à afficher dans le Tableau de bord
        en fonction de l'argument la_data toute les variables à utiliser et afficher sur le
        Tableau de bord sont calculées et retournées par cette fonction
         Return : toute les variables à afficher dans le Dashboard
        """
        _logger.info("Test", request.session)
        current_cid = self.env['res.company'].browse(self._context.get('allowed_company_ids'))

        # Initialisation des variables à retourner
        total_cac = 0
        cac_mecha = 0
        cac_carrosserie = 0
        cac_painting = 0
        total_entree = 0
        entree_mecha = 0
        entree_carrosserie = 0
        entree_painting = 0
        cac_autre = 0
        ca_ht = 0
        ca_ttc = 0
        ca_cp = 0
        ca_cnp = 0
        ca_nc = 0
        ca_ht_autre = 0
        ca_ttc_autre = 0
        current_cid = current_cid.id
        company_id = current_cid

        repair_order = self.env['repair.order']  # Les ordres de réparations
        invoice_report = self.env['account.invoice.report']  # Les factures
        account_move = self.env['account.move']  # Les factures

        if la_data:  # Vérifie si une période est définie et sauvegardée dans la_data

            # Récupération des valeurs de start_date et end_date dans la_data
            # la_data est la variable contenant la période :

            # la_data = {
            # #############"start_date": "jour_début/mois_début/année_début",
            # #############"end_date": "jour_fin/mois_fin/année_fin",
            # ###########}

            start0 = la_data['start_date']
            end0 = la_data['end_date']

            print('start0 =', start0)
            print('end0 =', end0)
            if end0 < start0:
                print('erruerrr')
            else:
                print("c'est ok")
            # start0 = "jour_début/mois_début/année_début"
            # end0 = "jour_fin/mois_fin/année_fin"

            # Création de liste en fonction de ces valeurs
            start = start0.split("/")
            end = end0.split('/')

            # start = [jour_début, mois_début, année_début]
            # end = [jour_fin, mois_fin, année_fin]

            start_date = date(int(start[2]), int(start[1]), int(start[0]))  # Date de début de la période
            end_date = date(int(end[2]), int(end[1]), int(end[0]))  # Date de fin de la période

            """ CALCUL LE NOMBRE D'ENTRÉES """
            # Total entree tout atelier
            total_entree += len(repair_order.sudo().search([
                ('state', '!=', '92_cancel'),
                ('receipt_date', '>=', start_date),
                ('receipt_date', '<=', end_date)
            ]))

            # entrée tout atelier mécanique
            entree_mecha += len(repair_order.sudo().search([
                '|',
                ('service_mechanical', '=', True),
                ('service_gps', '=', True),
                ('state', '!=', '92_cancel'),
                ('receipt_date', '>=', start_date),
                ('receipt_date', '<=', end_date)
            ]))
            # entrée tout atelier tôlerie
            entree_carrosserie += len(repair_order.sudo().search([
                ('service_bodywork', '=', True),
                ('receipt_date', '>=', start_date),
                ('receipt_date', '<=', end_date),
                ('state', '!=', '92_cancel')
            ]))
            # entrée tout atelier peinture
            entree_painting += len(repair_order.sudo().search([
                ('service_painting', '=', True),
                ('receipt_date', '>=', start_date),
                ('receipt_date', '<=', end_date),
                ('state', '!=', '92_cancel')
            ]))

            """ CALCUL CHIFFRE D'AFFAIRES HORS-TAXES """

            # Calcul du chiffre d'affaires hors-taxes relié à aucun atelier
            ca_ht_autre += sum(invoice_report.sudo().search([
                ('category_type', 'not in', ['mechanical', 'sheet_metal', 'painting']),
                ('state', 'not in', ['draft', 'cancel']),
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', start_date),
                ('invoice_date', '<=', end_date),
                ('price_subtotal', '>=', 0)
            ]).mapped('price_subtotal'))

            # Total chiffre d'affaires hors-taxes
            ca_ht += (sum(invoice_report.sudo().search([
                ('state', 'not in', ['draft', 'cancel']),
                ('move_type', '=', 'out_invoice'),
                ('price_subtotal', '>=', 0),
                ('invoice_date', '>=', start_date),
                ('invoice_date', '<=', end_date)
            ]).mapped('price_subtotal')))
            ca_ht = format(int(ca_ht), ",d").replace(",", " ") + " CFA"
            ca_ht_autre = format(int(ca_ht_autre), ",d").replace(",", " ") + " CFA"

            """ CALCUL CHIFFRE D'AFFAIRES TOUTES TAXES CONFONDUES """

            # Calcul du chiffre d'affaires TTC relié à aucun atelier
            ca_ttc_autre += sum(account_move.sudo().search([
                ('state', 'not in', ['draft', 'cancel']),
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', start_date),
                ('invoice_date', '<=', end_date),
                ('amount_total', '>=', 0)
            ]).mapped('amount_total'))
            ca_ttc_autre = format(int(ca_ttc_autre), ",d").replace(",", " ") + " CFA"

            # Total chiffre d'affaires TTC
            ca_ttc += (sum(account_move.sudo().search([
                ('state', 'not in', ['draft', 'cancel']),
                ('move_type', '=', 'out_invoice'),
                ('amount_total', '>=', 0),
                ('invoice_date', '>=', start_date),
                ('invoice_date', '<=', end_date)
            ]).mapped('amount_total')))
            ca_ttc = format(int(ca_ttc), ",d").replace(",", " ") + " CFA"

            """ CALCUL CHIFFRE D'AFFAIRES COMPTABILISÉ ET NON-PAYÉ """

            # Total chiffre d'affaires comptabilisé et non-payé
            ca_cnp += (sum(account_move.sudo().search([
                ('state', '=', 'posted'),
                ('move_type', '=', 'out_invoice'),
                ('payment_state', '!=', 'paid'),
                ('invoice_date', '>=', start_date),
                ('invoice_date', '<=', end_date),
                ('amount_total', '>=', 0)
            ]).mapped('amount_total')))
            ca_cnp = format(int(ca_cnp), ",d").replace(",", " ") + " CFA"

            """ CALCUL CHIFFRE D'AFFAIRES NON COMPTABILISÉ TTC """

            # Total chiffre d'affaires non comptabilisé ttc
            ca_nc += (sum(account_move.sudo().search([
                ('state', '=', 'draft'),
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', start_date),
                ('invoice_date', '<=', end_date),
                ('amount_total', '>=', 0)
            ]).mapped('amount_total')))
            ca_nc = format(int(ca_nc), ",d").replace(",", " ") + " CFA"

            """ CALCUL CHIFFRE D'AFFAIRES COMPTABILISÉ ET PAYÉ """

            # Total chiffre d'affaires comptabilisé et payé
            ca_cp += (sum(account_move.sudo().search([
                ('state', '=', 'posted'),
                ('move_type', '=', 'out_invoice'),
                ('payment_state', '=', 'paid'),
                ('invoice_date', '>=', start_date),
                ('invoice_date', '<=', end_date),
                ('amount_total', '>=', 0)
            ]).mapped('amount_total')))
            ca_cp = format(int(ca_cp), ",d").replace(",", " ") + " CFA"

            """ CALCUL CHIFFRE D'AFFAIRES COMPTABILITÉ HT """

            # Calcul du chiffre d'affaires comptabilité
            cac_autre += sum(invoice_report.sudo().search([  # chiffre d'affaires comptabilité hors atelier
                ('category_type', 'not in', ['mechanical', 'sheet_metal', 'painting']),
                ('state', 'not in', ['draft', 'cancel']),
                ('move_type', '=', 'out_invoice'),
                ('price_subtotal', '>=', 0),
                ('invoice_date', '>=', start_date),
                ('invoice_date', '<=', end_date)
            ]).mapped('price_subtotal'))
            cac_autre = format(int(cac_autre), ",d").replace(",", " ") + " CFA"

            # chiffre d'affaires comptabilité atelier mécanique
            cac_mecha += sum(invoice_report.sudo().search([
                ('category_type', '=', 'mechanical'),
                ('state', 'not in', ['draft', 'cancel']),
                ('move_type', '=', 'out_invoice'),
                ('price_subtotal', '>=', 0),
                ('invoice_date', '>=', start_date),
                ('invoice_date', '<=', end_date)
            ]).mapped('price_subtotal'))
            cac_mecha = format(int(cac_mecha), ",d").replace(",", " ") + " CFA"

            # chiffre d'affaires comptabilité atelier tôlerie
            cac_carrosserie += sum(invoice_report.sudo().search([
                ('category_type', '=', 'sheet_metal'),
                ('state', 'not in', ['draft', 'cancel']),
                ('move_type', '=', 'out_invoice'),
                ('price_subtotal', '>=', 0),
                ('invoice_date', '>=', start_date),
                ('invoice_date', '<=', end_date)
            ]).mapped('price_subtotal'))
            cac_carrosserie = format(int(cac_carrosserie), ",d").replace(",", " ") + " CFA"

            # chiffre d'affaires comptabilité atelier peinture
            cac_painting += sum(invoice_report.sudo().search([
                ('category_type', '=', 'painting'),
                ('state', 'not in', ['draft', 'cancel']),
                ('move_type', '=', 'out_invoice'),
                ('price_subtotal', '>=', 0),
                ('invoice_date', '>=', start_date),
                ('invoice_date', '<=', end_date)
            ]).mapped('price_subtotal'))
            cac_painting = format(int(cac_painting), ",d").replace(",", " ") + " CFA"

        else:  # Sinon, charger les données d'ensemble sur le dashboard
            # Calcule du nombre d'entrées

            # Pour le traitement du top 10 des articles les plus utilsés
            # transfert_lines : récupère toutes les lignes de chaque opération de transfert
            # transfert_lines = self.env['stock.picking'].sudo().search([]).move_ids_without_package
            # all_names = list(# les noms des articles de chaque ligne
            #     set(line.product_id.name for line in transfert_lines if line.quantity_done != float(0)))

            """ CALCUL LE NOMBRE D'ENTRÉES """

            # Nombre d'entrées tout atelier
            total_entree += len(repair_order.sudo().search([
                ('state', '!=', '92_cancel')
            ]))

            # Nombre d'entrés ateliers mécanique
            entree_mecha += len(repair_order.sudo().search([
                '|',
                ('service_mechanical', '=', True),
                ('service_gps', '=', True),
                ('state', '!=', '92_cancel')
            ]))

            # Nombre d'entrés ateliers tôlerie
            entree_carrosserie += len(repair_order.sudo().search([
                ('service_bodywork', '=', True),
                ('state', '!=', '92_cancel')
            ]))

            # Nombre d'entrés ateliers peinture
            entree_painting += len(repair_order.sudo().search([
                ('service_painting', '=', True),
                ('state', '!=', '92_cancel')
            ]))

            """ CALCUL CHIFFRE D'AFFAIRES HORS-TAXES """

            # Calcul du chiffre d'affaires hors-taxes relié à aucun atelier
            ca_ht_autre += sum(invoice_report.sudo().search([
                ('category_type', 'not in', ['mechanical', 'sheet_metal', 'painting']),
                ('state', 'not in', ['draft', 'cancel']),
                ('move_type', '=', 'out_invoice'),
                ('price_subtotal', '>=', 0)
            ]).mapped('price_subtotal'))

            # Total chiffre d'affaires hors-taxes
            ca_ht += (sum(invoice_report.sudo().search([
                ('state', 'not in', ['draft', 'cancel']),
                ('move_type', '=', 'out_invoice'),
                ('price_subtotal', '>=', 0)
            ]).mapped('price_subtotal')))
            ca_ht = format(int(ca_ht), ",d").replace(",", " ") + " CFA"
            ca_ht_autre = format(int(ca_ht_autre), ",d").replace(",", " ") + " CFA"

            """ CALCUL CHIFFRE D'AFFAIRES TOUTES TAXES CONFONDUES """

            # Total chiffre d'affaires TTC
            ca_ttc += (sum(account_move.sudo().search([
                ('state', 'not in', ['draft', 'cancel']),
                ('move_type', '=', 'out_invoice'),
                ('amount_total', '>=', 0)
            ]).mapped('amount_total')))
            ca_ttc = format(int(ca_ttc), ",d").replace(",", " ") + " CFA"

            """ CALCUL CHIFFRE D'AFFAIRES COMPTABILISÉ ET NON-PAYÉ """

            # Total chiffre d'affaires comptabilisé et non-payé
            ca_cnp += (sum(account_move.sudo().search([
                ('state', '=', 'posted'),
                ('move_type', '=', 'out_invoice'),
                ('payment_state', '!=', 'paid'),
                ('amount_total', '>=', 0)
            ]).mapped('amount_total')))
            ca_cnp = format(int(ca_cnp), ",d").replace(",", " ") + " CFA"

            """ CALCUL CHIFFRE D'AFFAIRES NON COMPTABILISÉ TTC """

            # Total chiffre d'affaires non comptabilisé ttc
            ca_nc += (sum(account_move.sudo().search([
                ('state', '=', 'draft'),
                ('move_type', '=', 'out_invoice'),
                ('amount_total', '>=', 0)
            ]).mapped('amount_total')))
            ca_nc = format(int(ca_nc), ",d").replace(",", " ") + " CFA"

            """ CALCUL CHIFFRE D'AFFAIRES COMPTABILISÉ ET PAYÉ """

            # Total chiffre d'affaires comptabilisé et payé
            ca_cp += (sum(account_move.sudo().search([
                ('state', '=', 'posted'),
                ('move_type', '=', 'out_invoice'),
                ('payment_state', '=', 'paid'),
                ('amount_total', '>=', 0)
            ]).mapped('amount_total')))
            ca_cp = format(int(ca_cp), ",d").replace(",", " ") + " CFA"

            """ CALCUL CHIFFRE D'AFFAIRES COMPTABILITÉ """

            # chiffre d'affaires comptabilité hors atelier
            cac_autre += sum(invoice_report.sudo().search([
                ('category_type', 'not in', ['mechanical', 'sheet_metal', 'painting']),
                ('state', 'not in', ['draft', 'cancel']),
                ('move_type', '=', 'out_invoice'),
                ('price_subtotal', '>=', 0)
            ]).mapped('price_subtotal'))
            cac_autre = format(int(cac_autre), ",d").replace(",", " ") + " CFA"

            # chiffre d'affaires comptabilité atelier mécanique
            cac_mecha += sum(invoice_report.sudo().search([
                ('category_type', '=', 'mechanical'),
                ('state', 'not in', ['draft', 'cancel']),
                ('move_type', '=', 'out_invoice'),
                ('price_subtotal', '>=', 0)
            ]).mapped('price_subtotal'))
            cac_mecha = format(int(cac_mecha), ",d").replace(",", " ") + " CFA"

            # chiffre d'affaires comptabilité atelier tôlerie
            cac_carrosserie += sum(invoice_report.sudo().search([
                ('category_type', '=', 'sheet_metal'),
                ('state', 'not in', ['draft', 'cancel']),
                ('move_type', '=', 'out_invoice'),
                ('price_subtotal', '>=', 0)
            ]).mapped('price_subtotal'))
            cac_carrosserie = format(int(cac_carrosserie), ",d").replace(",", " ") + " CFA"

            # chiffre d'affaires comptabilité atelier peinture
            cac_painting += sum(invoice_report.sudo().search([
                ('category_type', '=', 'painting'),
                ('state', 'not in', ['draft', 'cancel']),
                ('move_type', '=', 'out_invoice'),
                ('price_subtotal', '>=', 0)
            ]).mapped('price_subtotal'))
            cac_painting = format(int(cac_painting), ",d").replace(",", " ") + " CFA"

        # Récupération du nom de l'entreprise
        company_name = self.env['res.company'].sudo().search([('id', '=', int(company_id))]).name

        return {
            'total_entree': total_entree,
            'entree_mecha': entree_mecha,
            'entree_carrosserie': entree_carrosserie,
            'entree_painting': entree_painting,
            'ca_ht': ca_ht,
            'ca_ttc': ca_ttc,
            'ca_cnp': ca_cnp,
            'ca_nc': ca_nc,
            'ca_cp': ca_cp,
            'ca_ht_autre': ca_ht_autre,
            'total_cac': total_cac,
            'cac_mecha': cac_mecha,
            'cac_carrosserie': cac_carrosserie,
            'cac_painting': cac_painting,
            'company_name': company_name,
            'entree_autre': 0,
            'cac_autre': cac_autre
        }

    def get_report_by_month(self, report_list, report, field):
        """Cette méthode permet de calculer les chiffes d'affaires ventes/comptabilité pour chaque mois de l'année en
        cours. En fonction de la valeur de 'field', la méthode calculera les chiffres d'affaires vente ou compta
        Les différentes valeurs pour les 12 mois de l'année en cours sont enregistrées dans la liste report_list
        passée en commentaire.
        'report_list' sera modifiée"""

        # Récupération de l'année en cours
        today = date.today()
        year = today.year

        # on prend les 12 mois de l'année avec leur valeur numérique
        for month in range(1, 13):
            # calcule des dates des début et fin du mois dont la valeur numérique est 'month'
            first_day = date(year, month, 1)  # Date du premier jour du mois 'month'

            # Date du dernier jour du mois 'month'
            last_day = first_day.replace(day=28) + timedelta(days=4)
            last_day = last_day - timedelta(days=last_day.day)

            # si field = 'date' on calcule les chiffres d'affaires vente
            if field == 'date':
                cav_total = sum(report.sudo().search([
                    ('state', '=', 'sale'),
                    ('price_subtotal', '>=', 0),
                    (field, '>=', first_day),
                    (field, '<=', last_day)
                ]).mapped('price_subtotal'))
                report_list.append(cav_total)
            # si field = 'invoice_date' on calcule les chiffres d'affaires comptabilité
            elif field == 'invoice_date':
                cac_total = sum(report.sudo().search([
                    ('state', 'not in', ['draft', 'cancel']),
                    ('price_subtotal', '>=', 0),
                    ('move_type', '=', 'out_invoice'),
                    ('invoice_date', '>=', first_day),
                    ('invoice_date', '<=', last_day)
                ]).mapped('price_subtotal'))
                report_list.append(cac_total)
            else:  # Sinon on stop la boucle et rien ne se passe
                break

    @api.model
    def get_sale_report(self, ):
        """Cette methode calcule les différentes valeurs pour la construction du graph du chiffre d'affaires
         vente par mois"""

        sale_report = self.env['sale.report']  # les ventes

        sales = []  # Les différentes valeurs
        month = [  # Pour la légende du graph. Chaque mois correspond à une valeur
            'Janvier',
            'Février',
            'Mars',
            'Avril',
            'Mai',
            'Juin',
            'Juillet',
            'Août',
            'Septembre',
            'Octobre',
            'Novembre',
            'Décembre',
        ]

        self.get_report_by_month(sales, sale_report, 'date')  # Calcule des différentes données du graph

        # len(sales) = len(month)

        final = [sales, month]  # la variable retournée pour la construction du graph
        return final

    @api.model
    def get_invoice_report(self, ):
        """Cette methode calcule les différentes valeurs pour la construction du graph du chiffre d'affaires
         comptabilité par mois"""

        invoice_report = self.env['account.invoice.report']  # les factures

        invoices = []  # les différentes valeurs
        month = [  # pour lé légende du graph
            'Janvier',
            'Février',
            'Mars',
            'Avril',
            'Mai',
            'Juin',
            'Juillet',
            'Août',
            'Septembre',
            'Octobre',
            'Novembre',
            'Décembre',
        ]

        self.get_report_by_month(invoices, invoice_report, 'invoice_date')  # Calcule des différentes données du graph

        # len(invoices) = len(month)

        final = [invoices, month]  # la variable retournée pour la construction du graph
        return final

    @api.model
    def get_atelier_report(self, la_data=None):
        """Cette méthode compte les ordres de réparation pour chaque atelier pour les afficher dans le graph"""

        repair_order = self.env['repair.order']  # Les ordres de réparations
        atelier_name = ['Mécanique', 'Tôlerie', 'Peinture']  # Les labels pour chaque atelier

        if la_data:  # Vérifie si une période est définie et sauvegardée dans la_data

            # Récupération des valeurs de start_date et end_date dans la_data
            # la_data est la variable contenant la période :

            # la_data = {
            # #############"start_date": "jour_début/mois_début/année_début",
            # #############"end_date": "jour_fin/mois_fin/année_fin",
            # ###########}

            start0 = la_data['start_date']
            end0 = la_data['end_date']

            # start0 = "jour_début/mois_début/année_début"
            # end0 = "jour_fin/mois_fin/année_fin"

            # Création de liste en fonction de ces valeurs
            start = start0.split("/")
            end = end0.split('/')

            # start = [jour_début, mois_début, année_début]
            # end = [jour_fin, mois_fin, année_fin]

            start_date = date(int(start[2]), int(start[1]), int(start[0]))  # Date de début de la période
            end_date = date(int(end[2]), int(end[1]), int(end[0]))  # Date de fin de la période

            entree_mecha = len(repair_order.sudo().search([  # Nombre d'entrées pour l'atelier mécanique
                '|',
                ('service_mechanical', '=', True),
                ('service_gps', '=', True),
                ('state', '!=', '92_cancel'),
                ('receipt_date', '>=', start_date),
                ('receipt_date', '<=', end_date)
            ]))
            entree_carrosserie = len(repair_order.sudo().search([  # Nombre d'entrées pour l'atelier tôlerie
                ('service_bodywork', '=', True),
                ('receipt_date', '>=', start_date),
                ('receipt_date', '<=', end_date),
                ('state', '!=', '92_cancel')
            ]))
            entree_painting = len(repair_order.sudo().search([  # Nombre d'entrées pour l'atelier painting
                ('service_painting', '=', True),
                ('receipt_date', '>=', start_date),
                ('receipt_date', '<=', end_date),
                ('state', '!=', '92_cancel')
            ]))
        else:  # Sinon récupère les données globales
            entree_mecha = len(repair_order.sudo().search([  # Nombre d'entrées pour l'atelier mécanique
                '|',
                ('service_mechanical', '=', True),
                ('service_gps', '=', True),
                ('state', '!=', '92_cancel')
            ]))
            entree_carrosserie = len(repair_order.sudo().search([  # Nombre d'entrées pour l'atelier tôlerie
                ('service_bodywork', '=', True),
                ('state', '!=', '92_cancel')
            ]))
            entree_painting = len(repair_order.sudo().search([  # Nombre d'entrées pour l'atelier painting
                ('service_painting', '=', True),
                ('state', '!=', '92_cancel')
            ]))

        entrees = [entree_mecha, entree_carrosserie, entree_painting]  # La variable des différentes valeurs du graph
        final = [entrees, atelier_name]
        return final
