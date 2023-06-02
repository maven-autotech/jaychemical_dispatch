from odoo import models, fields
import requests
import json
import requests
from requests.auth import HTTPBasicAuth
import datetime
from dateutil import parser


class ProductTemplate(models.Model):
    _inherit = "product.template"

    varient_code = fields.Char(string= "Varient Code")
    

    def create_product(self):
        url = "http://103.54.21.182:5913/JAYUATWEB/OData/Company('JAY')/ItemMaster?$format=json"
        payload = ""
        headers = {
            'Accept': 'application/json'
        }
        response = requests.request("GET", url, headers=headers,
                                    auth=HTTPBasicAuth("JAYDEV-PC\JAYMIND1", "proBook@321"))
        res = json.loads(response.text)
        create_vals = []

        for rec in res['value']:
            varient_name = rec['Item_No'] + '_' + rec['Variant_Code']
            pro_obj_varient = self.env['product.template'].sudo().search([('name', '=',varient_name)])
            pro_obj = self.env['product.template'].sudo().search([('name', '=',rec['Item_No'])])
            if not pro_obj:
                pro_obj.create(
                    {'name': rec['Item_No'] ,
                      'description': rec['Item_Name'],
                     'varient_code': rec['Variant_Code'],
                     'tracking': 'lot',
                     'detailed_type': 'product',
                     })
            else:
                if not pro_obj_varient:
                    create_vals.append({
                              'name': rec['Item_No'] + '_' + rec['Variant_Code'],
                              'varient_code': rec['Variant_Code'],
                              'description': rec['Item_Name'],
                              'tracking': 'lot',
                              'detailed_type': 'product',
                          })
        if create_vals:
            self.create(create_vals)






