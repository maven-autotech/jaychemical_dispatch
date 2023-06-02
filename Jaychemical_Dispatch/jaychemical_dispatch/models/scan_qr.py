from odoo import fields, models, api
from odoo.exceptions import UserError
import datetime
import requests
import json
import requests
from requests_ntlm import HttpNtlmAuth



class ScanQr(models.Model):
    _name = "scan.qr"
    _description = "scan qr"

    name = fields.Char(require=True)

    def start_scan(self):
        name1 = self.name
        print("KKKKKKKKKKKKKKKKKKKKKK",name1)
        purchase = self.env['purchase.order'].create_po(name1)
        stock = self.env['stock.picking'].sudo().search([('origin', '=', name1),('picking_type_id.name','=','Receipts'),('state','=','assigned')])
        print("KMMMMMMMMMMMMMMMMMM",stock)
        if len(stock) != 0:
            try:
                return {
                    'name': "Receipts form",
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.picking',
                    'view_id': self.env.ref('stock.view_picking_form').id,
                    'res_id': stock.id,
                }
            except:
                return {
                    'name': "Receipts form",
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.picking',
                    'view_id': self.env.ref('stock.view_picking_form').id,
                    'res_id': stock.id,
                }
        else:
            raise UserError("This GRN already scanned")
