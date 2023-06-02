from odoo import models, fields, api,_
from odoo.exceptions import UserError
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
import json


class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    location_code = fields.Char("Location Code")
    # allowed_users = fields.Many2many(
    #     string="Allowed Users",
    #     comodel_name="res.users",
    #     help="""Users allowed to do operation/move from/to this location"""
    #          """, others users will have a popup error on transfert action""",
    # )


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    total_qty = fields.Float("Total Quantity")
    line_no = fields.Char(string="Line No")
    location_code = fields.Char("Location Code")
    posting_date = fields.Datetime(string="LR DATE")
    unit_of_measurement = fields.Char(string="Unit of Measure")
    purity = fields.Char("Purity")

    def action_submit(self):

        url = "/select_product?id=" + str(self.id)
        print("LLLLLLLLLLLLLLLLLLLL", url)
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': url,
            'tag': 'reload',
        }

    def start_scan_picking(self):
        url = "/scan_manual_transfer?source=" + str(self.name)
        return {'type': 'ir.actions.act_url',
                'target': 'self',
                'url': url, }



    def action_delivery_controller(self):
        print("HUUUUUUUUUUUUUURRRRRRRRRRRAAAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
        url = "/delivery_controller?delivery=" + str(self.name)
        return {'type': 'ir.actions.act_url',
                'target': 'self',
                'url': url, }


class StockMove(models.Model):
    _inherit = 'stock.move'

    total_qty = fields.Float("Total Quantity")
    lot_number = fields.Char(string="Lot Number")
    pack_size = fields.Float(string="Pack Size")# compute='_total_packsize')
    line_no = fields.Char(string="Line No")
    location_code = fields.Char("Location Code")
    posting_date = fields.Datetime(string="LR DATE")
    unit_of_measurement = fields.Char(string="Unit of Measure")
    purity = fields.Char("Purity")

    def action_network_printing(self):

        from ipaddress import ip_address
        import socket
        import requests
        user_obj = self.env['user.ip.address'].sudo().search([('name', '=', self.env.uid)])
        ip_address = user_obj.printer_ip_address
        port = 9100
        for rec in self.move_line_nosuggest_ids:
            recipt_name = self.name
            product_code1 = str(self.product_id.description).split('<p>')
            pro = str(product_code1[1]).split('</p>')[0]
            product_code = pro
            product_name = rec.product_id.name
            lot = rec.lot_name
            uom = self.unit_of_measurement
            receipt_date = self.date
            date_time_obj = receipt_date.strftime("%d-%m-%Y")
            if  rec.expiration_date != False:
                exp_date = rec.expiration_date.strftime("%d-%m-%Y")
            else:
                exp_date =  " "
            pack_size = self.pack_size

            try:
                mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                mysocket.connect((ip_address, port))
                print("neleneleklekelekleklekelke;lekle")
                mysocket.send(
                    f'^XA~TA000~JSN^LT0^MNW^MTT^PON^PMN^LH0,0^JMA^PR6,6~SD15^JUS^LRN^CI0^XZ^XA^MMT^PW799^LL0400^LS0^FO74,85^BQN,3,12^FDLA,{str(lot)}^FS^PQ1,0,1,Y^FT70,60^A0N,34,33^FH\^FD{str(product_code)}^FS^FT350,112^A0N,34,33^FH\^FD{str(product_name)}^FS^FT350,165^A0N,34,33^FH\^FDReciept Date:^FS^FT551,165^A0N,34,33^FH\^FD{str(date_time_obj)}^FS^FT350,225^A0N,34,33^FH\^FDExpiry date:^FS^FT534,225^A0N,34,33^FH\^FD{exp_date}^FS^FT350,283^A0N,34,33^FH\^FDPack Size:^FS^FT513,283^A0N,34,33^FH\^FD{float(pack_size)}^FS^FT615,283^A0N,34,33^FH\^FD{str(uom)}^FS^FT70,339^A0N,37,40^FH\^FD{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode(
                        'utf-8'))
                del mysocket
            except:
                print("Error with the connection")

    # def action_show_details(self):
    #     """ Returns an action that will open a form view (in a popup) allowing to work on all the
    #     move lines of a particular move. This form view is used when "show operations" is not
    #     checked on the picking type.
    #     """
    #     self.ensure_one()
    #
    #     if self.picking_type_id.show_reserved:
    #         view = self.env.ref('stock.view_stock_move_operations')
    #     else:
    #         view = self.env.ref('stock.view_stock_move_nosuggest_operations')
    #
    #     if self.product_id.tracking == "serial" and self.state == "assigned":
    #         lot_obj = self.env['stock.production.lot'].sudo().search([('name', 'ilike', str(self.lot_number + '-'))])
    #         self.next_serial = self.env['stock.production.lot']._get_next_serial(self.company_id, self.product_id)
    #         line_obj = self.env['stock.move.line'].sudo().search([('lot_name', 'ilike', str(self.lot_number))])
    #         self.next_serial = self.lot_number + '-' + str(len(line_obj) + 1)
    #         print("NEXT---", len(line_obj))
    #
    #     return {
    #         'name': _('Detailed Operations'),
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'stock.move',
    #         'views': [(view.id, 'form')],
    #         'view_id': view.id,
    #         'target': 'new',
    #         'res_id': self.id,
    #         'context': dict(
    #             self.env.context,
    #             show_owner=self.picking_type_id.code != 'incoming',
    #             show_lots_m2o=self.has_tracking != 'none' and (
    #                         self.picking_type_id.use_existing_lots or self.state == 'done' or self.origin_returned_move_id.id),
    #             # able to create lots, whatever the value of ` use_create_lots`.
    #             show_lots_text=self.has_tracking != 'none' and self.picking_type_id.use_create_lots and not self.picking_type_id.use_existing_lots and self.state != 'done' and not self.origin_returned_move_id.id,
    #             show_source_location=self.picking_type_id.code != 'incoming',
    #             show_destination_location=self.picking_type_id.code != 'outgoing',
    #             show_package=not self.location_id.usage == 'supplier',
    #             show_reserved_quantity=self.state != 'done' and not self.picking_id.immediate_transfer and self.picking_type_id.code != 'incoming'
    #         ),
    #     }

    def action_submit(self):
        pass

    # def assign_lot_no(self):
    #     temp = len(self.move_line_nosuggest_ids)
    #     if self.pack_size:
    #         pack = self.product_uom_qty / self.pack_size
    #         print("^^^^^", pack, int(pack))
    #         move_obj = self.env['stock.move.line'].sudo().search_count(
    #             [('lot_name', 'ilike', str(self.lot_number)), ('move_id', '=', self.id)])
    #         if move_obj == 0:
    #             for re in range(int(pack)):
    #                 move_line_obj = self.env['stock.move.line'].sudo().search_count(
    #                     [('lot_name', 'ilike', self.lot_number)])
    #                 if not move_line_obj:
    #                     test = self.move_line_nosuggest_ids.sudo().create({
    #                         'picking_id': self.picking_id.id,
    #                         'company_id': self.company_id.id,
    #                         'location_id': 4,
    #                         'location_dest_id': 8,
    #                         'lot_name': (self.lot_number + "_" + str(1)),
    #                         'product_id': self.product_id.id,
    #                         'product_uom_id': 1,
    #                         'qty_done': self.product_uom_qty / pack,
    #                     })
    #                 else:
    #                     test = self.move_line_nosuggest_ids.sudo().create({
    #                         'picking_id': self.picking_id.id,
    #                         'company_id': self.company_id.id,
    #                         'location_id': 4,
    #                         'location_dest_id': 8,
    #                         'lot_name': (self.lot_number + "_" + str(move_line_obj + 1)),
    #                         'product_id': self.product_id.id,
    #                         'product_uom_id': 1,
    #                         'qty_done': self.product_uom_qty / pack,
    #                     })
    #
    #         else:
    #             move_line_obj = self.env['stock.move.line'].sudo().search_count(
    #                 [('lot_name', 'ilike', str(self.lot_number))])
    #             qty = self.product_uom_qty - self.quantity_done
    #             if qty != 0:
    #                 test = self.move_line_nosuggest_ids.sudo().create({
    #                     'picking_id': self.picking_id.id,
    #                     'company_id': self.company_id.id,
    #                     'location_id': 4,
    #                     'location_dest_id': 8,
    #                     'lot_name': (self.lot_number + "_" + str(move_line_obj + 1)),
    #                     'product_id': self.product_id.id,
    #                     'product_uom_id': 1,
    #                     'qty_done': qty,
    #                 })
    #     else:
    #         raise UserError("Please Enter a Pack Size.")


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    line_no = fields.Char(string="Line No",compute="get_line_no")


    def get_line_no(self):
        print("::::::::",self.id)
        self.line_no = self.move_id.line_no


class ScanBarcode(models.Model):
    _inherit = "stock.picking.batch"

    def start_scan_picking_batch(self):
        url = "/batch_transfer_scan?batch=" + str(self.name)
        print("<<<<<<<<<<<<<<<<<<<<<<<<", self.name)
        return {'type': 'ir.actions.act_url',
                'target': 'self',
                'url': url, }


