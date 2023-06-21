# -*- coding: utf-8 -*-
{
    'name': "Repair Order Dashboard Pagani",
    'version': '16.0.1.0.2',
    'summary': """RO Dashboard""",
    'description': """Repair Order Dashboard""",
    'category': 'Dashboard',
    'author': 'Emmanuel Seri Koubi',
    'website': "https://www.progistack.com",
    'depends': ['account', 'repair_order', 'sale', 'permission_manager'],
    'data': [
        'views/dashboard_menues.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'repair_order_dashboard/static/src/xml/ro_dashboard.xml',
            'repair_order_dashboard/static/src/js/ro_dashboard.js',
            'repair_order_dashboard/static/src/css/ro_dashboard.css',
            'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.8.0/Chart.bundle.js',
        ],
    },
    'license': "AGPL-3",
    'installable': True,
    'application': False,
}
