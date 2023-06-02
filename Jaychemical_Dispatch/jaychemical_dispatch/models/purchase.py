from odoo import models, fields, api,_
from odoo.exceptions import UserError
import datetime
import requests
from requests.auth import HTTPBasicAuth
import json
from odoo.osv import expression

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    lot_number = fields.Char("Lot Number")
    line_no = fields.Char("Line No")
    pack_size = fields.Integer(string="Pack Size")
    total_qty = fields.Integer(string="Total Quantity")
    # unit_of_measurement = fields.Char(string="Unit of Measure cus")
    # purity = fields.Char(string="Purity")

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        self.ensure_one()
        self._check_orderpoint_picking_type()
        product = self.product_id.with_context(lang=self.order_id.dest_address_id.lang or self.env.user.lang)
        date_planned = self.date_planned or self.order_id.date_planned
        return {
            # truncate to 2000 to avoid triggering index limit error
            # TODO: remove index in master?
            'name': (self.product_id.display_name or '')[:2000],
            'product_id': self.product_id.id,
            'lot_number': self.lot_number,
            'line_no':self.line_no,
            'pack_size':self.pack_size,
            'total_qty':self.total_qty,
            # 'purity':self.purity,
            # 'unit_of_measurement': self.unit_of_measurement,
            'date': date_planned,
            'date_deadline': date_planned,
            'location_id': self.order_id.partner_id.property_stock_supplier.id,
            'location_dest_id': (self.orderpoint_id and not (
                    self.move_ids | self.move_dest_ids)) and self.orderpoint_id.location_id.id or self.order_id._get_destination_location(),
            'picking_id': picking.id,
            'partner_id': self.order_id.dest_address_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'purchase_line_id': self.id,
            'company_id': self.order_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': self.order_id.picking_type_id.id,
            'group_id': self.order_id.group_id.id,
            'origin': self.order_id.name,
            'description_picking': product.description_pickingin or self.name,
            'propagate_cancel': self.propagate_cancel,
            'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
            'product_uom_qty': product_uom_qty,
            'product_uom': product_uom.id,
            'product_packaging_id': self.product_packaging_id.id,
            'sequence': self.sequence,
        }

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def create_po(self, scan_number=None):
        url = "http://103.54.21.182:5913/JAYUATWEB/OData/Company('JAY')/PostedPurchaseReceiptLines?$format=json"
        payload = ""
        headers = {
            'Accept': 'application/json'
        }
        response = requests.request("GET", url, headers=headers,
                                    auth=HTTPBasicAuth("JAYDEV-PC\JAYMIND1", "proBook@321"))
        res = json.loads(response.text)
        date_format = '%Y-%m-%dT%H:%M:%S'
        list_grn = []

        context = self._context

        current_uid = context.get('uid')

        user = self.env['res.users'].browse(current_uid)
        user_warehouse = user.allowed_warehouse.name

        for rec1 in res['value']:
            if rec1['GRN_No'] == scan_number:
                list_grn.append(rec1)
        print("OOOOOOOOOOOOOOOOOOOO",list_grn)

        if len(list_grn) != 0:
            for rec in list_grn:
                print("&&&&&&&&&&&&&&&&&&&&&",rec,scan_number)
                purchase_obj = self.env['purchase.order'].sudo().search(
                    [('name', '=', scan_number)])
                pro_obj = self.env['product.product'].sudo().search([('name', '=', rec['Item_No'])])
                stock_warehouse_obj = self.env['stock.warehouse'].sudo().search([('location_code', '=', rec['Accloc'])])
                stock_pick = self.env['stock.picking.type'].sudo().search(
                    [('warehouse_id', '=', stock_warehouse_obj.id), ('name', '=', 'Receipts')])

                print("+++++++++++++++++++",user_warehouse,stock_warehouse_obj.name)

                if not pro_obj:
                    raise UserError("Please Create Product...............")
                elif user_warehouse != stock_warehouse_obj.name and user_warehouse != False:
                    raise UserError("Not allowed to scan")
                else:
                    if not purchase_obj and stock_warehouse_obj:
                        purchase_obj = purchase_obj.create({
                            'name': rec['GRN_No'],
                            'partner_id': 3,
                            'picking_type_id': stock_pick.id,
                        })
                        if purchase_obj:
                            purchase_obj_line = purchase_obj.order_line.create({
                                'order_id':purchase_obj.id,
                                'product_id': pro_obj.id,
                                'name': pro_obj.description,
                                'line_no': rec['Line_No'],
                                'unit_of_measurement': rec['Unit_of_Measure'],
                                'lot_number': rec['Lot_No'],
                                'product_qty': rec['Quantity'],
                            })
                    elif purchase_obj and stock_warehouse_obj and purchase_obj.state == 'draft':
                        purchase_obj_line = purchase_obj.order_line.create({
                            'order_id': purchase_obj.id,
                            'product_id': pro_obj.id,
                            'name': pro_obj.description,
                            'line_no': rec['Line_No'],
                            'unit_of_measurement': rec['Unit_of_Measure'],
                            'lot_number': rec['Lot_No'],
                            'product_qty': rec['Quantity'],

                        })
            purchase_obj.button_confirm()
            return purchase_obj
        else:
            raise UserError("GRN NO NOT VALID...............")

    def _prepare_picking(self):
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.name,
                'partner_id': self.partner_id.id
            })
        if not self.partner_id.property_stock_supplier.id:
            raise UserError(_("You must set a Vendor Location for this partner %s", self.partner_id.name))
        return {
            'picking_type_id': self.picking_type_id.id,
            'partner_id': self.partner_id.id,
            'user_id': self.user_id.id,
            'date': self.date_order,
            'origin': self.name,
            'location_dest_id': self._get_destination_location(),
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id,
        }

    def action_confirm(self):
        for order in self:
            if order.state not in ['sent', 'purchase']:
                print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                order.button_confirm()
            else:
                raise UserError("Please select GRN with RFQ state")

