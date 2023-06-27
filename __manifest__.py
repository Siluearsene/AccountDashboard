# -*- coding: utf-8 -*-
{
    'name': "Repair Order Dashboard Pagani",
    'version': '16.0.1.0.2',
    'summary': """RO Dashboard""",
    'description': """Repair Order Dashboard""",
    'category': 'Dashboard',
    'author': 'Emmanuel Seri Koubi',
    'website': "https://www.progistack.com",
    'depends': ['account_accountant','account_optimization'],
    'data': [
        'security/ir.model.access.csv',
        'views/mini_account_dashbord_view.xml',
        'views/dashboard_depense.xml',
        'views/views.xml',
        'views/dashboard_views.xml',
        'reports/account_dashboard_report.xml',
        'wizard/search_popup.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'account_dashboard/static/src/js/account_dashboard.js',
            'account_dashboard/static/src/xml/account_dashboard.xml',
            'account_dashboard/static/src/css/ro_dashboard.css',
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.8.0/Chart.bundle.js',
        ],
    },
    'license': "AGPL-3",
    'installable': True,
    'application': False,
}
