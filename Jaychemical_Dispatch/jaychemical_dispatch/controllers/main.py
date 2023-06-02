from odoo.exceptions import UserError, ValidationError
from odoo import http, tools, _
from odoo.http import request
from datetime import datetime, timedelta
import collections


class ManualTransfer(http.Controller):

    @http.route('/scan_manual_transfer', website=True, methods=['GET'], auth="public", csrf=False)
    def ManualTransfer1(self, **kw):

        done_qty = 0
        reserve_qty = 0

        request.session['source'] = kw['source']
        stock = request.env['stock.picking'].sudo().search([('name', '=', request.session['source'])])

        # ------- FOR Done Qty & Reserv Qty (Start) ------------
        for obj in stock:
            for move_line in obj.move_line_ids_without_package:
                done_qty += move_line.qty_done
        for res_obj in stock:
            for moves in res_obj.move_ids_without_package:
                reserve_qty += moves.product_uom_qty
        # ------- FOR Done Qty & Reserv Qty (End) --------------

        # ----------------------------- FOR Table (Start) ----------------------------------------------------------------------------------
        table = {}
        remove_list = []
        for obj in stock:
            for move_line in obj.move_line_ids_without_package:
                print("**************************************", move_line.product_id.name)
                if move_line.product_id.name in table:
                    if move_line.qty_done != move_line.product_uom_qty:
                        table[move_line.product_id.name][1] += move_line.qty_done
        for obj2 in stock:
            for move_ids in obj2.move_ids_without_package:
                if move_ids.product_id.name in table:
                    table[move_ids.product_id.name][0] += move_ids.product_uom_qty
                else:
                    table[move_ids.product_id.name] = [move_ids.product_uom_qty,
                                                       move_ids.product_uom_qty - move_ids.quantity_done]
        for product, qty in table.items():
            if qty[1] == 0:
                remove_list.append(product)
        for pro_qty in remove_list:
            del table[pro_qty]
        # ---------------------------- FOR Table (End) -------------------------------------------------------------------------------------
        print("8888999999999999999999999999999999999999999999", table)
        return http.request.render('jaychemical_dispatch.manual_transfer_page',
                                   {'qty_reqired': reserve_qty, 'qty_done': done_qty, 'table2': table})



    @http.route('/scan_manual_transfer', website=True, auth="public", csrf=False, type='http')
    def ManualTransfer2(self, **kw):
        # try:
            done_qty = 0
            reserve_qty = 0
            trf_obj = request.env['stock.picking'].sudo().search([('name', '=', request.session['source'])])


            lot_serial_list_grn = []
            self.serial = kw['serial']

            self.picking_type = trf_obj.picking_type_id.name

            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%",trf_obj)
            ################################################## For Delivery Orders (Start) ###########################################################
            if self.picking_type == 'Internal Transfers':
                # ------- FOR Done Qty & Reserv Qty (Start) ------------
                for obj in trf_obj:
                    for move_line in obj.move_line_ids_without_package:
                        lot_serial_list_grn.append(move_line.lot_id.name)
                        done_qty += move_line.qty_done
                for res_obj in trf_obj:
                    for moves in res_obj.move_ids_without_package:
                        reserve_qty += moves.product_uom_qty
                # ------- FOR Done Qty & Reserv Qty (End) --------------

                # ----------------------------- FOR Table (Start) ----------------------------------------------------------------------------------
                table = {}
                remove_list = []
                pick_location = {}
                for obj in trf_obj:
                    for move_line in obj.move_line_ids_without_package:
                        if move_line.product_id.name in table:
                            if move_line.qty_done != move_line.product_uom_qty:
                                table[move_line.product_id.name][1] += move_line.qty_done
                for obj2 in trf_obj:
                    for move_ids in obj2.move_ids_without_package:
                        if move_ids.product_id.name in table:
                            table[move_ids.product_id.name][0] += move_ids.product_uom_qty
                        else:
                            table[move_ids.product_id.name] = [move_ids.product_uom_qty,
                                                                       move_ids.product_uom_qty - move_ids.quantity_done]
                for obj3 in trf_obj:
                    for move_line2 in obj3.move_line_ids_without_package:
                        if move_line2.product_id.name in pick_location:
                            pass
                        else:
                            print("______________",pick_location)
                            pick_location[move_line2.product_id.name] = move_line2.location_id.complete_name
                for prd, loc in pick_location.items():
                    if prd in table:
                        table[prd].append(loc)
                for product, qty in table.items():
                    if qty[1] == 0:
                        remove_list.append(product)
                for pro_qty in remove_list:
                    del table[pro_qty]
                for product in table:
                    if len(table[product]) == 2:
                        table[product].append("Not Available")
                # ---------------------------- FOR Table (End) -------------------------------------------------------------------------------------

                lot_obj = request.env['stock.lot'].sudo().search([('name', '=', kw['serial'])])
                print("666666666666666666666666666666666666666",lot_obj.name,lot_serial_list_grn)
                product = lot_obj.product_id
                # -------------------------- Product List and Invalid Serial number (Start) ----------------------
                if not lot_obj:
                    print("11111111111111111111111111111", lot_obj.name)
                    return http.request.render('jaychemical_dispatch.manual_transfer_page', {'error': "Invalid serial number.",
                                                                                'qty_reqired': reserve_qty,
                                                                                'qty_done': done_qty,
                                                                                'table1': table})
                product_list = []
                print("KKKKKKKKFFDDDDDjjjjjjjjjjjjjjDDDDDDDDDDDDDDDDDDDDDDDDjjjjjj",table)
                for obj in trf_obj:
                    for move_line in obj.move_line_ids_without_package:
                        product_list.append(move_line.product_id.name)
                if lot_obj.product_qty <= 0:
                    print("222222222222222222222222222222222222", lot_obj.name,lot_obj.product_qty)
                    return http.request.render('jaychemical_dispatch.manual_transfer_page', {'error': "Invalid serial number.",
                                                                                'qty_reqired': reserve_qty,
                                                                                'qty_done': done_qty,
                                                                                'table1': table})
                if lot_obj.product_id.name not in product_list:
                    print("3333333333333333333333333333333333333333333", lot_obj.name)
                    return http.request.render('jaychemical_dispatch.manual_transfer_page', {'error': "Invalid serial number.",
                                                                                'qty_reqired': reserve_qty,
                                                                                'qty_done': done_qty,
                                                                                'table1': table})
                # -------------------------- Product List and Invalid Serial number (End) ------------------------

                # ----------------- Already Scanned serial no  (Start) ------------------------------------
                print("----ELSE ELSE ELSE ELSE------")
                scanned_list = []
                for obj in trf_obj:
                    for move_line in obj.move_line_ids_without_package:
                        if move_line.qty_done >= move_line.reserved_uom_qty:
                            scanned_list.append(move_line.lot_id.name)

                # ----------------- Already Scanned serial no  (End) --------------------------------------
                # fifo_list = eval(trf_obj.fifo_list)
                # if kw['serial'] not in fifo_list and lot_obj.product_id.default_code in table:
                #     return http.request.render('jay_chemical_raw_inward_latest_15.fifo_warning_page', {'serial': kw['serial']})
                # else:
                fifo = []
                last_status = None
                for i in trf_obj.move_line_ids_without_package:
                    fifo.append(i.lot_id.id)
                for obj in trf_obj:
                    if last_status == 1:
                        break
                    for move_line in obj.move_line_ids_without_package:
                        print("LLLLLLLLLLLLLMMMMMMMMMMMMMMMMM",lot_obj)
                        if lot_obj.name in lot_serial_list_grn:
                            if lot_obj.name not in scanned_list:
                                if lot_obj.id in fifo:
                                    if move_line.lot_id.id == lot_obj.id:
                                        move_line.write({'qty_done': move_line.reserved_uom_qty, 'company_id': request.env.user.company_id,})
                                    else:
                                        pass
                                else:
                                    if move_line.product_id == product and move_line.qty_done < move_line.product_uom_qty:
                                        move_line.write({
                                            'lot_id': lot_obj.id,
                                            'qty_done': move_line.product_uom_qty,
                                            'company_id': request.env.user.company_id,
                                        })
                                        last_status = 1
                                        break
                                    elif move_line.product_id == product and move_line.product_id.name not in table:
                                        return http.request.render('jaychemical_dispatch.manual_transfer_page',
                                                                {'error': "Demand of this material is already fulfilled.",
                                                                'qty_reqired': reserve_qty,
                                                                'qty_done': done_qty,
                                                                'table1': table})
                            else:
                                return http.request.render('jaychemical_dispatch.manual_transfer_page',
                                                           {
                                                               'error': "This serial number Already scanned",
                                                               'qty_reqired': reserve_qty,
                                                               'qty_done': done_qty,
                                                               'table1': table})

                        else:
                            return http.request.render('jaychemical_dispatch.manual_transfer_page',
                                                       {'error': "This serial number is not valid for this document.",
                                                        'qty_reqired': reserve_qty,
                                                        'qty_done': done_qty,
                                                        'table1': table})


                # -------- FOR Done Qty & Reserv Qty 2 (Start) ---------
                tmp_dq = 0
                tmp_rq = 0
                tmp_qty_done = 0
                for obj in trf_obj:
                    for move_line in obj.move_line_ids_without_package:
                        tmp_dq += move_line.qty_done
                        tmp_qty_done +=move_line.reserved_uom_qty
                for obj2 in trf_obj:
                    for move_ids in obj2.move_ids_without_package:
                        tmp_rq += move_ids.product_uom_qty
                # -------- FOR Done Qty & Reserv Qty 2 (End) -----------

                # -------------------------- FOR Table 2 (Start) -----------------------------------------------------------------------------------
                table = {}
                remove_list = []
                pick_location = {}
                for obj in trf_obj:
                    for move_line in obj.move_line_ids_without_package:
                        if move_line.product_id.name in table:
                            if move_line.qty_done != move_line.product_uom_qty:
                                table[move_line.product_id.name][1] += move_line.qty_done
                for obj2 in trf_obj:
                    for move_ids in obj2.move_ids_without_package:
                        if move_ids.product_id.name in table:
                            table[move_ids.product_id.name][0] += move_ids.product_uom_qty
                        else:
                            table[move_ids.product_id.name] = [move_ids.product_uom_qty,
                                                                       move_ids.product_uom_qty - move_ids.quantity_done]
                for obj3 in trf_obj:
                    for move_line2 in obj3.move_line_ids_without_package:
                        print("move_line2:::::::::",move_line2.product_id.name)
                        if move_line2.product_id.name in pick_location:
                            pass
                        else:
                            pick_location[move_line2.product_id.name] = move_line2.location_id.complete_name
                print("------->>",pick_location)
                for prd, loc in pick_location.items():
                    if prd in table:
                        table[prd].append(loc)
                for product, qty in table.items():
                    if qty[1] == 0:
                        remove_list.append(product)
                for pro_qty in remove_list:
                    del table[pro_qty]

                for product in table:
                    if len(table[product]) == 2:
                        table[product].append("Not Available")

                    # -------------------------- FOR Table 2 (End) -------------------------------------------------------------------------------------
                if tmp_dq != tmp_rq and tmp_qty_done != tmp_dq :
                    print("KKKKKKKKKKKKKKKKKKKKKKKKKKBBBBBBBBBBBBBBBBBB",tmp_dq,tmp_qty_done)
                    return http.request.render('jaychemical_dispatch.manual_transfer_page', {'success': "Done",
                                                                                'qty_reqired': tmp_rq,
                                                                                'qty_done': tmp_dq,
                                                                                'table1': table})
                elif tmp_qty_done == tmp_dq:
                    print("???????????????????___________________________",tmp_qty_done,)
                    obj.button_validate()
                    return http.request.render('jaychemical_dispatch.complete_page', {})

            elif self.picking_type == 'Delivery Orders':
                for obj in trf_obj:
                    for move_line in obj.move_line_ids_without_package:
                        done_qty += move_line.qty_done

                for res_obj in trf_obj:
                    for moves in res_obj.move_ids_without_package:
                        reserve_qty += moves.product_uom_qty

                table = {}
                remove_list = []
                pick_location = {}
                for obj in trf_obj:
                    for move_line in obj.move_line_ids_without_package:
                        if move_line.product_id.name in table:
                            if move_line.qty_done != move_line.product_uom_qty:
                                table[move_line.product_id.name][1] += move_line.qty_done
                for obj2 in trf_obj:
                    for move_ids in obj2.move_ids_without_package:
                        if move_ids.product_id.name in table:
                            table[move_ids.product_id.name][0] += move_ids.product_uom_qty
                        else:
                            table[move_ids.product_id.name] = [move_ids.product_uom_qty,
                                                               move_ids.product_uom_qty - move_ids.quantity_done]

                for obj3 in trf_obj:
                    for move_line2 in obj3.move_line_ids_without_package:
                        if move_line2.product_id.name in pick_location:
                            pass
                        else:
                            print("______________", pick_location)
                            pick_location[move_line2.product_id.name] = move_line2.location_id.complete_name
                for prd, loc in pick_location.items():
                    if prd in table:
                        table[prd].append(loc)
                for product, qty in table.items():
                    if qty[1] == 0:
                        remove_list.append(product)
                for pro_qty in remove_list:
                    del table[pro_qty]
                for product in table:
                    if len(table[product]) == 2:
                        table[product].append("Not Available")

                lot_obj = request.env['stock.lot'].sudo().search([('name', '=', kw['serial'])])
                print("666666666666666666666666666666666666666", lot_obj.name)
                product = lot_obj.product_id
                # -------------------------- Product List and Invalid Serial number (Start) ----------------------
                if not lot_obj:
                    print("11111111111111111111111111111", lot_obj.name)
                    return http.request.render('jaychemical_dispatch.manual_transfer_page',
                                               {'error': "Invalid serial number.", 'qty_reqired': reserve_qty,
                                                'qty_done': done_qty, 'table1': table})
                product_list = []
                print("KKKKKKKKFFDDDDDjjjjjjjjjjjjjjDDDDDDDDDDDDDDDDDDDDDDDDjjjjjj", table)
                for obj in trf_obj:
                    for move_line in obj.move_line_ids_without_package:
                        product_list.append(move_line.product_id.name)
                if lot_obj.product_qty <= 0:
                    print("222222222222222222222222222222222222", lot_obj.name, lot_obj.product_qty)
                    return http.request.render('jaychemical_dispatch.manual_transfer_page',
                                               {'error': "Invalid serial number.", 'qty_reqired': reserve_qty,
                                                'qty_done': done_qty, 'table1': table})


                if lot_obj.product_id.name not in product_list:
                    print("3333333333333333333333333333333333333333333", lot_obj.name)
                    return http.request.render('jaychemical_dispatch.manual_transfer_page', {'error': "Invalid serial number.",
                                                                                'qty_reqired': reserve_qty,
                                                                                'qty_done': done_qty,
                                                                                'table1': table})

                # if lot_obj.is_used == True:
                #     print("rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr", lot_obj.name)
                #     return http.request.render('jay_chemical_raw_inward_latest_15.manual_transfer_page', {'error': "This serial number already scanned.",
                #                                                                 'qty_reqired': reserve_qty,
                #                                                                 'qty_done': done_qty,
                #                                                                 'table1': table})


                print("----ELSE ELSE ELSE ELSE------")
                scanned_list = []
                for obj in trf_obj:
                    for move_line in obj.move_line_ids_without_package:
                        if move_line.qty_done >= move_line.reserved_uom_qty:
                            scanned_list.append(move_line.lot_id.name)


                fifo = []
                last_status = None
                for i in trf_obj.move_line_ids_without_package:
                    fifo.append(i.lot_id.id)
                for obj in trf_obj:
                    if last_status == 1:
                        break
                    for move_line in obj.move_line_ids_without_package:
                        if lot_obj.id in fifo:
                            if move_line.lot_id.id == lot_obj.id:
                                move_line.write({'qty_done': move_line.reserved_uom_qty,
                                                 'company_id': request.env.user.company_id, })
                                # lot_obj.is_used = True
                            else:
                                pass
                        else:
                            if move_line.product_id == product and move_line.qty_done < move_line.product_uom_qty:
                                move_line.write({'lot_id': lot_obj.id, 'qty_done': move_line.product_uom_qty,
                                    'company_id': request.env.user.company_id, })
                                # lot_obj.is_used = True
                                print("777777777777777777777777", scanned_list)
                                last_status = 1
                                break
                            elif move_line.product_id == product and move_line.product_id.name not in table:
                                return http.request.render('jaychemical_dispatch.manual_transfer_page',
                                                           {'error': "Demand of this material is already fulfilled.",
                                                            'qty_reqired': reserve_qty, 'qty_done': done_qty,
                                                            'table1': table})
                tmp_dq = 0
                tmp_rq = 0
                for obj in trf_obj:
                    for move_line in obj.move_line_ids_without_package:
                        tmp_dq += move_line.qty_done
                for obj2 in trf_obj:
                    for move_ids in obj2.move_ids_without_package:
                        tmp_rq += move_ids.product_uom_qty  # -------- FOR Done Qty & Reserv Qty 2 (End) -----------

                table = {}
                remove_list = []
                pick_location = {}
                for obj in trf_obj:
                    for move_line in obj.move_line_ids_without_package:
                        if move_line.product_id.name in table:
                            if move_line.qty_done != move_line.product_uom_qty:
                                table[move_line.product_id.name][1] += move_line.qty_done
                for obj2 in trf_obj:
                    for move_ids in obj2.move_ids_without_package:
                        if move_ids.product_id.name in table:
                            table[move_ids.product_id.name][0] += move_ids.product_uom_qty
                        else:
                            table[move_ids.product_id.name] = [move_ids.product_uom_qty,
                                                               move_ids.product_uom_qty - move_ids.quantity_done]
                for obj3 in trf_obj:
                    for move_line2 in obj3.move_line_ids_without_package:
                        print("move_line2:::::::::", move_line2.product_id.name)
                        if move_line2.product_id.name in pick_location:
                            pass
                        else:
                            pick_location[move_line2.product_id.name] = move_line2.location_id.complete_name
                print("------->>", pick_location)
                for prd, loc in pick_location.items():
                    if prd in table:
                        table[prd].append(loc)
                for product, qty in table.items():
                    if qty[1] == 0:
                        remove_list.append(product)
                for pro_qty in remove_list:
                    del table[pro_qty]

                for product in table:
                    if len(table[product]) == 2:
                        table[product].append("Not Available")

                    # -------------------------- FOR Table 2 (End) -------------------------------------------------------------------------------------
                if tmp_dq != tmp_rq:
                    print("------->>>>> ------->>>>>>", table)
                    return http.request.render('jaychemical_dispatch.manual_transfer_page',
                                               {'success': "Done", 'qty_reqired': tmp_rq, 'qty_done': tmp_dq,
                                                'table1': table})
                else:
                    print("++++++++++++(((((L<",obj,scanned_list)
                    for rec in obj3.move_line_ids_without_package:
                        if tmp_dq == tmp_rq:
                            lot_obj1 = request.env['stock.lot'].sudo().search([('name','=',rec.lot_id.name)])
                            # for re in lot_obj1:
                            #     if re.name == rec.lot_id.name:
                            #         re.is_delivered = True
                    obj.button_validate()
                    return http.request.render('jaychemical_dispatch.complete_page', {})


    @http.route('/confirm_fifo_warning', website=True, auth="public", csrf=False, type='http')
    def confirm_warning(self, **kw):
        try:
            trf_obj = request.env['stock.picking'].sudo().search([('name', '=', self.trf_name)])
            lot_obj = request.env['stock.lot'].sudo().search([('name', '=', self.serial)])
            product = lot_obj.product_id

            last_status = None
            for obj in trf_obj:
                if last_status == 1:
                    break
                for move_line in obj.move_line_ids_without_package:
                    if move_line.product_id == product and move_line.qty_done < move_line.product_uom_qty:
                        move_line.write({'lot_id': lot_obj.id,
                                         'company_id': request.env.user.company_id,
                                         'qty_done': move_line.product_uom_qty,
                                         'scan_date': datetime.today().date(),
                                         'scanned_by': request.env.user.name,
                                         'scan_time': (datetime.now() + timedelta(hours=5, minutes=30)).strftime(
                                             "%H:%M")})
                        last_status = 1
                        break
                    else:
                        pass

            # -------- FOR Done Qty & Reserv Qty 2 (Start) ---------
            tmp_dq = 0
            tmp_rq = 0
            for obj in trf_obj:
                for move_line in obj.move_line_ids_without_package:
                    tmp_dq += move_line.qty_done
            for obj2 in trf_obj:
                for move_ids in obj2.move_ids_without_package:
                    tmp_rq += move_ids.product_uom_qty
            # -------- FOR Done Qty & Reserv Qty 2 (End) -----------

            # -------------------------- FOR Table 2 (Start) -----------------------------------------------------------------------------------
            table = {}
            remove_list = []
            pick_location = {}
            for obj in trf_obj:
                for move_line in obj.move_line_ids_without_package:
                    if move_line.product_id.name in table:
                        if move_line.qty_done != move_line.product_uom_qty:
                            table[move_line.product_id.name][1] += move_line.qty_done
            for obj2 in trf_obj:
                for move_ids in obj2.move_ids_without_package:
                    if move_ids.product_id.name in table:
                        table[move_ids.product_id.name][0] += move_ids.product_uom_qty
                    else:
                        table[move_ids.product_id.name] = [move_ids.product_uom_qty,
                                                                   move_ids.product_uom_qty - move_ids.quantity_done]
            for obj3 in trf_obj:
                for move_line2 in obj3.move_line_ids_without_package:
                    if move_line2.product_id.name in pick_location:
                        pass
                    else:
                        pick_location[move_line2.product_id.name] = move_line2.location_id.complete_name
            for prd, loc in pick_location.items():
                if prd in table:
                    table[prd].append(loc)
            for product, qty in table.items():
                if qty[1] == 0:
                    remove_list.append(product)
            for pro_qty in remove_list:
                del table[pro_qty]
            for product in table:
                    if len(table[product]) == 2:
                        table[product].append("Not Available")
                # -------------------------- FOR Table 2 (End) -------------------------------------------------------------------------------------
            if tmp_dq != tmp_rq:
                return http.request.render('jaychemical_dispatch.manual_transfer_page', {'success': "Done",
                                                                            'qty_reqired': tmp_rq,
                                                                            'qty_done': tmp_dq,
                                                                            'table1': table})
            else:
                obj.button_validate()
                return http.request.render('jaychemical_dispatch.complete_page', {})
        except:
            import werkzeug.utils
            action_id = request.env.ref('stock.stock_picking_type_action')
            return werkzeug.utils.redirect('/web#action={}'.format(action_id.id))

    @http.route('/cancel_fifo_warning', website=True, auth="public", csrf=False, type='http')
    def cancel_warning(self, **kw):
        try:
            trf_obj = request.env['stock.picking'].sudo().search([('name', '=', self.trf_name)])
            lot_obj = request.env['stock.lot'].sudo().search([('name', '=', self.serial)])
            product = lot_obj.product_id

            # ------- FOR Done Qty & Reserv Qty (Start) ------------
            tmp_dq = 0
            tmp_rq = 0
            for obj in trf_obj:
                for move_line in obj.move_line_ids_without_package:
                    tmp_dq += move_line.qty_done
            for obj2 in trf_obj:
                for move_ids in obj2.move_ids_without_package:
                    tmp_rq += move_ids.product_uom_qty
            # ------- FOR Done Qty & Reserv Qty (End) --------------

            # ----------------------------- FOR Table (Start) ----------------------------------------------------------------------------------
            table = {}
            remove_list = []
            pick_location = {}
            for obj in trf_obj:
                for move_line in obj.move_line_ids_without_package:
                    if move_line.product_id.name in table:
                        if move_line.qty_done != move_line.product_uom_qty:
                            table[move_line.product_id.name][1] += move_line.qty_done
            for obj2 in trf_obj:
                for move_ids in obj2.move_ids_without_package:
                    if move_ids.product_id.name in table:
                        table[move_ids.product_id.name][0] += move_ids.product_uom_qty
                    else:
                        table[move_ids.product_id.name] = [move_ids.product_uom_qty,
                                                                   move_ids.product_uom_qty - move_ids.quantity_done]
            for obj3 in trf_obj:
                for move_line2 in obj3.move_line_ids_without_package:
                    if move_line2.product_id.name in pick_location:
                        pass
                    else:
                        pick_location[move_line2.product_id.name] = move_line2.location_id.complete_name
            for prd, loc in pick_location.items():
                if prd in table:
                    table[prd].append(loc)
            for product, qty in table.items():
                if qty[1] == 0:
                    remove_list.append(product)
            for pro_qty in remove_list:
                del table[pro_qty]
            for product in table:
                    if len(table[product]) == 2:
                        table[product].append("Not Available")
            # ---------------------------- FOR Table (End) -------------------------------------------------------------------------------------

            return http.request.render('jaychemical_dispatch.manual_transfer_page',
                                       {'qty_reqired': tmp_rq, 'qty_done': tmp_dq, 'table1': table})
        except:
            import werkzeug.utils
            action_id = request.env.ref('stock.stock_picking_type_action')
            return werkzeug.utils.redirect('/web#action={}'.format(action_id.id))

    @http.route('/back_home', website=True, auth="public", csrf=False, type='http')
    def back_button(self, **kw):
        import werkzeug.utils
        trf_obj = request.env['stock.picking'].sudo().search([('name', '=', request.session['source'])])
        action_id = request.env.ref('stock.action_picking_tree_ready')
        return werkzeug.utils.redirect('/web#id={}&cids=1&menu_id=173&action={}&active_id=41&model=stock.picking&view_type=form'.format(trf_obj.id,action_id.id))





