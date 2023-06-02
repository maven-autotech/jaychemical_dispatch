from odoo.exceptions import UserError, ValidationError
from odoo import http, tools, _
from odoo.http import request
from datetime import datetime, timedelta
import collections


class Inventory(http.Controller):

    @http.route('/assign_serial_invert', website=True, methods=['GET'], auth="public", csrf=False)
    def assign_serailnum(self, **kw):
            print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", kw)
            request.session['move_id']=kw['move_id']
            request.session['product_id']=kw['product']
            request.session['picking_id']=kw['picking_id']
            move_obj = request.env['stock.move'].sudo().search([('id','=',request.session['move_id'])])


            pro_track = request.env['product.template'].sudo().search([('id', '=',request.session['product_id'])])
            # print("LLLLLLLLLLLLLLLLLLLL", pro_track)


            picking_obj = request.env['stock.move'].sudo().search([('product_id.id', '=',request.session['product_id'])])

            picking_obj1 = request.env['stock.picking'].sudo().search([('id', '=',request.session['picking_id'])])
           
            track = pro_track.tracking

            request.session['track'] = track
            # print("GGGSSSSSSADERDWEFDWEFSDFS",self.track)


            # print("TTTTTTTTTTTTTTTT", track_pro,self.track)
            #----------Jaineel Code for serials list-----------
            self.assigned_list = ""
            stock_move = request.env['stock.move'].sudo().search([('id','=',request.session['move_id'])])
            stock_move_line = request.env['stock.move.line'].sudo().search([('move_id.id','=',request.session['move_id'])])
            if len(stock_move_line)>stock_move.product_uom_qty:
                for i in stock_move_line:
                    print("------------------",i.lot_name)
                    if i.lot_name != False:
                        self.assigned_list += "{}  |  ".format(i.lot_name)
                not_assigned = ""
            else:
                not_assigned = "No serial/lot assigned."
            #--------------------------------------------------
            table = {}
            request.session['table'] = table
            for move_line in picking_obj1.move_ids_without_package:
                # print("**************************************", move_line.product_id.name)
                if move_line.product_id.name == picking_obj.product_id.name:
                    request.session['table'][move_line.product_id.name] = [move_line.product_uom_qty,
                                                           move_line.product_uom_qty - move_line.quantity_done]
                    # print("***************jjj*****************", self.table)

            if request.session['track'] == "lot":
                # print("JJJJJJJJJJJJJJJJJJ",not_assigned)
                return http.request.render('scan_invert.inventory_in_page',
                                           {'pro': request.session['product_id'], 'track_pro': False,'table':request.session['table'], 'not_assigned':not_assigned, 'assigned_list':self.assigned_list.strip("  |  ")})
            else:
                # print("JJJJJJJJJJJJJJJJJJ",not_assigned)
                return http.request.render('scan_invert.inventory_in_page',
                                           {'pro': request.session['product_id'], 'track_pro': True,'table':request.session['table'], 'not_assigned':not_assigned, 'assigned_list':self.assigned_list.strip("  |  ")})
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

            #user_picking = request.env['user.picking'].sudo().search([('user_id', '=', request.env.uid)])
            # self.pro_id = kw['product']

            # print("KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK", self.pro_id, id, self.pick_id)
            pro_track = request.env['product.product'].sudo().search([('id', '=', request.session['product_id'])])
            print("LLLLLLLLLLLLLLLLLLLL", pro_track)
            comp = request.env.user.company_id.id
          #
            self.track = pro_track.product_tmpl_id.tracking
            print("77777777777777777777777777777777777777777777777777777777777777", self.track,self.assigned_list)



            if self.track == "lot":
                comp = request.env.user.company_id.id
                ser_list =[]
                picking_obj1 = request.env['stock.picking'].sudo().search(
                    [('id', '=', self.pick_id), ('company_id', '=', comp)])
                picking_obj = request.env['stock.move'].sudo().search([('product_id.id','=',self.pro_id)])
                stock_pro_lot = request.env['stock.production.lot'].sudo().search([('product_id.id','=',self.pro_id)])
                for re in picking_obj1:
                    print("PPPPPPPP",re)
                for ser in picking_obj.move_line_ids:
                    ser_list.append(ser.lot_name)
                for rec in picking_obj:
                    if rec.picking_id == picking_obj1:
                        if rec.quantity_done != rec.product_uom_qty:
                            print("******************************************")
                            remain_qty = float(rec.product_uom_qty) - float(rec.quantity_done)
                            self.re = abs(remain_qty)
                            if rec.product_uom_qty > rec.quantity_done:
                                if float(kw['qty']) <= rec.product_uom_qty:
                                    if rec.product_uom_qty >= float(kw['qty']) <= (
                                            rec.product_uom_qty - rec.quantity_done):
                                        if float(kw['qty']) + rec.quantity_done <= rec.product_uom_qty:
                                            comp = request.env.user.company_id.id
                                            if comp == 1:
                                                if stock_pro_lot or kw['lot'] in ser_list:
                                                    print("777777777777777777777777777777777777777")
                                                    error = "this serial number already assigned"
                                                    return http.request.render('scan_invert.inventory_in_page',
                                                                               {'track_pro': False, 'error': error,'table':self.table, 'assigned_list':self.assigned_list.strip("  |  ")})
                                                else:
                                                    print("88888888888888888888888888888888888")
                                                    move_obj_line = request.env['stock.move.line'].sudo().create({
                                                        'picking_id': re.id,
                                                        'company_id': request.env.user.company_id,
                                                        'location_id': 4,
                                                        'location_dest_id': 9,
                                                        'lot_name': kw['lot'],
                                                        'product_id': self.pro_id,
                                                        'product_uom_id': 1,
                                                        'qty_done': float(kw['qty']),
                                                    })
                                                    remain_qty = float(rec.product_uom_qty) - float(rec.quantity_done)
                                                    #----------Jaineel Code for serials list-----------
                                                    self.assigned_list = ""
                                                    stock_move = request.env['stock.move'].sudo().search([('id','=',self.stock_move_id)])
                                                    stock_move_line = request.env['stock.move.line'].sudo().search([('move_id','=',self.stock_move_id)])
                                                    if len(stock_move_line)>stock_move.product_uom_qty:
                                                        for i in stock_move_line:
                                                            if i.lot_name != False:
                                                                self.assigned_list += "{}  |  ".format(i.lot_name)
                                                        not_assigned = ""
                                                    else:
                                                        not_assigned = "No serial/lot assigned."
                                                    #--------------------------------------------------
                                                    self.table = {}
                                                    for move_line in picking_obj1.move_ids_without_package:
                                                        print("**************************************",
                                                              move_line.product_id.name)
                                                        if move_line.product_id.name == picking_obj.product_id.name:
                                                            self.table[move_line.product_id.name] = [
                                                                move_line.product_uom_qty,
                                                                move_line.product_uom_qty - move_line.quantity_done]
                                                            print("********************************", self.table)

                                                    if remain_qty == 0.0:
                                                            import werkzeug.utils
                                                            action_id = request.env.ref('stock.action_picking_tree_ready')
                                                            return werkzeug.utils.redirect(
                                                                '/web#id={}&cids=1&menu_id=211&action={}&active_id=1&model=stock.picking&view_type=form'.format(
                                                                    picking_obj1.id,
                                                                    action_id.id))
                                                    return http.request.render('scan_invert.inventory_in_page',
                                                                               {'track_pro': False,'table':self.table, 'assigned_list':self.assigned_list.strip("  |  ")})
                                            else:
                                                if stock_pro_lot or kw['lot'] in ser_list:
                                                    error = "this serial number already assigned"
                                                    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%",self.table)
                                                    return http.request.render('scan_invert.inventory_in_page',
                                                                               {'track_pro': False, 'error': error,'table':self.table, 'assigned_list':self.assigned_list.strip("  |  ")})
                                                else:
                                                    move_obj_line = request.env['stock.move.line'].sudo().create({
                                                        'picking_id': re.id,
                                                        'company_id': request.env.user.company_id,
                                                        'location_id': 4,
                                                        'location_dest_id': 26,
                                                        'lot_name': kw['lot'],
                                                        'product_id': self.pro_id,
                                                        'product_uom_id': 1,
                                                        'qty_done': float(kw['qty']),
                                                    })
                                                    remain_qty = float(rec.product_uom_qty) - float(rec.quantity_done)
                                                    #----------Jaineel Code for serials list-----------
                                                    self.assigned_list = ""
                                                    stock_move = request.env['stock.move'].sudo().search([('id','=',self.stock_move_id)])
                                                    stock_move_line = request.env['stock.move.line'].sudo().search([('move_id','=',self.stock_move_id)])
                                                    if len(stock_move_line)>stock_move.product_uom_qty:
                                                        for i in stock_move_line:
                                                            if i.lot_name != False:
                                                                self.assigned_list += "{}  |  ".format(i.lot_name)
                                                        not_assigned = ""
                                                    else:
                                                        not_assigned = "No serial/lot assigned."
                                                    #--------------------------------------------------
                                                    self.table = {}
                                                    for move_line in picking_obj1.move_ids_without_package:
                                                        print("productproduct5555555555555555555",
                                                              move_line.product_id.name)
                                                        if move_line.product_id.name == picking_obj.product_id.name:
                                                            self.table[move_line.product_id.name] = [
                                                                move_line.product_uom_qty,
                                                                move_line.product_uom_qty - move_line.quantity_done]
                                                            print("********************************", self.table)

                                                    if remain_qty == 0.0:
                                                        print("company 2222222222222222222222222222222222222222")
                                                        import werkzeug.utils
                                                        action_id = request.env.ref('stock.action_picking_tree_ready')
                                                        return werkzeug.utils.redirect(
                                                            '/web#id={}&menu_id=245&action={}&active_id=12&model=stock.picking&view_type=form'.format(
                                                                picking_obj1.id,
                                                                action_id.id))

                                                return http.request.render('scan_invert.inventory_in_page',
                                                                           {'track_pro': False,'table':self.table, 'assigned_list':self.assigned_list.strip("  |  ")})
                                        else:
                                            error = "the qunatity must be {} or  less than {}".format(self.re,
                                                                                                      self.re)
                                            return http.request.render('scan_invert.inventory_in_page',
                                                                       {'track_pro': False, 'error': error,'table':self.table, 'assigned_list':self.assigned_list.strip("  |  ")})
                                    else:
                                        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                                        error = "the qunatity must be {} or  less than {}".format(self.re,
                                                                                                  self.re)
                                        return http.request.render('scan_invert.inventory_in_page',
                                                                   {'track_pro': False, 'error': error, 'assigned_list':self.assigned_list.strip("  |  ")})
                                elif float(kw['qty']) == rec.product_uom_qty:
                                            print("iiiiiiiiiiiiiiiiiiiiiiiifffffffffffffff",float(kw['qty']),rec.product_uom_qty)
                                            comp = request.env.user.company_id.id
                                            print("77777777777777777777777777777777777777777", comp)
                                            if comp == 1:
                                                move_obj_line = request.env['stock.move.line'].sudo().create({
                                                    'picking_id': re.id,
                                                    'company_id': request.env.user.company_id,
                                                    # 'move_id': rec.id,
                                                    'location_id': 4,
                                                    'location_dest_id': 9,
                                                    'lot_name': kw['lot'],
                                                    'product_id': self.pro_id,
                                                    'product_uom_id': 1,
                                                    'qty_done': float(kw['qty']),
                                                })
                                                #----------Jaineel Code for serials list-----------
                                                self.assigned_list = ""
                                                stock_move = request.env['stock.move'].sudo().search([('id','=',self.stock_move_id)])
                                                stock_move_line = request.env['stock.move.line'].sudo().search([('move_id','=',self.stock_move_id)])
                                                if len(stock_move_line)>stock_move.product_uom_qty:
                                                    for i in stock_move_line:
                                                        if i.lot_name != False:
                                                            self.assigned_list += "{}  |  ".format(i.lot_name)
                                                    not_assigned = ""
                                                else:
                                                    not_assigned = "No serial/lot assigned."
                                                #--------------------------------------------------
                                                self.table = {}
                                                for move_line in picking_obj1.move_ids_without_package:
                                                    print("**************************************",
                                                          move_line.product_id.name)
                                                    if move_line.product_id.name == picking_obj.product_id.name:
                                                        self.table[move_line.product_id.name] = [
                                                            move_line.product_uom_qty,
                                                            move_line.product_uom_qty - move_line.quantity_done]
                                                        print("********************************", self.table)

                                            else:
                                                move_obj_line = request.env['stock.move.line'].sudo().create({
                                                    'picking_id': re.id,
                                                    'company_id': request.env.user.company_id,
                                                    # 'move_id': rec.id,
                                                    'location_id': 4,
                                                    'location_dest_id': 26,
                                                    'lot_name': kw['lot'],
                                                    'product_id': self.pro_id,
                                                    'product_uom_id': 1,
                                                    'qty_done': float(kw['qty']),
                                                })
                                                #----------Jaineel Code for serials list-----------
                                                self.assigned_list = ""
                                                not_assigned = ""
                                                stock_move = request.env['stock.move'].sudo().search([('id','=',self.stock_move_id)])
                                                stock_move_line = request.env['stock.move.line'].sudo().search([('move_id','=',self.stock_move_id)])
                                                if len(stock_move_line)>stock_move.product_uom_qty:
                                                    for i in stock_move_line:
                                                        if i.lot_name != False:
                                                            self.assigned_list += "{}  |  ".format(i.lot_name)
                                                            print("{}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}",self.assigned_list)
                                                else:
                                                    not_assigned = "No serial/lot assigned."
                                                #--------------------------------------------------
                                                self.table = {}
                                                for move_line in picking_obj1.move_ids_without_package:
                                                    print("**************************************",
                                                          move_line.product_id.name)
                                                    if move_line.product_id.name == picking_obj.product_id.name:
                                                        self.table[move_line.product_id.name] = [
                                                            move_line.product_uom_qty,
                                                            move_line.product_uom_qty - move_line.quantity_done]
                                                        print("********************************", self.table)


                                else:
                                    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                                    error = "the qunatity must be {}".format(rec.product_uom_qty)
                                    return http.request.render('scan_invert.inventory_in_page',
                                                               {'track_pro': False, 'error': error,'table':self.table, 'assigned_list':self.assigned_list.strip("  |  ")})
                        #     else:
                        #         print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                        #         error = "the qunatity must be {} or  less than {}".format(self.re,self.re)
                        #         return http.request.render('scan_invert.inventory_in_page',
                        #                                    {'track_pro': False,'error':error})
                        # else:
                        #     print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                        #     error = "the qunatity must be {} or  less than {}".format(self.re, self.re)
                        #     return http.request.render('scan_invert.inventory_in_page',
                        #                                {'track_pro': False, 'error': error})


            else:
                comp = request.env.user.company_id.id
                ser_list = []

                request.session['serial'] = kw['serial']
                picking_obj1 = request.env['stock.picking'].sudo().search(
                    [('id', '=',request.session['picking_id'] ), ('company_id', '=', comp)])
                print("$$$$$$$$$$$$$$$$$$$$$$$",picking_obj1)
                for re in picking_obj1:
                    print("PPPPPPPP")
                print(":::::::::::::::::::::::::::::::::::",kw['serial'],picking_obj1.picking_type_id)
                picking_obj = request.env['stock.move'].sudo().search([('product_id.id','=',request.session['product_id'])])
                for ser in picking_obj.move_line_ids:
                    ser_list.append(ser.lot_name)
                    print("__________________________________________________________",ser_list)
                for rec in picking_obj:
                    print("((((((((((((((((((((((((((((((((((((((((((((",rec.picking_id,picking_obj1)
                    if rec.picking_id == picking_obj1:
                        print("0000000000000000000000000000000000000000000000000")
                        if rec.state == "assigned":
                            print(":::::::::::::::::::::::::::",rec.product_id,rec.product_id.id,request.session['product_id'])
                            if rec.product_id.id == int(request.session['product_id']):
                               ser_lot = request.env['stock.lot'].sudo().search([('name', '=',request.session['serial'])])

                               print(">>>>>>>>######################$$$$$$$$$$$$$$$$$$>>>>>>>>>>>>>>>",request.session['serial'].split("-")[0],rec.lot_number)
                               if ser_lot or request.session['serial'] in ser_list:
                                   error = "this serial number already assigned"
                                   return http.request.render('scan_invert.inventory_in_page', {'track_pro': True,'error': error,'table':request.session['table'], 'assigned_list':self.assigned_list.strip("  |  ")})
                               else:
                                   comp = request.env.user.company_id.id
                                   if str(rec.lot_number).split("-")[0] == str(request.session['serial'].split("-")[0]):
                                       print("PPPPPPPPPPPPPPPPPPPPPP", ser_list)
                                       if request.session['serial'] in ser_list or ser_lot:
                                           error = "this serial number already assigned"
                                           return http.request.render('scan_invert.inventory_in_page',
                                                                      {'track_pro': True, 'error': error,'table':request.session['table'], 'assigned_list':self.assigned_list.strip("  |  ")})
                                       else:
                                            rec.move_line_ids.sudo().create({
                                                'picking_id': re.id,
                                                # 'move_id': rec.id,
                                                'company_id': request.env.user.company_id.id,
                                                'location_id': 4,
                                                'location_dest_id': 8,
                                                'lot_name': kw['serial'],
                                                'product_id': pro_track.id,
                                                'product_uom_id': 1,
                                                'qty_done': 1,
                                            })

                                            for move_line in picking_obj1.move_ids_without_package:
                                                # print("**************************************", move_line.product_id.name)
                                                if move_line.product_id.name == picking_obj.product_id.name:
                                                    request.session['table'][move_line.product_id.name] = [
                                                        move_line.product_uom_qty,
                                                        move_line.product_uom_qty - move_line.quantity_done]

                                            stock_move = request.env['stock.move'].sudo().search(
                                                [('id', '=',request.session['move_id'])])
                                            stock_move_line = request.env['stock.move.line'].sudo().search(
                                                [('move_id', '=',request.session['move_id'])])
                                            print("janvi javi jajnvi ?????????",len(stock_move_line),stock_move.product_uom_qty)
                                            if len(stock_move_line) > stock_move.product_uom_qty:
                                                for i in stock_move_line:
                                                    if i.lot_name != False:
                                                        self.assigned_list += "{}  |  ".format(i.lot_name)
                                                not_assigned = ""
                                            else:
                                                self.assigned_list += "{}  |  ".format(request.session['serial'])
                                                not_assigned = "No serial/lot assigned."

                                            if rec.product_uom_qty == rec.quantity_done:
                                                comp = request.env.user.company_id.id
                                                import werkzeug.utils
                                                action_id = request.env.ref('stock.action_picking_tree_ready')
                                                return werkzeug.utils.redirect(
                                                    '/web#id={}&cids=1&menu_id=211&action={}&active_id=1&model=stock.picking&view_type=form'.format(
                                                        picking_obj1.id,
                                                        action_id.id))
                                            # return http.request.render('scan_invert.inventory_in_page',
                                            #                            {'track_pro': True,
                                            #                             'table': request.session['table'],
                                            #                             'assigned_list': self.assigned_list.strip(
                                            #                                 "  |  ")})


                                   else:
                                       error = "Lot number not match"
                                       return http.request.render('scan_invert.inventory_in_page',
                                                                  {'track_pro': True, 'error': error,
                                                                   'table': request.session['table'],
                                                                   'assigned_list': self.assigned_list.strip("  |  ")})


                                #return http.request.render('scan_invret.thank_you_page', {'track_pro': True})

                               return http.request.render('scan_invert.inventory_in_page',{'track_pro': True,'table':request.session['table'], 'assigned_list':self.assigned_list.strip("  |  ")})



