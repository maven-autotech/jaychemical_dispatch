from odoo.exceptions import UserError, ValidationError
from odoo import http, tools, _
from odoo.http import request
from datetime import datetime, timedelta
import collections


class Delivery_page(http.Controller):
    def count_done(self):

        total_values = 0
        remain_values = 0
        done_qty = 0

        delivery_obj1 = request.env['stock.picking'].sudo().search([('name', '=', request.session['delivery'])])
        location_name = delivery_obj1.location_id
        stock_loc_obj = request.env['stock.location'].sudo().search([('id', '=', location_name.id)])
        stock_quant_obj = request.env['stock.quant'].sudo().search(
            [('location_id', '=', location_name.id), ('lot_id.name', '=', request.session['scan_value'])])
        print(":::::::::::::::::::::::::::::::::", stock_quant_obj)

        if len(delivery_obj1.move_line_ids_without_package) != 0:
            for line in delivery_obj1.move_line_ids_without_package:
                print("$$$$$$$$$$$$$$$$$$$",line.product_id.name,stock_quant_obj.product_id.name)
                if line.product_id == stock_quant_obj.product_id:
                    if line.lot_id.name == request.session['scan_value']:
                      done_qty += line.qty_done
                      total_values = float(stock_quant_obj.inventory_quantity_auto_apply) - float(done_qty)
                      print("++++++++++++++++++++++++++++++++++",total_values,done_qty)
                  # remain_values = float(line.quantity_done)
                  # print("LLLLLLLLLLLLLLLLLLLLLLLLLLL",total_values,remain_values)
                    else:
                        total_values = stock_quant_obj.inventory_quantity_auto_apply
                        print(":::::::::::{{{{{{{{{{{{{{}}}}}}",total_values)
                else:
                    total_values = stock_quant_obj.inventory_quantity_auto_apply

        else:
                total_values = stock_quant_obj.inventory_quantity_auto_apply
                # remain_values = 0
                print("5555555555555555555555", total_values)


        return total_values

    @http.route('/delivery_controller', website=True, methods=['GET'], auth="public", csrf=False)
    def deliveryinitial(self, **kw):
        request.session['delivery'] = kw['delivery']
        print("+++++++++++++++++++++++++++++",request.session['delivery'])
        #total_values = self.count_done()
        return http.request.render('jay_chemical_raw_inward_latest_15.delivery_transfer_page',{})

    @http.route('/delivery_controller', website=True, auth="public", csrf=False, type='http')
    def deliverytotalquantity(self, **kw):
        lot1_list = []
        request.session['lot_list'] = lot1_list

        request.session['scan_value'] = kw['serial']
        delivery_obj1 = request.env['stock.picking'].sudo().search([('name', '=', request.session['delivery'])])
        location_name = delivery_obj1.location_id
        stock_loc_obj = request.env['stock.location'].sudo().search([('id', '=',location_name.id)])
        stock_quant_obj = request.env['stock.quant'].sudo().search([('location_id','=',stock_loc_obj.id),('lot_id.name','=',request.session['scan_value'])])
        print("1st page >>>>>>>>>>>>>>>>>>>>>>>>>>>>",stock_quant_obj)

        for rec1 in delivery_obj1.move_line_ids_without_package:
            print("PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP", rec1.lot_id.name)
            request.session['lot_list'].append(rec1.lot_id.name)

        if len(delivery_obj1.move_line_ids_without_package) == 0:
            if stock_quant_obj and stock_quant_obj.inventory_quantity_auto_apply!= 0.0:
                total_values = self.count_done()
                if total_values > stock_quant_obj.inventory_quantity_auto_apply:
                    return http.request.render('jay_chemical_raw_inward_latest_15.delivery_transfer_page',
                                               {'error': 'Product is not avaliable for this location.'})

                elif stock_quant_obj.inventory_quantity_auto_apply >= 0:
                    values = {
                        'inventory_quantity_auto_apply': stock_quant_obj.inventory_quantity_auto_apply
                    }
                    print("=========================================================", values)
                return http.request.render('jay_chemical_raw_inward_latest_15.delivery_scanned_page',
                                           {'values': total_values, 'lot_id_name': request.session['scan_value']})
            else:
                return http.request.render('jay_chemical_raw_inward_latest_15.delivery_transfer_page',
                                           {'error':'Product is not avaliable for this location.'})
        else:
            for rec in delivery_obj1.move_line_ids_without_package:
                total_values = self.count_done()
                print("777777777777777777777777777777777777",total_values,request.session['scan_value'])
                if request.session['scan_value'] in request.session['lot_list'] and total_values != 0:
                    print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",total_values,stock_quant_obj.inventory_quantity_auto_apply)
                    return http.request.render('jay_chemical_raw_inward_latest_15.delivery_scanned_page',
                                               {'values': total_values, 'lot_id_name': request.session['scan_value']})
                elif request.session['scan_value'] not in request.session['lot_list'] and total_values != 0:
                    return http.request.render('jay_chemical_raw_inward_latest_15.delivery_scanned_page',
                                               {'values': total_values, 'lot_id_name': request.session['scan_value']})
                else:
                    return http.request.render('jay_chemical_raw_inward_latest_15.delivery_transfer_page',
                                               {'error': 'Product is not avaliable for this location.'})



    @http.route('/delivery_scanned', website=True, auth="public", csrf=False, type='http')
    def deliverysubmit(self, **kw):

        delivery_obj1 = request.env['stock.picking'].sudo().search([('name', '=', request.session['delivery'])])
        location_name = delivery_obj1.location_id

        stock_loc_obj = request.env['stock.location'].sudo().search([('id', '=', location_name.id)])
        print("+++++++++++++++++++++++++++++", stock_loc_obj.complete_name)
        stock_quant_obj = request.env['stock.quant'].sudo().search(
            [('location_id', '=', stock_loc_obj.id), ('lot_id.name', '=', request.session['scan_value'])])
        print("2nd page>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.",stock_quant_obj.lot_id)


        if stock_quant_obj.inventory_quantity_auto_apply >= float(kw['Quantity']) and float(kw['Quantity']) > 0:
            if len(delivery_obj1.move_line_ids_without_package) == 0:
                print("1111111111111111111111111")
                delivery_obj1.move_line_ids_without_package.sudo().create({
                    'picking_id': delivery_obj1.id,
                    'product_id': stock_quant_obj.product_id.id,
                    'lot_id': stock_quant_obj.lot_id.id,
                    'qty_done': float(kw['Quantity']),
                    'company_id': 1,
                    'location_id': stock_loc_obj.id,
                    'location_dest_id': 5,
                })
                total_values = self.count_done()
                return http.request.render('jay_chemical_raw_inward_latest_15.delivery_transfer_page', {'success':'Successfully Dispatch','values': total_values, 'lot_id_name':  request.session['scan_value']})

            else:

                    print("22222222222222222222")
                    delivery_obj1.move_line_ids_without_package.sudo().create({
                         'picking_id': delivery_obj1.id,
                         'product_id': stock_quant_obj.product_id.id,
                         'lot_id': stock_quant_obj.lot_id.id,
                         'qty_done': float(kw['Quantity']),
                         'company_id': 1,
                         'location_id': stock_loc_obj.id,
                         'location_dest_id': 5,
                        })
                    total_values = self.count_done()
                    return http.request.render('jay_chemical_raw_inward_latest_15.delivery_transfer_page', {'success':'Successfully Dispatch','values': total_values, 'lot_id_name':  request.session['scan_value']})

        else:
            total_values = self.count_done()
            print("PPPPPPPPPPPPPPPPPPPPPPP",total_values)
            return http.request.render('jay_chemical_raw_inward_latest_15.delivery_scanned_page', {'error':'You can not add more quantity','values': total_values, 'lot_id_name':  request.session['scan_value']})

    @http.route('/back_button', website=True, auth="public", csrf=False)
    def back_button(self):
        delivery_obj1 = request.env['stock.picking'].sudo().search([('name', '=', request.session['delivery'])])
        import werkzeug.utils
        action_id = request.env.ref('stock.action_picking_tree_ready')

        return werkzeug.utils.redirect(
            '/web#id={}&cids=1&menu_id=173&action={}&active_id=2&model=stock.picking&view_type=form'.format(
                delivery_obj1.id,action_id.id))

