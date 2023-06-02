from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError

class Stock(models.Model):
    _inherit = 'stock.move'

    is_track = fields.Boolean(string="track",default=False)

    @api.model
    def create(self, vals):
        product_product = self.env['product.product'].sudo().search([('id', '=', vals['product_id'])])
        if product_product.tracking == 'none':
            vals['is_track'] = 1
        else:
            vals['is_track'] = 0
        return super(Stock, self).create(vals)

    # def temp(self):
    #     stock_move = self.env['stock.move'].sudo().search([])
    #     print("called------------")
    #     for move in stock_move:
    #         if move.product_id.tracking == 'none':
    #             move.write({'is_track':True})

    # @api.onchange('qty_done')
    # def button_invisible(self):
    #     print("bbhubhubhubhubhu",self.product_uom_qty,self.quantity_done)
    #     if self.product_uom_qty == self.quantity_done:
    #         print("\n\n\n\n\n\n00000000babababababababababab0000000000000",self.is_track)
    #         self.is_track = True
    #         print("3333333333333333333333333", self.is_track)
    #     else:
    #         print("___________________________")
    #         self.is_track = False


    def start_scan(self):
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        if self.product_uom_qty == self.quantity_done:
            print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",self.product_uom_qty,self.quantity_done)
            raise UserError(_('Scanning is completed'))

        else:
            url = "/assign_serial_invert?product=" + str(self.product_id.id) + "&picking_id=" + str(self.picking_id.id) + "&move_id=" + str(self.id)
            print("LLLLLLLLLLLLLLLLLLLL", url,self, self.picking_id.id, self.picking_id, self.id)
            return {
                'type': 'ir.actions.act_url',
                'target': 'self',
                'url': url,
                'tag': 'reload',
            }

    # def start_scan(self):
    #     # @api.onchange('move_line_no_suggest_ids')
    #     # def set_package(self):
    #             print(self.picking_id.picking_type_id.id)
    #             print("HHHHHHHHHHHHHH",self.origin,self.picking_id)
    #             sale_ref = self.env['sale.order'].sudo().search([('client_order_ref', '=',self.origin)])
    #             print("*********************",sale_ref)
    #             del_ref = self.env['stock.picking'].sudo().search([('origin', '=',sale_ref.name)])
    #             print("JJJJJJJJJJJJJJJJJJJJJ",del_ref)
    #             if self.picking_id.picking_type_id.id == 10 and del_ref.state =="done":
    #                 for rec in del_ref.package_level_ids_details:
    #                     print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&",rec.package_id.name)
    #                     pack_re = self.env['stock.package_level'].sudo().search([('package_id','=',rec.package_id.id)])
    #                     print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO",pack_re.package_id.name)
    #                     for re in pack_re.move_line_ids:
    #                         print("QQQQQQQQQQQQQQQTTTTTTTTTTTTTTYYYYYYYYYY",re.qty_done)
    #                     pack = self.env['stock.quant.package'].search([('name','=',pack_re.package_id.name)])
    #                     # pack.write({'company_id':self.env.company.id,'location_id':24})
    #                     self.move_line_nosuggest_ids.sudo().create({
    #                                                        'move_id': self.id,
    #                                                        'location_dest_id':25,
    #                                                        'result_package_id':rec.package_id.id,
    #                                                        'product_uom_id':1,
    #                                                        'product_id':self.product_id.id,
    #                                                        'qty_done':re.qty_done,
    #                                                        'company_id':self.env.company.id,
    #                                                        # 'location_dest_id':25,
    #                                                 })

                # self.picking_id.button_validate()

class ScanBarcode(models.Model):
    _inherit = "stock.picking"

    tmp_name = fields.Char('Reference', readonly=True)
    fifo_list = fields.Text('FIFO_list',readonly=True)

    def start_scan_picking(self):
        user_picking = self.env['user.picking'].sudo().search([('user_id', '=', self.env.uid)])
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",str(self._context.get('name')),self)
        if self._context.get('direct'):
            url = "/scan_manual_transfer?source=" + str(self._context.get('name'))
            if user_picking:
                user_picking.write({'picking_name': str(self._context.get('name'))})
            else:
                user_picking.create({'user_id': self.env.uid, 'picking_name': self.name})
            return {'type': 'ir.actions.act_url',
                    'target': 'self',
                    'url': url,}
        else:
            print("666666666666666666666666666")
            url = "/scan_manual_transfer?source=" + str(self.name)
            if user_picking:
                user_picking.write({'picking_name': self.name})
            else:
                user_picking.create({'user_id': self.env.uid, 'picking_name': self.name})
            return {'type': 'ir.actions.act_url',
                    'target': 'self',
                    'url': url, }

    def start_scan(self):
        print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        # if self.product_uom_qty == self.quantity_done:
        #     print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$", self.product_uom_qty,
        #           self.quantity_done)
        #     raise UserError(_('Scanning is completed'))

        # else:
        url = "/assign_serial_invert?picking_id=" + str(self.id)
        print("LLLLLLLLLLLLLLLLLLLL", url, self, self.id)
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': url,
            'tag': 'reload',
        }
