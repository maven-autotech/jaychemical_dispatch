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

    ],

    'data': [
       'views/scan_button.xml',
       'views/scan_start_temp.xml',
        'views/manual_location.xml',
        'views/thank_you.xml',
        'views/manual_transfer.xml',
        'views/complete.xml',
        'views/thank_you.xml',
        'report/zpl_report.xml',

    ],
    'demo': [

    ],
   # 'qweb': ['static/src/xml/button.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,

 }
