from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError
import json
import requests
from requests.auth import HTTPBasicAuth


class ScanBarcode(models.Model):
    _inherit = "stock.picking"

    tmp_name = fields.Char('Reference', readonly=True)
    fifo_list = fields.Text('FIFO_list',readonly=True)

    def start_scan_picking(self):
        # user_picking = self.env['user.picking'].sudo().search([('user_id', '=', self.env.uid)])
        # print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",str(self._context.get('name')),self)
        # if self._context.get('direct'):
            url = "/scan_manual_transfer?source=" + str(self.name)
            # if user_picking:
            #     user_picking.write({'picking_name': str(self._context.get('name'))})
            # else:
            #     user_picking.create({'user_id': self.env.uid, 'picking_name': self.name})
            return {'type': 'ir.actions.act_url',
                    'target': 'self',
                    'url': url,}
        # else:
        #     print("666666666666666666666666666")
        #     url = "/scan_manual_transfer?source=" + str(self.name)
        #     if user_picking:
        #         user_picking.write({'picking_name': self.name})
        #     else:
        #         user_picking.create({'user_id': self.env.uid, 'picking_name': self.name})
        #     return {'type': 'ir.actions.act_url',
        #             'target': 'self',
        #             'url': url, }