##########################################  For GRN and ISSUE Process  ###########################################################################


# class ManualTransfer(http.Controller):
#
#     @http.route('/scan_manual_transfer', website=True, methods=['GET'], auth="public", csrf=False)
#     def ManualTransfer1(self, **kw):
#         done_qty = 0
#         reserve_qty = 0
#         # try:
#         self.trf_name = kw['source']
#         # except:
#         #     import werkzeug.utils
#         #     action_id = request.env.ref('stock.stock_picking_type_action')
#         #     return werkzeug.utils.redirect('/web#action={}'.format(action_id.id))
#         # trf_obj = request.env['stock.picking'].sudo().search([('name', '=', self.trf_name)])
#         user_picking = request.env['user.picking'].sudo().search([('user_id', '=', request.env.uid)])
#         trf_obj = request.env['stock.picking'].sudo().search([('name', '=', user_picking.picking_name)])
#         self.picking_type = trf_obj.picking_type_id.name
#         print("##########################################################3",trf_obj.picking_type_id.name)
#         if self.picking_type == 'Delivery':
#             self.lot_serial_list_issue = []
#             # ------- FOR Done Qty & Reserv Qty (Start) ------------
#             for obj in trf_obj:
#                 for move_line in obj.move_line_ids_without_package:
#                     done_qty += move_line.qty_done
#                     self.lot_serial_list_issue.append(move_line.lot_id.name)
#             for res_obj in trf_obj:
#                 for moves in res_obj.move_ids_without_package:
#                     reserve_qty += moves.product_uom_qty
#             # ------- FOR Done Qty & Reserv Qty (End) --------------
#
#             # ------------- FOR FIFO List --------------------------
#             if done_qty == 0:
#                 trf_obj.write({'fifo_list': str(self.lot_serial_list_issue)})
#             # ------------------------------------------------------
#
#             # ----------------------------- FOR Table (Start) ----------------------------------------------------------------------------------
#             table = {}
#             remove_list = []
#             pick_location = {}
#             for obj in trf_obj:
#                 for move_line in obj.move_line_ids_without_package:
#                     print("**************************************", move_line.product_id.name)
#                     if move_line.product_id.name in table:
#                         if move_line.qty_done != move_line.product_uom_qty:
#                             table[move_line.product_id.name][1] += move_line.qty_done
#             for obj2 in trf_obj:
#                 for move_ids in obj2.move_ids_without_package:
#                     if move_ids.product_id.name in table:
#                         table[move_ids.product_id.name][0] += move_ids.product_uom_qty
#                     else:
#                         table[move_ids.product_id.name] = [move_ids.product_uom_qty,
#                                                                    move_ids.product_uom_qty - move_ids.quantity_done]
#             for obj3 in trf_obj:
#                 for move_line2 in obj3.move_line_ids_without_package:
#                     if move_line2.product_id.name in pick_location:
#                         pass
#                     else:
#                         pick_location[move_line2.product_id.name] = move_line2.location_id.complete_name
#             for prd, loc in pick_location.items():
#                 if prd in table:
#                     table[prd].append(loc)
#             for product, qty in table.items():
#                 if qty[1] == 0:
#                     remove_list.append(product)
#             for pro_qty in remove_list:
#                 del table[pro_qty]
#             for product in table:
#                     if len(table[product]) == 2:
#                         table[product].append("Not Available")
#             # ----------------------------- FOR Table (End) ------------------------------------------------------------------------------------
#             print(")))))))))))))))))))))))))))))))))))))))",table)
#             return http.request.render('scan_invert.manual_location_page', {'qty_reqired': reserve_qty,
#                                                                         'qty_done': done_qty,
#                                                                         'table1': table})
#         else:
#             # ------- FOR Done Qty & Reserv Qty (Start) ------------
#             for obj in trf_obj:
#                 for move_line in obj.move_line_ids_without_package:
#                     done_qty += move_line.qty_done
#             for res_obj in trf_obj:
#                 for moves in res_obj.move_ids_without_package:
#                     reserve_qty += moves.product_uom_qty
#             # ------- FOR Done Qty & Reserv Qty (End) --------------
#
#             # ----------------------------- FOR Table (Start) ----------------------------------------------------------------------------------
#             table = {}
#             remove_list = []
#             for obj in trf_obj:
#                 for move_line in obj.move_line_ids_without_package:
#                     print("**************************************", move_line.product_id.name)
#                     if move_line.product_id.name in table:
#                         if move_line.qty_done != move_line.product_uom_qty:
#                             table[move_line.product_id.name][1] += move_line.qty_done
#             for obj2 in trf_obj:
#                 for move_ids in obj2.move_ids_without_package:
#                     if move_ids.product_id.name in table:
#                         table[move_ids.product_id.name][0] += move_ids.product_uom_qty
#                     else:
#                         table[move_ids.product_id.name] = [move_ids.product_uom_qty,
#                                                                    move_ids.product_uom_qty - move_ids.quantity_done]
#             for product, qty in table.items():
#                 if qty[1] == 0:
#                     remove_list.append(product)
#             for pro_qty in remove_list:
#                 del table[pro_qty]
#             # ---------------------------- FOR Table (End) -------------------------------------------------------------------------------------
#             print("8888999999999999999999999999999999999999999999", table)
#             return http.request.render('scan_invert.manual_transfer_page', {'qty_reqired': reserve_qty,
#                                                                         'qty_done': done_qty,
#                                                                         'table2': table})
#
#     # @http.route('/scan_manual_transfer', website=True, auth="public", csrf=False, type='http')
#     # def ManualTransfer2(self, **kw):
#     #     # try:
#     #         done_qty = 0
#     #         reserve_qty = 0
#     #         # trf_obj = request.env['stock.picking'].sudo().search([('name', '=', self.trf_name)])
#     #
#     #         user_picking = request.env['user.picking'].sudo().search([('user_id', '=', request.env.uid)])
#     #         trf_obj = request.env['stock.picking'].sudo().search([('name', '=', user_picking.picking_name)])
#     #         lot_serial_list_grn = []
#     #         # self.serial = kw['serial']
#     #         user_picking.write({'lot_serial':kw['serial']})
#     #
#     #         print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%",self.picking_type)
#     #         ################################################## For Delivery Orders (Start) ###########################################################
#     #         if self.picking_type == 'Delivery Orders':
#     #             # ------- FOR Done Qty & Reserv Qty (Start) ------------
#     #             for obj in trf_obj:
#     #                 for move_line in obj.move_line_ids_without_package:
#     #                     done_qty += move_line.qty_done
#     #             for res_obj in trf_obj:
#     #                 for moves in res_obj.move_ids_without_package:
#     #                     reserve_qty += moves.product_uom_qty
#     #             # ------- FOR Done Qty & Reserv Qty (End) --------------
#     #
#     #             # ----------------------------- FOR Table (Start) ----------------------------------------------------------------------------------
#     #             table = {}
#     #             remove_list = []
#     #             pick_location = {}
#     #             for obj in trf_obj:
#     #                 for move_line in obj.move_line_ids_without_package:
#     #                     if move_line.product_id.name in table:
#     #                         if move_line.qty_done != move_line.product_uom_qty:
#     #                             table[move_line.product_id.name][1] += move_line.qty_done
#     #             for obj2 in trf_obj:
#     #                 for move_ids in obj2.move_ids_without_package:
#     #                     if move_ids.product_id.name in table:
#     #                         table[move_ids.product_id.name][0] += move_ids.product_uom_qty
#     #                     else:
#     #                         table[move_ids.product_id.name] = [move_ids.product_uom_qty,
#     #                                                                    move_ids.product_uom_qty - move_ids.quantity_done]
#     #             for obj3 in trf_obj:
#     #                 for move_line2 in obj3.move_line_ids_without_package:
#     #                     if move_line2.product_id.name in pick_location:
#     #                         pass
#     #                     else:
#     #                         print("______________",pick_location)
#     #                         pick_location[move_line2.product_id.name] = move_line2.location_id.complete_name
#     #             for prd, loc in pick_location.items():
#     #                 if prd in table:
#     #                     table[prd].append(loc)
#     #             for product, qty in table.items():
#     #                 if qty[1] == 0:
#     #                     remove_list.append(product)
#     #             for pro_qty in remove_list:
#     #                 del table[pro_qty]
#     #             for product in table:
#     #                 if len(table[product]) == 2:
#     #                     table[product].append("Not Available")
#     #             # ---------------------------- FOR Table (End) -------------------------------------------------------------------------------------
#     #
#     #             lot_obj = request.env['stock.production.lot'].sudo().search([('name', '=', kw['serial'])])
#     #             print("666666666666666666666666666666666666666",lot_obj.name)
#     #             product = lot_obj.product_id
#     #             # -------------------------- Product List and Invalid Serial number (Start) ----------------------
#     #             if not lot_obj:
#     #                 print("11111111111111111111111111111", lot_obj.name)
#     #                 return http.request.render('scan_invert.manual_transfer_page', {'error': "Invalid serial number.",
#     #                                                                             'qty_reqired': reserve_qty,
#     #                                                                             'qty_done': done_qty,
#     #                                                                             'table1': table})
#     #             product_list = []
#     #             print("KKKKKKKKFFDDDDDjjjjjjjjjjjjjjDDDDDDDDDDDDDDDDDDDDDDDDjjjjjj",table)
#     #             for obj in trf_obj:
#     #                 for move_line in obj.move_line_ids_without_package:
#     #                     product_list.append(move_line.product_id.name)
#     #             if lot_obj.product_qty <= 0:
#     #                 print("222222222222222222222222222222222222", lot_obj.name,lot_obj.product_qty)
#     #                 return http.request.render('scan_invert.manual_transfer_page', {'error': "Invalid serial number.",
#     #                                                                             'qty_reqired': reserve_qty,
#     #                                                                             'qty_done': done_qty,
#     #                                                                             'table1': table})
#     #             if lot_obj.product_id.name not in product_list:
#     #                 print("3333333333333333333333333333333333333333333", lot_obj.name)
#     #                 return http.request.render('scan_invert.manual_transfer_page', {'error': "Invalid serial number.",
#     #                                                                             'qty_reqired': reserve_qty,
#     #                                                                             'qty_done': done_qty,
#     #                                                                             'table1': table})
#     #             # -------------------------- Product List and Invalid Serial number (End) ------------------------
#     #
#     #             # ----------------- Already Scanned serial no  (Start) ------------------------------------
#     #             print("----ELSE ELSE ELSE ELSE------")
#     #             scanned_list = []
#     #             for obj in trf_obj:
#     #                 for move_line in obj.move_line_ids_without_package:
#     #                     if move_line.qty_done >= move_line.product_uom_qty:
#     #                         scanned_list.append(move_line.lot_id.name)
#     #             if user_picking.lot_serial in scanned_list:
#     #                 return http.request.render('scan_invert.manual_transfer_page', {'error1': "Already Scanned",
#     #                                                                             'qty_reqired': reserve_qty,
#     #                                                                             'qty_done': done_qty,
#     #                                                                             'table1': table})
#     #             # ----------------- Already Scanned serial no  (End) --------------------------------------
#     #             # fifo_list = eval(trf_obj.fifo_list)
#     #             # if kw['serial'] not in fifo_list and lot_obj.product_id.default_code in table:
#     #             #     return http.request.render('scan_invert.fifo_warning_page', {'serial': kw['serial']})
#     #             # else:
#     #             fifo = []
#     #             last_status = None
#     #             for i in trf_obj.move_line_ids_without_package:
#     #                 fifo.append(i.lot_id.id)
#     #             for obj in trf_obj:
#     #                 if last_status == 1:
#     #                     break
#     #                 for move_line in obj.move_line_ids_without_package:
#     #                     if lot_obj.id in fifo:
#     #                         if move_line.lot_id.id == lot_obj.id:
#     #                             move_line.write({'qty_done': move_line.product_uom_qty, 'company_id': request.env.user.company_id,})
#     #                         else:
#     #                             pass
#     #                     else:
#     #                         if move_line.product_id == product and move_line.qty_done < move_line.product_uom_qty:
#     #                             move_line.write({
#     #                                 'lot_id': lot_obj.id,
#     #                                 'qty_done': move_line.product_uom_qty,
#     #                                 'company_id': request.env.user.company_id,
#     #                             })
#     #                             last_status = 1
#     #                             break
#     #                         elif move_line.product_id == product and move_line.product_id.name not in table:
#     #                             return http.request.render('scan_invert.manual_transfer_page',
#     #                                                     {'error': "Demand of this material is already fulfilled.",
#     #                                                     'qty_reqired': reserve_qty,
#     #                                                     'qty_done': done_qty,
#     #                                                     'table1': table})
#     #
#     #             # -------- FOR Done Qty & Reserv Qty 2 (Start) ---------
#     #             tmp_dq = 0
#     #             tmp_rq = 0
#     #             for obj in trf_obj:
#     #                 for move_line in obj.move_line_ids_without_package:
#     #                     tmp_dq += move_line.qty_done
#     #             for obj2 in trf_obj:
#     #                 for move_ids in obj2.move_ids_without_package:
#     #                     tmp_rq += move_ids.product_uom_qty
#     #             # -------- FOR Done Qty & Reserv Qty 2 (End) -----------
#     #
#     #             # -------------------------- FOR Table 2 (Start) -----------------------------------------------------------------------------------
#     #             table = {}
#     #             remove_list = []
#     #             pick_location = {}
#     #             for obj in trf_obj:
#     #                 for move_line in obj.move_line_ids_without_package:
#     #                     if move_line.product_id.name in table:
#     #                         if move_line.qty_done != move_line.product_uom_qty:
#     #                             table[move_line.product_id.name][1] += move_line.qty_done
#     #             for obj2 in trf_obj:
#     #                 for move_ids in obj2.move_ids_without_package:
#     #                     if move_ids.product_id.name in table:
#     #                         table[move_ids.product_id.name][0] += move_ids.product_uom_qty
#     #                     else:
#     #                         table[move_ids.product_id.name] = [move_ids.product_uom_qty,
#     #                                                                    move_ids.product_uom_qty - move_ids.quantity_done]
#     #             for obj3 in trf_obj:
#     #                 for move_line2 in obj3.move_line_ids_without_package:
#     #                     print("move_line2:::::::::",move_line2.product_id.name)
#     #                     if move_line2.product_id.name in pick_location:
#     #                         pass
#     #                     else:
#     #                         pick_location[move_line2.product_id.name] = move_line2.location_id.complete_name
#     #             print("------->>",pick_location)
#     #             for prd, loc in pick_location.items():
#     #                 if prd in table:
#     #                     table[prd].append(loc)
#     #             for product, qty in table.items():
#     #                 if qty[1] == 0:
#     #                     remove_list.append(product)
#     #             for pro_qty in remove_list:
#     #                 del table[pro_qty]
#     #
#     #             for product in table:
#     #                 if len(table[product]) == 2:
#     #                     table[product].append("Not Available")
#     #
#     #                 # -------------------------- FOR Table 2 (End) -------------------------------------------------------------------------------------
#     #             if tmp_dq != tmp_rq:
#     #                 print("------->>>>> ------->>>>>>",table)
#     #                 return http.request.render('scan_invert.manual_transfer_page', {'success': "Done",
#     #                                                                             'qty_reqired': tmp_rq,
#     #                                                                             'qty_done': tmp_dq,
#     #                                                                             'table1': table})
#     #             else:
#     #                 obj.button_validate()
#     #                 return http.request.render('scan_invert.complete_page', {})
#     #         else:
#     #             pass
#     #         ################################################ For Delivery Orders (End) ###############################################################
#     #
#     #         ################################################## For Internal Transfer (Start) #########################################################
#     #         if self.picking_type == 'Internal Transfers':
#     #             # ------- FOR Done Qty & Reserv Qty (Start) ------------
#     #             for obj in trf_obj:
#     #                 for move_line in obj.move_line_ids_without_package:
#     #                     done_qty += move_line.qty_done
#     #                     lot_serial_list_grn.append(move_line.lot_id.name)
#     #             for res_obj in trf_obj:
#     #                 for moves in res_obj.move_ids_without_package:
#     #                     reserve_qty += moves.product_uom_qty
#     #             # ------- FOR Done Qty & Reserv Qty (End) --------------
#     #
#     #             # ----------------------------- FOR Table (Start) ----------------------------------------------------------------------------------
#     #             table = {}
#     #             remove_list = []
#     #             for obj in trf_obj:
#     #                 for move_line in obj.move_line_ids_without_package:
#     #                     if move_line.product_id.name in table:
#     #                         if move_line.qty_done != move_line.product_uom_qty:
#     #                             table[move_line.product_id.name][1] += move_line.qty_done
#     #
#     #             for obj2 in trf_obj:
#     #                 for move_ids in obj2.move_ids_without_package:
#     #                     if move_ids.product_id.name in table:
#     #                         table[move_ids.product_id.name][0] += move_ids.product_uom_qty
#     #                     else:
#     #                         table[move_ids.product_id.name] = [move_ids.product_uom_qty,
#     #                                                                    move_ids.product_uom_qty - move_ids.quantity_done]
#     #
#     #             for product, qty in table.items():
#     #                 if qty[1] == 0:
#     #                     remove_list.append(product)
#     #             for pro_qty in remove_list:
#     #                 del table[pro_qty]
#     #             # ---------------------------- FOR Table (End) -------------------------------------------------------------------------------------
#     #             if user_picking.lot_serial in lot_serial_list_grn:
#     #                 print(")))))))))))))))))))))))))))**************************")
#     #                 lot = request.env['stock.production.lot'].sudo().search([('name', '=', kw['serial'])])
#     #                 self.tracking = lot.product_id.tracking
#     #                 for obj in trf_obj:
#     #                     for move_line in obj.move_line_ids_without_package:
#     #                         if move_line.lot_id.name == kw['serial']:
#     #                             if move_line.qty_done == move_line.product_uom_qty:
#     #                                 return http.request.render('scan_invert.manual_transfer_page',
#     #                                                            {'error': "Already scanned",
#     #                                                             'qty_reqired': reserve_qty,
#     #                                                             'qty_done': done_qty,
#     #                                                             'table2': table})
#     #                             else:
#     #                                 pass
#     #                         else:
#     #                             pass
#     #                 print("-------------------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
#     #                 return http.request.render('scan_invert.manual_location_page', {'tracking': self.tracking})
#     #             else:
#     #                 return http.request.render('scan_invert.manual_transfer_page', {'error': "Invalid lot/Serial number.",
#     #                                                                             'qty_reqired': reserve_qty,
#     #                                                                             'qty_done': done_qty,
#     #                                                                             'table2': table})
#     #         else:
#     #             pass
#     #         ############################################### For Internal Transfer (End) ##############################################################
#     #     # except:
#     #     #     import werkzeug.utils
#     #     #     action_id = request.env.ref('stock.stock_picking_type_action')
#     #     #     return werkzeug.utils.redirect('/web#action={}'.format(action_id.id))
#
#     # @http.route('/scan_manual_location', website=True, auth="public", csrf=False)
#     # def Location(self, **kw):
#     #     try:
#     #         user_picking = request.env['user.picking'].sudo().search([('user_id', '=', request.env.uid)])
#     #         trf_obj = request.env['stock.picking'].sudo().search([('name', '=', user_picking.picking_name)])
#     #         # trf_obj = request.env['stock.picking'].sudo().search([('name', '=', self.trf_name)])
#     #         loc_obj = request.env['stock.location'].sudo().search([('complete_name', '=', kw['location'])])
#     #         done_qty = 0
#     #         reserve_qty = 0
#     #         if loc_obj:
#     #             for obj in trf_obj:
#     #                 for move_line in obj.move_line_ids_without_package:
#     #                     # if move_line.lot_id.name == self.serial:
#     #                     if move_line.lot_id.name == user_picking.lot_serial:
#     #                         print("janvijanvijanvujnavijangvuh",move_line.lot_id.name,move_line.product_id.name)
#     #                         move_line.write({'location_dest_id': loc_obj.id,
#     #                                          'qty_done': move_line.product_uom_qty,
#     #                                          'company_id': request.env.user.company_id,
#     #                                          })
#     #                                          # 'scan_date': datetime.today().date(),
#     #                                          # 'scanned_by': request.env.user.name,
#     #                                          # 'scan_time': (datetime.now() + timedelta(hours=5, minutes=30)).strftime(
#     #                                          #     "%H:%M"
#     #
#     #             # ------- FOR Done Qty & Reserv Qty (Start) ------------
#     #             for obj in trf_obj:
#     #                 for move_line in obj.move_line_ids_without_package:
#     #                     done_qty += move_line.qty_done
#     #             for res_obj in trf_obj:
#     #                 for moves in res_obj.move_ids_without_package:
#     #                     reserve_qty += moves.product_uom_qty
#     #             # ------- FOR Done Qty & Reserv Qty (End) --------------
#     #
#     #             # ----------------------------- FOR Table (Start) ----------------------------------------------------------------------------------
#     #             table = {}
#     #             remove_list = []
#     #             for obj in trf_obj:
#     #                 for move_line in obj.move_line_ids_without_package:
#     #                     if move_line.product_id.name in table:
#     #                         table[move_line.product_id.name][0] += move_line.product_uom_qty
#     #                         if move_line.qty_done != move_line.product_uom_qty:
#     #                             table[move_line.product_id.name][
#     #                                 1] += move_line.product_uom_qty - move_line.qty_done
#     #                     else:
#     #                         table[move_line.product_id.name] = [move_line.product_uom_qty,
#     #                                                                     move_line.product_uom_qty - move_line.qty_done]
#     #             for product, qty in table.items():
#     #                 if qty[1] <= 0:
#     #                     remove_list.append(product)
#     #             for pro_qty in remove_list:
#     #                 del table[pro_qty]
#     #             # ---------------------------- FOR Table (End) -------------------------------------------------------------------------------------
#     #             if done_qty != reserve_qty and (reserve_qty - done_qty) > 0:
#     #                 return http.request.render('scan_invert.manual_transfer_page', {'success': "DONE",
#     #                                                                             'qty_reqired': reserve_qty,
#     #                                                                             'qty_done': done_qty,
#     #                                                                             'table2': table, })
#     #             else:
#     #                 obj.button_validate()
#     #                 return http.request.render('scan_invert.complete_page', {})
#     #         else:
#     #             return http.request.render('scan_invert.manual_location_page', {'error': "Invalid Location."})
#     #     except:
#     #         import werkzeug.utils
#     #         action_id = request.env.ref('stock.stock_picking_type_action')
#     #         return werkzeug.utils.redirect('/web#action={}'.format(action_id.id))
#
#     # @http.route('/confirm_fifo_warning', website=True, auth="public", csrf=False, type='http')
#     # def confirm_warning(self, **kw):
#     #     try:
#     #         trf_obj = request.env['stock.picking'].sudo().search([('name', '=', self.trf_name)])
#     #         lot_obj = request.env['stock.production.lot'].sudo().search([('name', '=', self.serial)])
#     #         product = lot_obj.product_id
#     #
#     #         last_status = None
#     #         for obj in trf_obj:
#     #             if last_status == 1:
#     #                 break
#     #             for move_line in obj.move_line_ids_without_package:
#     #                 if move_line.product_id == product and move_line.qty_done < move_line.product_uom_qty:
#     #                     move_line.write({'lot_id': lot_obj.id,
#     #                                      'company_id': request.env.user.company_id,
#     #                                      'qty_done': move_line.product_uom_qty,
#     #                                      'scan_date': datetime.today().date(),
#     #                                      'scanned_by': request.env.user.name,
#     #                                      'scan_time': (datetime.now() + timedelta(hours=5, minutes=30)).strftime(
#     #                                          "%H:%M")})
#     #                     last_status = 1
#     #                     break
#     #                 else:
#     #                     pass
#     #
#     #         # -------- FOR Done Qty & Reserv Qty 2 (Start) ---------
#     #         tmp_dq = 0
#     #         tmp_rq = 0
#     #         for obj in trf_obj:
#     #             for move_line in obj.move_line_ids_without_package:
#     #                 tmp_dq += move_line.qty_done
#     #         for obj2 in trf_obj:
#     #             for move_ids in obj2.move_ids_without_package:
#     #                 tmp_rq += move_ids.product_uom_qty
#     #         # -------- FOR Done Qty & Reserv Qty 2 (End) -----------
#     #
#     #         # -------------------------- FOR Table 2 (Start) -----------------------------------------------------------------------------------
#     #         table = {}
#     #         remove_list = []
#     #         pick_location = {}
#     #         for obj in trf_obj:
#     #             for move_line in obj.move_line_ids_without_package:
#     #                 if move_line.product_id.name in table:
#     #                     if move_line.qty_done != move_line.product_uom_qty:
#     #                         table[move_line.product_id.name][1] += move_line.qty_done
#     #         for obj2 in trf_obj:
#     #             for move_ids in obj2.move_ids_without_package:
#     #                 if move_ids.product_id.name in table:
#     #                     table[move_ids.product_id.name][0] += move_ids.product_uom_qty
#     #                 else:
#     #                     table[move_ids.product_id.name] = [move_ids.product_uom_qty,
#     #                                                                move_ids.product_uom_qty - move_ids.quantity_done]
#     #         for obj3 in trf_obj:
#     #             for move_line2 in obj3.move_line_ids_without_package:
#     #                 if move_line2.product_id.name in pick_location:
#     #                     pass
#     #                 else:
#     #                     pick_location[move_line2.product_id.name] = move_line2.location_id.complete_name
#     #         for prd, loc in pick_location.items():
#     #             if prd in table:
#     #                 table[prd].append(loc)
#     #         for product, qty in table.items():
#     #             if qty[1] == 0:
#     #                 remove_list.append(product)
#     #         for pro_qty in remove_list:
#     #             del table[pro_qty]
#     #         for product in table:
#     #                 if len(table[product]) == 2:
#     #                     table[product].append("Not Available")
#     #             # -------------------------- FOR Table 2 (End) -------------------------------------------------------------------------------------
#     #         if tmp_dq != tmp_rq:
#     #             return http.request.render('scan_invert.manual_transfer_page', {'success': "Done",
#     #                                                                         'qty_reqired': tmp_rq,
#     #                                                                         'qty_done': tmp_dq,
#     #                                                                         'table1': table})
#     #         else:
#     #             obj.button_validate()
#     #             return http.request.render('scan_invert.complete_page', {})
#     #     except:
#     #         import werkzeug.utils
#     #         action_id = request.env.ref('stock.stock_picking_type_action')
#     #         return werkzeug.utils.redirect('/web#action={}'.format(action_id.id))
#     #
#     # @http.route('/cancel_fifo_warning', website=True, auth="public", csrf=False, type='http')
#     # def cancel_warning(self, **kw):
#     #     try:
#     #         trf_obj = request.env['stock.picking'].sudo().search([('name', '=', self.trf_name)])
#     #         lot_obj = request.env['stock.production.lot'].sudo().search([('name', '=', self.serial)])
#     #         product = lot_obj.product_id
#     #
#     #         # ------- FOR Done Qty & Reserv Qty (Start) ------------
#     #         tmp_dq = 0
#     #         tmp_rq = 0
#     #         for obj in trf_obj:
#     #             for move_line in obj.move_line_ids_without_package:
#     #                 tmp_dq += move_line.qty_done
#     #         for obj2 in trf_obj:
#     #             for move_ids in obj2.move_ids_without_package:
#     #                 tmp_rq += move_ids.product_uom_qty
#     #         # ------- FOR Done Qty & Reserv Qty (End) --------------
#     #
#     #         # ----------------------------- FOR Table (Start) ----------------------------------------------------------------------------------
#     #         table = {}
#     #         remove_list = []
#     #         pick_location = {}
#     #         for obj in trf_obj:
#     #             for move_line in obj.move_line_ids_without_package:
#     #                 if move_line.product_id.name in table:
#     #                     if move_line.qty_done != move_line.product_uom_qty:
#     #                         table[move_line.product_id.name][1] += move_line.qty_done
#     #         for obj2 in trf_obj:
#     #             for move_ids in obj2.move_ids_without_package:
#     #                 if move_ids.product_id.name in table:
#     #                     table[move_ids.product_id.name][0] += move_ids.product_uom_qty
#     #                 else:
#     #                     table[move_ids.product_id.name] = [move_ids.product_uom_qty,
#     #                                                                move_ids.product_uom_qty - move_ids.quantity_done]
#     #         for obj3 in trf_obj:
#     #             for move_line2 in obj3.move_line_ids_without_package:
#     #                 if move_line2.product_id.name in pick_location:
#     #                     pass
#     #                 else:
#     #                     pick_location[move_line2.product_id.name] = move_line2.location_id.complete_name
#     #         for prd, loc in pick_location.items():
#     #             if prd in table:
#     #                 table[prd].append(loc)
#     #         for product, qty in table.items():
#     #             if qty[1] == 0:
#     #                 remove_list.append(product)
#     #         for pro_qty in remove_list:
#     #             del table[pro_qty]
#     #         for product in table:
#     #                 if len(table[product]) == 2:
#     #                     table[product].append("Not Available")
#     #         # ---------------------------- FOR Table (End) -------------------------------------------------------------------------------------
#     #
#     #         return http.request.render('scan_invert.manual_transfer_page',
#     #                                    {'qty_reqired': tmp_rq, 'qty_done': tmp_dq, 'table1': table})
#     #     except:
#     #         import werkzeug.utils
#     #         action_id = request.env.ref('stock.stock_picking_type_action')
#     #         return werkzeug.utils.redirect('/web#action={}'.format(action_id.id))





