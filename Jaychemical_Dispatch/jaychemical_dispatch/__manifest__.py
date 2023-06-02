# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Scanning at time of Invert',
    'description': 'This is hospital management system in odoo 14',
    'summary': 'Invert serial/Lo',
    'category': 'Invert serial/Lo',
    'sequence': 1,
    'version': '1.0',
    'author': 'Maven Autotech Pvt Ltd',
    'website': 'https://www.mavenautomation.in',
    'depends': [
        'product',
        'website',
        'web',
        'stock',
        'purchase_stock',
        'stock_picking_batch',

    ],

    'data': [
       'security/ir.model.access.csv',
       'security/security_groups.xml',
        'views/manual_location.xml',
        'views/manual_transfer.xml',
        'views/purchase_views.xml',
        'views/complete.xml',
        'views/thank_you.xml',
        'views/stock_views.xml',
        'views/product_views.xml',
        'views/scan_qr_views.xml',
        'views/batch_scan.xml',
        'views/user_ip_address_view.xml',
        'views/location_view.xml',
        'views/delivery_scan.xml',
        'views/delivery_scan_submit.xml',
    ],
    'demo': [

    ],
   # 'qweb': ['static/src/xml/button.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,

 }
