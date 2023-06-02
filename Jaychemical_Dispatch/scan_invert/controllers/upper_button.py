from odoo.exceptions import UserError, ValidationError
from odoo import http, tools, _
from odoo.http import request
from datetime import datetime, timedelta
import collections


class Inventory(http.Controller):

    def count_done(self):
        tmp_dq = 0
        tmp_rq = 0

        stock_pick_obj = request.env['stock.picking'].sudo().search([('id', '=', request.session['picking_id'])])
        for obj2 in stock_pick_obj:
            for move_ids in obj2.move_ids_without_package:
                tmp_rq += move_ids.product_uom_qty
                tmp_dq += move_ids.quantity_done
        return tmp_rq,tmp_dq

    @http.route('/assign_serial_invert', website=True, methods=['GET'], auth="public", csrf=False)
    def assign_serailnum(self, **kw):
        request.session['picking_id'] = kw['picking_id']
        stock_pick_obj = request.env['stock.picking'].sudo().search([('id', '=', request.session['picking_id'])])

        ser_list = []

        request.session['ser_list'] = ser_list

        self.assigned_list = ""
        # stock_move = request.env['stock.move'].sudo().search([('id', '=', request.session['move_id'])])
        # stock_move_line = request.env['stock.move.line'].sudo().search(
        #     [('move_id.id', '=', request.session['move_id'])])
        #
        # if len(stock_move_line) > stock_move.product_uom_qty:
        #     for i in stock_move_line:
        #         print("------------------", i.lot_name)
        #         if i.lot_name != False:
        #             self.assigned_list += "{}  |  ".format(i.lot_name)
        #     not_assigned = ""
        # else:
        #     not_assigned = "No serial/lot assigned."
        # --------------------------------------------------
        table = {}
        request.session['table'] = table


        for move_ids in stock_pick_obj.move_ids_without_package:
            if move_ids.product_id.name in table:
                request.session['table'][move_ids.lot_number][0] += move_ids.product_uom_qty
            else:
                request.session['table'][move_ids.lot_number] = [move_ids.product_uom_qty,
                                                   move_ids.product_uom_qty - move_ids.quantity_done]

        #request.session['table'][move_line.product_id.name] = [move_line.product_uom_qty,(move_line.product_uom_qty - move_line.quantity_done)]


        # if request.session['track'] == "lot":
        #     # print("JJJJJJJJJJJJJJJJJJ",not_assigned)
        #     return http.request.render('scan_invert.inventory_in_page',
        #                                {'pro': request.session['product_id'], 'track_pro': False,
        #                                 'table': request.session['table'], 'not_assigned': not_assigned,
        #                                 'assigned_list': self.assigned_list.strip("  |  ")})
        # else:
            # print("JJJJJJJJJJJJJJJJJJ",not_assigned)
        return http.request.render('scan_invert.inventory_in_page',
                                   {'pro': request.session['product_id'], 'track_pro': True,
                                    'table': request.session['table'], 'not_assigned': not_assigned,
                                    'assigned_list': self.assigned_list.strip("  |  ")})

    # except:
    #     picking_obj = request.env['stock.move'].sudo().search([('product_id.id', '=', self.pro_id)])
    #     comp = request.env.user.company_id.id
    #     picking_obj1 = request.env['stock.picking'].sudo().search([('id', '=', self.pick_id),('company_id', '=', comp)])
    #     # print("77777777777777777777777777777777777777777", comp)
    #     if comp == 1:
    #         print("company 11111111111111111111111111111111111111111")
    #         import werkzeug.utils
    #         action_id = request.env.ref('stock.action_picking_tree_ready')
    #         return werkzeug.utils.redirect(
    #             '/web#id={}&cids=1&menu_id=211&action={}&active_id=1&model=stock.picking&view_type=form'.format(
    #                 picking_obj1.id,
    #                 action_id.id))
    #     else:
    #         print("company 2222222222222222222222222222222222222222")
    #         import werkzeug.utils
    #         action_id = request.env.ref('stock.action_picking_tree_ready')
    #         return werkzeug.utils.redirect(
    #             '/web#id={}&menu_id=245&action={}&active_id=12&model=stock.picking&view_type=form'.format(
    #                 picking_obj1.id,
    #                 action_id.id))

    @http.route('/assign_serial_invert', website=True, auth="public", csrf=False, type='http')
    def assign_serailnum_check(self, **kw):
        if kw:
            request.session['serial'] = kw['serial']

            stock_pick_obj = request.env['stock.picking'].sudo().search([('id', '=', request.session['picking_id'])])



            for ser in stock_pick_obj.move_line_ids:
                request.session['ser_list'].append(ser.lot_name)


            for rec in stock_pick_obj.move_ids_without_package:

                ser_lot = request.env['stock.lot'].sudo().search([('name', '=', request.session['serial'])])

                print(">>>>>>>>######################$$$$$$$$$$$$$$$$$$>>>>>>>>>>>>>>>",)

                if ser_lot or request.session['serial'] in request.session['ser_list']:
                    error = "this serial number already assigned"
                    return http.request.render('scan_invert.inventory_in_page',
                                               {'track_pro': True, 'error': error, 'table': request.session['table'],
                                                'assigned_list': self.assigned_list.strip("  |  ")})
                else:
                    if request.session['serial'] not in request.session['ser_list'] and rec.product_uom_qty != rec.quantity_done:

                        if str(request.session['serial'].split("_")[0]) == str(rec.lot_number):
                            print("11111111111111111111111111111111")
                            rec.move_line_ids.sudo().create({
                                'picking_id': stock_pick_obj.id,
                                # 'move_id': rec.id,
                                'company_id': request.env.user.company_id.id,
                                'location_id': 4,
                                'location_dest_id': 8,
                                'lot_name': kw['serial'],
                                'product_id': rec.product_id.id,
                                'product_uom_id': 1,
                                'qty_done': 1,
                            })
                            tmp_rq, tmp_dq = self.count_done()
                            if tmp_dq == tmp_rq:
                                return http.request.render('scan_invert.thank_you_page', {'track_pro': True})

                            if len(rec.move_line_ids) > rec.product_uom_qty:
                                for i in rec.move_line_ids:
                                    if i.lot_name != False:
                                        self.assigned_list += "{}  |  ".format(i.lot_name)
                                not_assigned = ""
                            else:
                                self.assigned_list += "{}  |  ".format(request.session['serial'])
                                not_assigned = "No serial/lot assigned."

                            for move_ids in stock_pick_obj.move_ids_without_package:
                                if move_ids.product_id.name in request.session['table']:
                                    request.session['table'][move_ids.lot_number][0] += move_ids.product_uom_qty
                                else:
                                    request.session['table'][move_ids.lot_number] = [move_ids.product_uom_qty,
                                                                                     move_ids.product_uom_qty - move_ids.quantity_done]

                            # if rec.product_uom_qty <= rec.quantity_done:
                            #     return http.request.render('scan_invert.thank_you_page', {'track_pro': True})
                            #
                            print("22222222222222222222222222222222222222222")
                            return http.request.render('scan_invert.inventory_in_page',
                                                           {'pro': request.session['product_id'], 'track_pro': True,
                                                            'table': request.session['table'],
                                                             'assigned_list': self.assigned_list.strip("  |  ")})
                        else:
                            return http.request.render('scan_invert.inventory_in_page',
                                                       {'pro': request.session['product_id'], 'track_pro': True,
                                                        'table': request.session['table'],
                                                        'assigned_list': self.assigned_list.strip("  |  "),'error':"Lot Number not match"})










