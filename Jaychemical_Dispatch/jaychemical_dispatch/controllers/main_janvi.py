from odoo import http, tools, _
from odoo.http import request
from datetime import datetime, timedelta


class ScanLableShow(http.Controller):

    @http.route('/batch_transfer_scan', website=True, methods=['GET'], auth="public", csrf=False)
    def scan_lable(self, **kw):
        # print("OOOOOOOOOOOOOOOOOOOOOOOOOO", kw)
        request.session['batch'] = kw['batch']
        batch_obj = request.env['stock.picking.batch'].sudo().search([('name', '=', request.session['batch'])])

        lot_list = []

        for rec1 in batch_obj.move_line_ids:
            lot_list.append(rec1.lot_id.name)

        request.session['list_lot'] = lot_list

        table = {}
        request.session['table'] = table


        for obj2 in batch_obj:
            for move_ids in obj2.move_ids:
                if move_ids.product_id.name in request.session['table']:
                    request.session['table'][move_ids.product_id.name][0] += move_ids.product_uom_qty
                    request.session['table'][move_ids.product_id.name][1] += move_ids.product_uom_qty - move_ids.quantity_done
                    print("(((((((((((((((((((((((((((((((",request.session['table'])

                else:
                    request.session['table'][move_ids.product_id.name] = [move_ids.product_uom_qty,
                                                            move_ids.product_uom_qty - move_ids.quantity_done]
                    print("6666666666666666666666666666666666666666",request.session['table'])
        print("1111111111111111111111111111111111111111", request.session['table'])

        return http.request.render('jay_chemical_raw_inward_latest_15.batch_scan_page',
                                   {'table2': request.session['table']})

    @http.route('/batch_transfer_scan', website=True, auth="public", csrf=False, type='http')
    def scan_lable2(self, **kw):
        batch_obj = request.env['stock.picking.batch'].sudo().search([('name', '=', request.session['batch'])])
        print("PPPPPPPPPPPPPPPPPPPP", batch_obj,request.session['list_lot'],request.session['table'])

        for rec in batch_obj.move_line_ids:
            print("LLLLLLLLLLLLLLLLLLLLLLL", rec.product_id, rec.lot_id.name, kw['serial'])
            if kw['serial'] in request.session['list_lot']:
                if kw['serial'] == rec.lot_id.name:
                    print("PPPPPPPPPPPPPjjjjjjjjjjjjjjjjjjjjjjjjjjj", rec.lot_id.name, rec.qty_done)
                    if rec.qty_done == 0:
                        rec.write({
                            'qty_done': 1.0,
                        })
                        request.session['table'] = {}
                        remove_list = []
                        for obj2 in batch_obj:
                            for move_ids in obj2.move_ids:
                                if move_ids.product_id.name in request.session['table'] and move_ids.picking_id.name not in request.session['table']:
                                    request.session['table'][move_ids.product_id.name][0] += move_ids.product_uom_qty
                                    request.session['table'][move_ids.product_id.name][
                                        1] += move_ids.product_uom_qty - move_ids.quantity_done
                                else:
                                    request.session['table'][move_ids.product_id.name] = [move_ids.product_uom_qty,
                                                                       move_ids.product_uom_qty - move_ids.quantity_done]
                        print("hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh",request.session['table'])
                        return http.request.render('jay_chemical_raw_inward_latest_15.batch_scan_page',
                                                   {'success': 'Done',
                                                    'table2':request.session['table']})

                    else:
                        print("OOOOOOOOOOOOOOOOOOOOOOOOO",request.session['table'])
                        return http.request.render('jay_chemical_raw_inward_latest_15.batch_scan_page',{'error':'Already scanned',
                                                   'table2': request.session['table']})
            else:
                print("UUUUUUUUUUUUUUUUUUUUUUU",request.session['table'])
                return http.request.render('jay_chemical_raw_inward_latest_15.batch_scan_page',
                                           {'error': "Invalid serial number.",
                                            'table2': request.session['table']})
