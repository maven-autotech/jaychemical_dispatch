from odoo.exceptions import UserError, ValidationError
from odoo import http, tools, _
from odoo.http import request
from datetime import datetime, timedelta
import collections
import serial
import time
import base64
import requests
from requests_ntlm import HttpNtlmAuth
import json


class Inventory(http.Controller):

    request.session['ser_list'] = []

    @http.route('/select_product', website=True, methods=['GET'], auth="public", csrf=False)
    def select_product(self, **kw):

        try:
            request.session['id'] = kw['id']
            print("LKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK",kw)
            return http.request.render('vidya.select_product_page',
                                       {})
        except:
            stock_pick_obj = request.env['stock.picking'].sudo().search([('id', '=', request.session['id'])])
            import werkzeug.utils
            action_id = request.env.ref('stock.action_picking_tree_ready')
            return werkzeug.utils.redirect(
                '/web#id=223&cids={}&menu_id=178&action={}&active_id=1&model=stock.picking&view_type=form'.format(
                    stock_pick_obj.id, action_id.id))

    @http.route('/select_product', website=True, auth="public", csrf=False, type='http')
    def select_product1(self, **kw):
        product = kw['pro'].split("|")
        request.session['product'] = product[0]
        request.session['line_no'] = product[1]
        self.pro_list = []
        self.len_pro = []


        stock_pick_obj = request.env['stock.picking'].sudo().search([('id', '=', request.session['id'])])
        pro_obj = request.env['product.template'].sudo().search([('name', '=', request.session['product'])])
        request.session['unit'] = pro_obj.unit

        used = request.env['num.ser'].sudo().search([('series_code', '=', pro_obj.default_code)])
        num_ser = used.last_number_used

        self.table = {}
        for move_line in stock_pick_obj.move_ids_without_package:
            if move_line.product_id.name == request.session['product'] and move_line.line_no == request.session[
                'line_no']:
                # self.table[move_line.product_id.name] = [move_line.product_uom_qty,
                #                                          move_line.product_uom_qty - move_line.quantity_done,
                #                                          request.session['unit']]
                self.table[move_line.product_id.name] = [
                    move_line.product_uom_qty,
                    abs(round(
                        move_line.product_uom_qty - move_line.quantity_done,
                        3)), request.session['unit']]

        self.ser_list1 = {}
        for re in stock_pick_obj.move_ids_without_package.move_line_nosuggest_ids:
            if re.product_id.name in self.ser_list1:
                print("****************&&&&&&&&&&&&&^^^^^^^^^^^^^^^^^^^@2222222222222222222222222",
                      self.ser_list1[re.product_id.name][0], re.lot_name)
                self.ser_list1[re.product_id.name].append(re.lot_name)
            else:
                self.ser_list1[re.product_id.name] = [re.lot_name]
        print("1111111111111111111111111111111111", self.ser_list1)

        self.table1 = {}
        for move_line in stock_pick_obj.move_ids_without_package:
            print("serial******************************", move_line.product_id.name)
            if move_line.product_id.name == request.session['product'] and move_line.line_no == request.session[
                'line_no']:
                self.table1[move_line.product_id.name] = [move_line.product_uom_qty,
                                                          move_line.product_uom_qty - move_line.quantity_done,
                                                          request.session['unit']]

        for rec in stock_pick_obj.move_ids_without_package:
            self.pro_list.append(rec.product_id.name)
        for re in stock_pick_obj.move_ids_without_package.move_line_nosuggest_ids:

            if re.product_id.name == request.session['product']:
                self.len_pro.append(re.lot_name)

        for rec in stock_pick_obj.move_ids_without_package:
            if request.session['product'] in self.pro_list:
                if rec.product_id.name == request.session['product']:
                    print("9999999999999999999999999999999999999999999999")
                    if rec.line_no == request.session['line_no']:
                        print("**8888888888888888888888888888888888888888")
                        if rec.product_id.tracking == "lot":
                            request.session['track_pro'] = False
                            if pro_obj.by_system == True:
                                request.session['by_sys'] = True

                                # url = "http://117.247.85.169:7148/BC200-TEST/ODataV4/Company('VWPL_01042022')/PowerApp_ScanNoSeriesLine"
                                # payload = ""
                                # headers = {
                                #     'Accept': 'application/json'
                                # }
                                #
                                # response = requests.request("GET", url, headers=headers,
                                #                             auth=HttpNtlmAuth("Vidya\\administrator",
                                #                                               "V!dya@#$2020"))
                                # res = json.loads(response.text)
                                # print("::::::::::::jjjjjjjjjjjjjjjjjjjjjjjjjjj:::::::::::::::",
                                #       len(rec.move_line_nosuggest_ids))
                                # for re in res['value']:
                                #     if re['Series_Code'] == str(rec.product_id.default_code):
                                #
                                #         if re['Last_No_Used'].find("-"):
                                #             num_ser = re['Last_No_Used']
                                print("QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ",self.table)
                                return http.request.render('vidya.enter_weight_page',
                                                           {'track_pro': False, 'by_sys': True, 'lot_name': num_ser,
                                                            'product': rec.description_picking, 'table': self.table})
                            else:
                                if pro_obj.packing_size:
                                    request.session['by_sys'] = False
                                    request.session['packing_size'] = 10
                                    pack_size_qty = float(rec.product_qty) / float(pro_obj.packing_size)
                                    self.remain = pack_size_qty - len(self.len_pro)
                                    return http.request.render('vidya.enter_weight_page',
                                                               {'by_sys': False, 'pack_size': 10, 'remain': self.remain,'lot_name': num_ser,
                                                                'product': rec.description_picking,
                                                                'table': self.table})
                                else:
                                    request.session['by_sys'] = False
                                    return http.request.render('vidya.enter_weight_page',
                                                               {'track_pro': False, 'by_sys': False,'lot_name': num_ser,
                                                                'product': rec.description_picking,
                                                                'table': self.table})

                        elif rec.product_id.tracking == "serial":
                            request.session['track_pro'] = True
                            if pro_obj.by_system == True:
                                request.session['by_sys'] = True
                                return http.request.render('vidya.enter_weight_page',
                                                           {'track_pro': True, 'by_sys': True,'lot_name': num_ser,
                                                            'product': rec.description_picking, 'table': self.table1})
                            else:
                                request.session['by_sys'] = False
                                return http.request.render('vidya.enter_weight_page',
                                                           {'track_pro': True, 'by_sys': False,'lot_name': num_ser,
                                                            'product': rec.description_picking, 'table': self.table1})
                        else:
                            request.session['track_pro'] = 5
                            return http.request.render('vidya.enter_weight_page',
                                                       {'track_pro': 5, 'product': rec.description_picking,'lot_name': num_ser,
                                                        'table': self.table})

            else:
                error = "This product does not exists."
                return http.request.render('vidya.select_product_page',
                                           {'error': error})

    @http.route('/enter_weight', website=True, auth="public", csrf=False, type='http', )
    def enter_weight(self, **kw):
        if not request.session.get('ser_list'):
            request.session['ser_list'] = []
            stock_picking = request.env['stock.picking'].sudo().search([('state', '=', 'assigned'), ('picking_type_id', '=', 1)])

            for line in stock_picking.move_ids_without_package.move_line_nosuggest_ids:
                request.session['ser_list'].append(line.lot_name)
        else:
            pass
        print("\n\n\n\nJaineel ::::::::  ",request.session)
        stock_pick_obj = request.env['stock.picking'].sudo().search([('id', '=', request.session['id'])])
        if kw.get('lot'):
           stock_move_line = request.env['stock.move.line'].sudo().search([('lot_name','=',kw['lot'])])
        user_obj = request.env['user.ip.address'].sudo().search([('name', '=', request.session['uid'])])
        pro_obj = request.env['product.template'].sudo().search([('name', '=', request.session['product'])])
        # try:

        for rec in stock_pick_obj.move_ids_without_package:
            self.pro_list.append(rec.product_id.name)

        pdf = None
        count = 0
        for rec in stock_pick_obj.move_ids_without_package:
            value1 = 0.0
            request.session['resub'] = value1
            pdf = None
            if request.session['product'] in self.pro_list:
                if rec.product_id.name == request.session['product']:
                    if rec.line_no == request.session['line_no']:
                        ################################ here the lot product weight scanning code start########################################################
                        if rec.product_id.tracking == "lot":
                            print("OOOOOOOOOOO***************************))))))))))))))))))", rec.line_no,request.session['line_no'])
                            ################################ tracking is by Lot and System generated lot number########################################################
                            if pro_obj.by_system == True:
                                if request.httprequest.method == "POST":
                                    print(">>WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW>>>>>>>>>>>>>",request.session['ser_list'])
                                    used = request.env['num.ser'].sudo().search(
                                        [('series_code', '=', pro_obj.default_code)])
                                    num_ser = used.last_number_used
                                    ################################ if product has tolerance then below code follow########################################################
                                    if rec.tolerance:

                                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",
                                              rec.tolerance)
                                        tol = (rec.tolerance)
                                        tolerance_obj = rec.product_uom_qty + ((rec.product_uom_qty * float(tol)) / 100)
                                        if (rec.quantity_done + (
                                                float(kw['we']) - float(kw['tel_we']))) > tolerance_obj:
                                            error = "You can't add more weights."
                                            return http.request.render('vidya.enter_weight_page',
                                                                       {'track_pro': False, 'by_sys': True,
                                                                        'swt_val': value1,'lot_name': num_ser,
                                                                        'product': rec.description_picking,
                                                                        'error': error, 'table': self.table})
                                        elif float(kw['we']) > float(kw['tel_we']):
                                                used = request.env['num.ser'].sudo().search([('series_code','=',pro_obj.default_code)])
                                                num_ser = used.last_number_used
                                                last_digit = num_ser.split("-")[-1]
                                                ser = int((num_ser.split("-")[-1])) + used.increment_by
                                                ser1 = str(ser).zfill(len(last_digit))
                                                print("KJJJGDHSDGSDSDGDFSDFDSFFFFADFDFFFFFF", ser1)
                                                move_obj_line = request.env['stock.move.line'].sudo().create({
                                                    'picking_id': stock_pick_obj.id,
                                                    'move_id': rec.id,
                                                    'location_id': 4,
                                                    'location_dest_id': 8,
                                                    'lot_name':  (num_ser.split("-")[0] + "-" + num_ser.split("-")[1] + "-" + ser1),
                                                    'product_uom_id': 1,
                                                    'product_id': rec.product_id.id,
                                                    'qty_done': float(kw['we']) - float(kw['tel_we']),
                                                    'company_id': 1,
                                                })
                                                used.write({
                                                    'last_number_used':move_obj_line.lot_name,

                                                })
                                                for move_line in stock_pick_obj.move_ids_without_package:
                                                    if move_line.product_id.name == request.session[
                                                        'product'] and move_line.line_no == request.session['line_no']:
                                                        self.table[move_line.product_id.name] = [
                                                            move_line.product_uom_qty,
                                                            abs(round(
                                                                move_line.product_uom_qty - move_line.quantity_done,
                                                                3)), request.session['unit']]
                                                # name = str(move_obj_line.product_id.name)
                                                # qty = str(move_obj_line.qty_done).encode('utf-8')
                                                # des = str("abc")
                                                # lot = str(move_obj_line.lot_name)
                                                name = str(move_obj_line.product_id.name)

                                                # qty = str(move_obj_line.qty_done).encode('utf-8')
                                                des = str(move_obj_line.product_id.description_purchase)
                                                lot = str(move_obj_line.lot_name)
                                                vendor = str(stock_pick_obj.partner_id.name)
                                                vendor = str(stock_pick_obj.partner_id.name)
                                                # printer code start from heree#####################
                                                user_obj = request.env['user.ip.address'].sudo().search(
                                                    [('name', '=', request.session['uid'])])
                                                pro_obj = request.env['product.template'].sudo().search(
                                                    [('name', '=', request.session['product'])])
                                                for i in range(int(kw['pr_qty'])):
                                                    from ipaddress import ip_address
                                                    import socket
                                                    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                                    ip_address = user_obj.printer_ip_address
                                                    print("::::::::::::::::::::::::::::::::::::::::::", ip_address,vendor)
                                                    port = 9100
                                                    try:
                                                        mysocket.connect((ip_address, port))
                                                        print("neleneleklekelekleklekelke;lekle",
                                                              name)  # connecting to host
                                                        # mysocket.send(
                                                        #     f'^XA^MMT^PW831^LL1205^LS0^FT671,607^A0B,45,45^FH\^FD{str(vendor)}^FS^FT561,606^A0B,45,45^FH\^FD{str(des)}^FS^FT677,976^A0B,56,55^FH\^FDVendor^FS^FT680,648^A0B,56,55^FH\^FD:^FS^FT566,980^A0B,56,45^FH\^FDItem Description^FS^FT569,653^A0B,56,45^FH\^FD:^FS^FT454,980^A0B,56,55^FH\^FDItem Code^FS^FT446,604^A0B,45,45^FH\^FD{str(name)}^FS^FT457,653^A0B,56,55^FH\^FD:^FS^FT131,769^BQN,2,10^FH\^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode(
                                                        #         'utf-8'))  # using bytes
                                                        # mysocket.close()  # closing connection

                                                        mysocket.send(
                                                            f'^XA^SZ2^JMA^MCY^PMN^PW580~JSN^JZY^LH0,0^LRN^XZ^XA^FT34,60^CI0^A0N,28,38^FDItem Code^FS^FT34,132^A0N,28,38^FDDescription^FS^FT34,204^A0N,28,38^FDVendorName^FS^FT269,60^A0N,28,38^FD:{str(name)}^FS^FT270,132^A0N,28,38^FD:{str(des)}^FS^FT270,204^A0N,28,38^FD:{str(vendor)}^FS^FO227,220^BQN,2,6^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode(
                                                                'utf-8'))
                                                        # using bytes
                                                        mysocket.close()  # closing connection

                                                    except:
                                                        print("Error with the connection")
                                                # printer code end from here##################
                                                return http.request.render('vidya.enter_weight_page',
                                                                           {'track_pro': False, 'by_sys': True,
                                                                            'swt_val': value1,'lot_name': num_ser,
                                                                            'product': rec.description_picking,
                                                                            'table': self.table})
                                        else:
                                            error = "Tel weight must be less then product actual weight."
                                            return http.request.render('vidya.enter_weight_page',
                                                                       {'track_pro': False, 'by_sys': True,
                                                                        'swt_val': value1,'lot_name': num_ser,
                                                                        'product': rec.description_picking,
                                                                        'table': self.table, 'error': error})

                                    ################################ if product has not tolerance then below code follow########################################################
                                    elif rec.tolerance == False or rec.tolerance == '':
                                        print("646547484857447474")

                                        if float(kw['we']) > float(kw['tel_we']):
                                            print(">===================>>>>>>>>>>>>>", rec.tolerance)
                                            if rec.product_uom_qty < rec.quantity_done + ((float(kw['we']) - float(kw['tel_we']))):
                                                print("fggggggggggggggggggggggggnnnnnnnnnnnnnnnnnnnnnnnnnnnnn",
                                                      self.table)
                                                error = f"You can't add more than {self.table[rec.product_id.name][1]} quantity"
                                                return http.request.render('vidya.enter_weight_page',
                                                                           {'track_pro': False, 'by_sys': True,
                                                                            'lot_name': num_ser, 'error': error,
                                                                            'swt_val': value1,
                                                                            'product': rec.description_picking,
                                                                            'table': self.table})
                                            else:
                                                print(">22222222222222>>>>>>>>>>>>>",rec.tolerance)
                                                used = request.env['num.ser'].sudo().search(
                                                    [('series_code', '=', pro_obj.default_code)])
                                                num_ser = used.last_number_used
                                                # num_ser = pro_obj.last_number_used
                                                last_digit = num_ser.split("-")[-1]
                                                ser = int((num_ser.split("-")[-1])) + used.increment_by
                                                ser1 = str(ser).zfill(len(last_digit))
                                                print("KJJJGDHSDGSDSDGDFSDFDSFFFFADFDFFFFFF", ser1)
                                                move_obj_line = request.env['stock.move.line'].sudo().create({
                                                    'picking_id': stock_pick_obj.id,
                                                    'move_id': rec.id,
                                                    'location_id': 4,
                                                    'location_dest_id': 8,
                                                    #'lot_name':str(rec.product_id.name) + str(len(rec.move_line_nosuggest_ids)),
                                                    'lot_name': (num_ser.split("-")[0] + "-" + num_ser.split("-")[1] + "-" + ser1),
                                                    'product_uom_id': 1,
                                                    'product_id': rec.product_id.id,
                                                    'qty_done': float(kw['we']) - float(kw['tel_we']),
                                                    'company_id': 1,
                                                })
                                                used.write({
                                                    'last_number_used': move_obj_line.lot_name,

                                                })
                                                for move_line in stock_pick_obj.move_ids_without_package:
                                                    if move_line.product_id.name == request.session[
                                                        'product'] and move_line.line_no == request.session[
                                                        'line_no']:
                                                        self.table[move_line.product_id.name] = [
                                                            move_line.product_uom_qty,
                                                            abs(round(
                                                                move_line.product_uom_qty - move_line.quantity_done,
                                                                3)), request.session['unit']]

                                                print(
                                                    "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM",
                                                    self.table)
                                                name = str(move_obj_line.product_id.name)

                                                # qty = str(move_obj_line.qty_done).encode('utf-8')
                                                des = str(move_obj_line.product_id.description_purchase)
                                                lot = str(move_obj_line.lot_name)
                                                vendor = str(stock_pick_obj.partner_id.name)
                                                print("JJJJJJJJJJJJJJJJJJJJJJJJJJJJJ",name,des,lot,vendor)
                                                # printer code start from heree#####################
                                                # self.connect_printer()
                                                user_obj = request.env['user.ip.address'].sudo().search(
                                                    [('name', '=', request.session['uid'])])
                                                pro_obj = request.env['product.template'].sudo().search(
                                                    [('name', '=', request.session['product'])])
                                                for i in range(int(kw['pr_qty'])):
                                                    from ipaddress import ip_address
                                                    import socket
                                                    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                                    ip_address = user_obj.printer_ip_address
                                                    print("::::::::::::::::::::::::::::::::::::::::::",
                                                          ip_address)
                                                    port = 9100
                                                    try:
                                                        mysocket.connect((ip_address, port))

                                                        print("neleneleklekelekleklekelke;lekle",
                                                              name)  # connecting to host

                                                        mysocket.send(
                                                            f'^XA^SZ2^JMA^MCY^PMN^PW580~JSN^JZY^LH0,0^LRN^XZ^XA^FT34,60^CI0^A0N,28,38^FDItem Code^FS^FT34,132^A0N,28,38^FDDescription^FS^FT34,204^A0N,28,38^FDVendorName^FS^FT269,60^A0N,28,38^FD:{str(name)}^FS^FT270,132^A0N,28,38^FD:{str(des)}^FS^FT270,204^A0N,28,38^FD:{str(vendor)}^FS^FO227,220^BQN,2,6^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode('utf-8'))
                                                            # f'^XA^SZ2^JMA^MCY^PMN^PW580~JSN^JZY^LH0,0^LRN^XZ^XA^FT34,60^CI0^A0N,28,38^FDItem Code^FS^FT34,132^A0N,28,38^FDDescription^FS^FT34,204^A0N,28,38^FDVendor Name^FS^FT292,204^A0N,28,38^FDVendor Name_V^FS^FT269,60^A0N,28,38^FD:{str(name)}^FS^FT270,132^A0N,28,38^FD:{str(des)}^FS^FT270,204^A0N,28,38^FD:{str(vendor)}^FS^FT292,60^A0N,28,38^
                                                        # FDItem Code_V^FS^FT293,132^A0N,28,38^FDDescription_V^FS^FO227,220^BQN,2,6^FDLA,LOT/SR^FS^PQ1,0,1,Y^XZ'.encode(
                                                            #     'utf-8'))
                                                        mysocket.close()  # closing connection
                                                        print("YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYy")
                                                    except:
                                                        print("Error with the connection")
                                                    # printer code end from here##################
                                                return http.request.render('vidya.enter_weight_page',
                                                                           {'track_pro': False, 'by_sys': True,
                                                                            'lot_name': num_ser,
                                                                            'swt_val': value1,
                                                                            'product': rec.description_picking,
                                                                            'table': self.table})


                                        else:
                                            error = "Tel weight must be less then product actual weight."
                                            return http.request.render('vidya.enter_weight_page',
                                                                       {'track_pro': False, 'by_sys': True,
                                                                        'lot_name': num_ser,
                                                                        'swt_val': value1,
                                                                        'product': rec.description_picking,
                                                                        'table': self.table, 'error': error})


                            ################################ tracking is by Lot and user generated lot number########################################################
                            else:
                                if request.httprequest.method == "POST":
                                    stock_lot = request.env['stock.lot'].sudo().search(
                                        [('name', '=', kw['lot'])])
                                    used = request.env['num.ser'].sudo().search(
                                        [('series_code', '=', pro_obj.default_code)])
                                    num_ser = used.last_number_used
                                    ################################ tracking is by Lot and user generated lot number and tolerance mention########################################################
                                    if rec.tolerance:
                                            tol = (rec.tolerance)
                                            tolerance_obj = rec.product_uom_qty + ((rec.product_uom_qty * float(tol)) / 100)

                                        # if kw['lot'] in request.session['ser_list'] or stock_lot and request.session[
                                        #             'product'] != stock_lot.product_id.name:
                                        #     error = "Serial/Lot number exits"
                                        #     return http.request.render('vidya.enter_weight_page',
                                        #                                {'track_pro': False, 'by_sys': False,
                                        #                                 'swt_val': value1,
                                        #                                 'product': rec.description_picking,
                                        #                                 'error': error, 'table': self.table})
                                        # else:
                                            print("LLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBB")
                                            if (rec.quantity_done + float(kw['we'])) > tolerance_obj:
                                                error = "You can't add more weights."
                                                return http.request.render('vidya.enter_weight_page',
                                                                           {'track_pro': False, 'by_sys': False,
                                                                            'swt_val': value1,'lot_name': num_ser,
                                                                            'product': rec.description_picking,
                                                                            'error': error, 'table': self.table})

                                            elif float(kw['we']) > float(kw['tel_we']):
                                                print("7777777777777777777777777777777777",self.ser_list1)
                                                if self.ser_list1 == {} and stock_lot and request.session[
                                                    'product'] != stock_lot.product_id.name and kw['lot'] in request.session['ser_list']:
                                                    error = "This Lot number already exits"
                                                    return http.request.render('vidya.enter_weight_page',
                                                                               {'track_pro': False, 'by_sys': False,
                                                                                'swt_val': value1,'lot_name': num_ser,
                                                                                'product': rec.description_picking,
                                                                                'table': self.table,'error': error})
                                                elif self.ser_list1 == {}:
                                                    move_obj_line = request.env['stock.move.line'].sudo().create({
                                                        'picking_id': stock_pick_obj.id,
                                                        'move_id': rec.id,
                                                        'location_id': 4,
                                                        'location_dest_id': 8,
                                                        'lot_name': kw['lot'],
                                                        'product_uom_id': 1,
                                                        'product_id': rec.product_id.id,
                                                        'qty_done': float(kw['we']) - float(kw['tel_we']),
                                                        'company_id': 1,
                                                    })

                                                    for re in stock_pick_obj.move_ids_without_package.move_line_nosuggest_ids:
                                                        request.session['ser_list'].append(re.lot_name)
                                                        print("///////////////////////////////////////////",
                                                              request.session['ser_list'])

                                                    for re in stock_pick_obj.move_ids_without_package.move_line_nosuggest_ids:
                                                        if re.product_id.name in self.ser_list1:
                                                            self.ser_list1[re.product_id.name].append(
                                                                re.lot_name)
                                                        else:
                                                            self.ser_list1[re.product_id.name] = [
                                                                re.lot_name]
                                                            print("4444477777777777777777777777777777",
                                                                  self.ser_list1[re.product_id.name])

                                                    name = str(move_obj_line.product_id.name)
                                                    des = str(move_obj_line.product_id.description_purchase)
                                                    lot = str(move_obj_line.lot_name)
                                                    vendor = str(stock_pick_obj.partner_id.name)
                                                    for move_line in stock_pick_obj.move_ids_without_package:
                                                        if move_line.product_id.name == request.session[
                                                            'product'] and move_line.line_no == request.session[
                                                            'line_no']:
                                                            print("KKKKKKKKKKKKKKKKBBBBBBBBBBBBBBBBBBBBB")
                                                            # self.table[move_line.product_id.name] = [
                                                            #     move_line.product_uom_qty, round((move_line.product_uom_qty - move_line.quantity_done) * (-1), 3),
                                                            #     request.session['unit']]
                                                            self.table[move_line.product_id.name] = [
                                                                move_line.product_uom_qty,
                                                                abs(round(
                                                                    move_line.product_uom_qty - move_line.quantity_done,
                                                                    3)), request.session['unit']]

                                                    # Printer code start from here#######################################

                                                    user_obj = request.env['user.ip.address'].sudo().search(
                                                        [('name', '=', request.session['uid'])])
                                                    pro_obj = request.env['product.template'].sudo().search(
                                                        [('name', '=', request.session['product'])])
                                                    for i in range(int(kw['pr_qty'])):
                                                        from ipaddress import ip_address
                                                        import socket
                                                        mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                                        ip_address = user_obj.printer_ip_address
                                                        print("::::::::::::::::::::::::::::::::::::::::::", ip_address)
                                                        port = 9100
                                                        try:
                                                            mysocket.connect((ip_address, port))
                                                            print("neleneleklekelekleklekelke;lekle",
                                                                  name)  # connecting to host
                                                            # mysocket.send(
                                                            #     f'^XA^MMT^PW831^LL1205^LS0^FT671,607^A0B,45,45^FH\^FD{str(vendor)}^FS^FT561,606^A0B,45,45^FH\^FD{str(des)}^FS^FT677,976^A0B,56,55^FH\^FDVendor^FS^FT680,648^A0B,56,55^FH\^FD:^FS^FT566,980^A0B,56,45^FH\^FDItem Description^FS^FT569,653^A0B,56,45^FH\^FD:^FS^FT454,980^A0B,56,55^FH\^FDItem Code^FS^FT446,604^A0B,45,45^FH\^FD{str(name)}^FS^FT457,653^A0B,56,55^FH\^FD:^FS^FT131,769^BQN,2,10^FH\^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode(
                                                            #         'utf-8'))  # using bytes
                                                            # mysocket.close()  # closing connection

                                                            mysocket.send(
                                                                 f'^XA^SZ2^JMA^MCY^PMN^PW580~JSN^JZY^LH0,0^LRN^XZ^XA^FT34,60^CI0^A0N,28,38^FDItem Code^FS^FT34,132^A0N,28,38^FDDescription^FS^FT34,204^A0N,28,38^FDVendorName^FS^FT269,60^A0N,28,38^FD:{str(name)}^FS^FT270,132^A0N,28,38^FD:{str(des)}^FS^FT270,204^A0N,28,38^FD:{str(vendor)}^FS^FO227,220^BQN,2,6^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode('utf-8'))  # using bytes
                                                            mysocket.close()  # closing connection

                                                        except:
                                                            print("Error with the connection")

                                                    # Printer code end from here#######################################

                                                    return http.request.render('vidya.enter_weight_page',
                                                                               {'track_pro': False, 'by_sys': False,
                                                                                'swt_val': value1,'lot_name': num_ser,
                                                                                'product': rec.description_picking,
                                                                                'table': self.table})
                                                else:
                                                        print("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT",stock_move_line)
                                                        if len(stock_move_line) == 0:
                                                            move_obj_line = request.env[
                                                                'stock.move.line'].sudo().create(
                                                                {'picking_id': stock_pick_obj.id, 'move_id': rec.id,
                                                                    'location_id': 4, 'location_dest_id': 8,
                                                                     'lot_name': kw['lot'], 'product_uom_id': 1,
                                                                    'product_id': rec.product_id.id,
                                                                    'qty_done': float(kw['we']) - float(kw['tel_we']),
                                                                    'company_id': 1, })
                                                            print(">>>>>>>>>>>>>>MMMMMMMMMMMMMMMMMMMMMMMMMMMM",
                                                                  move_obj_line)


                                                            for re in stock_pick_obj.move_ids_without_package.move_line_nosuggest_ids:
                                                                request.session['ser_list'].append(re.lot_name)


                                                            for re in stock_pick_obj.move_ids_without_package.move_line_nosuggest_ids:
                                                                if re.product_id.name in self.ser_list1:
                                                                    self.ser_list1[re.product_id.name].append(
                                                                        re.lot_name)
                                                                else:
                                                                    self.ser_list1[re.product_id.name] = [re.lot_name]

                                                            name = str(move_obj_line.product_id.name)
                                                            des = str(move_obj_line.product_id.description_purchase)
                                                            lot = str(move_obj_line.lot_name)
                                                            vendor = str(stock_pick_obj.partner_id.name)
                                                            for move_line in stock_pick_obj.move_ids_without_package:
                                                                if move_line.product_id.name == request.session[
                                                                    'product'] and move_line.line_no == request.session[
                                                                    'line_no']:
                                                                    print("111111111111111111111111111111111111111111",
                                                                          self.table)
                                                                    # self.table[move_line.product_id.name] = [
                                                                    #     move_line.product_uom_qty, round((
                                                                    #                                             move_line.product_uom_qty - move_line.quantity_done) * (
                                                                    #                                          -1), 3),
                                                                    #     request.session['unit']]
                                                                    self.table[move_line.product_id.name] = [
                                                                        move_line.product_uom_qty, abs(round(
                                                                            move_line.product_uom_qty - move_line.quantity_done,
                                                                            3)), request.session['unit']]

                                                            # Printer code start from here#######################################

                                                            user_obj = request.env['user.ip.address'].sudo().search(
                                                                [('name', '=', request.session['uid'])])
                                                            pro_obj = request.env['product.template'].sudo().search(
                                                                [('name', '=', request.session['product'])])
                                                            for i in range(int(kw['pr_qty'])):
                                                                from ipaddress import ip_address
                                                                import socket
                                                                mysocket = socket.socket(socket.AF_INET,
                                                                                         socket.SOCK_STREAM)
                                                                ip_address = user_obj.printer_ip_address
                                                                print("::::::::::::::::::::::::::::::::::::::::::",
                                                                      ip_address)
                                                                port = 9100
                                                                try:
                                                                    mysocket.connect((ip_address, port))
                                                                    print("neleneleklekelekleklekelke;lekle",
                                                                          name)  # connecting to host
                                                                    # mysocket.send(
                                                                    #     f'^XA^MMT^PW831^LL1205^LS0^FT671,607^A0B,45,45^FH\^FD{str(vendor)}^FS^FT561,606^A0B,45,45^FH\^FD{str(des)}^FS^FT677,976^A0B,56,55^FH\^FDVendor^FS^FT680,648^A0B,56,55^FH\^FD:^FS^FT566,980^A0B,56,45^FH\^FDItem Description^FS^FT569,653^A0B,56,45^FH\^FD:^FS^FT454,980^A0B,56,55^FH\^FDItem Code^FS^FT446,604^A0B,45,45^FH\^FD{str(name)}^FS^FT457,653^A0B,56,55^FH\^FD:^FS^FT131,769^BQN,2,10^FH\^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode(
                                                                    #         'utf-8'))  # using bytes
                                                                    # mysocket.close()  # closing connection

                                                                    mysocket.send(
                                                                        f'^XA^SZ2^JMA^MCY^PMN^PW580~JSN^JZY^LH0,0^LRN^XZ^XA^FT34,60^CI0^A0N,28,38^FDItem Code^FS^FT34,132^A0N,28,38^FDDescription^FS^FT34,204^A0N,28,38^FDVendorName^FS^FT269,60^A0N,28,38^FD:{str(name)}^FS^FT270,132^A0N,28,38^FD:{str(des)}^FS^FT270,204^A0N,28,38^FD:{str(vendor)}^FS^FO227,220^BQN,2,6^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode(
                                                                            'utf-8'))  # using bytes
                                                                    mysocket.close()  # closing connection


                                                                except:
                                                                    print("Error with the connection")

                                                            # Printer code end from here#######################################

                                                            return http.request.render('vidya.enter_weight_page',
                                                                                       {'track_pro': False,
                                                                                        'by_sys': False,'lot_name': num_ser,
                                                                                        'swt_val': value1,
                                                                                        'product': rec.description_picking,
                                                                                        'table': self.table})
                                                        else:
                                                            for re in stock_move_line:
                                                                print("KKKKKKKKKKKKKKKKKKKKKKKKKK",
                                                                      re)
                                                                if re.product_id.name == request.session['product']:
                                                                    move_obj_line = request.env['stock.move.line'].sudo().create({
                                                                        'picking_id': stock_pick_obj.id,
                                                                        'move_id': rec.id,
                                                                        'location_id': 4,
                                                                        'location_dest_id': 8,
                                                                        'lot_name': kw['lot'],
                                                                        'product_uom_id': 1,
                                                                        'product_id': rec.product_id.id,
                                                                        'qty_done': float(kw['we']) - float(kw['tel_we']),
                                                                        'company_id': 1,
                                                                    })
                                                                    print("hello herlojhgfjhsegru7fothjdguydtsafjhvgiufyiuxvh",move_obj_line.lot_name)

                                                                    for re in stock_pick_obj.move_ids_without_package.move_line_nosuggest_ids:
                                                                        request.session['ser_list'].append(
                                                                            re.lot_name)
                                                                        print("oooooooooooooooooooooooooo",
                                                                              request.session['ser_list'])

                                                                    for re in stock_pick_obj.move_ids_without_package.move_line_nosuggest_ids:
                                                                        if re.product_id.name in self.ser_list1:
                                                                            self.ser_list1[
                                                                                re.product_id.name].append(
                                                                                re.lot_name)
                                                                        else:
                                                                            self.ser_list1[
                                                                                re.product_id.name] = [
                                                                                re.lot_name]

                                                                    name = str(move_obj_line.product_id.name)
                                                                    des = str(move_obj_line.product_id.description_purchase)
                                                                    lot = str(move_obj_line.lot_name)
                                                                    vendor = str(stock_pick_obj.partner_id.name)
                                                                    for move_line in stock_pick_obj.move_ids_without_package:
                                                                        if move_line.product_id.name == request.session[
                                                                            'product'] and move_line.line_no == request.session['line_no']:
                                                                            print("111111111111111111111111111111111111111111",self.table)
                                                                            # self.table[move_line.product_id.name] = [
                                                                            #     move_line.product_uom_qty, round((
                                                                            #                                             move_line.product_uom_qty - move_line.quantity_done) * (
                                                                            #                                          -1), 3),
                                                                            #     request.session['unit']]
                                                                            self.table[move_line.product_id.name] = [
                                                                                move_line.product_uom_qty,
                                                                                abs(round(
                                                                                    move_line.product_uom_qty - move_line.quantity_done,
                                                                                    3)), request.session['unit']]

                                                                    # Printer code start from here#######################################

                                                                    user_obj = request.env['user.ip.address'].sudo().search(
                                                                        [('name', '=', request.session['uid'])])
                                                                    pro_obj = request.env['product.template'].sudo().search(
                                                                        [('name', '=', request.session['product'])])
                                                                    for i in range(int(kw['pr_qty'])):
                                                                        from ipaddress import ip_address
                                                                        import socket
                                                                        mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                                                        ip_address = user_obj.printer_ip_address
                                                                        print("::::::::::::::::::::::::::::::::::::::::::", ip_address)
                                                                        port = 9100
                                                                        try:
                                                                            mysocket.connect((ip_address, port))
                                                                            print("neleneleklekelekleklekelke;lekle",
                                                                                  name)  # connecting to host
                                                                            # mysocket.send(
                                                                            #     f'^XA^MMT^PW831^LL1205^LS0^FT671,607^A0B,45,45^FH\^FD{str(vendor)}^FS^FT561,606^A0B,45,45^FH\^FD{str(des)}^FS^FT677,976^A0B,56,55^FH\^FDVendor^FS^FT680,648^A0B,56,55^FH\^FD:^FS^FT566,980^A0B,56,45^FH\^FDItem Description^FS^FT569,653^A0B,56,45^FH\^FD:^FS^FT454,980^A0B,56,55^FH\^FDItem Code^FS^FT446,604^A0B,45,45^FH\^FD{str(name)}^FS^FT457,653^A0B,56,55^FH\^FD:^FS^FT131,769^BQN,2,10^FH\^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode(
                                                                            #         'utf-8'))  # using bytes
                                                                            # mysocket.close()  # closing connection

                                                                            mysocket.send(
                                                                                 f'^XA^SZ2^JMA^MCY^PMN^PW580~JSN^JZY^LH0,0^LRN^XZ^XA^FT34,60^CI0^A0N,28,38^FDItem Code^FS^FT34,132^A0N,28,38^FDDescription^FS^FT34,204^A0N,28,38^FDVendorName^FS^FT269,60^A0N,28,38^FD:{str(name)}^FS^FT270,132^A0N,28,38^FD:{str(des)}^FS^FT270,204^A0N,28,38^FD:{str(vendor)}^FS^FO227,220^BQN,2,6^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode('utf-8'))  # using bytes
                                                                            mysocket.close()  # closing connection


                                                                        except:
                                                                            print("Error with the connection")

                                                                    # Printer code end from here#######################################

                                                                    return http.request.render('vidya.enter_weight_page',
                                                                                               {'track_pro': False, 'by_sys': False,
                                                                                                'swt_val': value1,'lot_name': num_ser,
                                                                                                'product': rec.description_picking,
                                                                                                'table': self.table})
                                                                else:
                                                                    error = "This lot number already exits."
                                                                    return http.request.render('vidya.enter_weight_page',
                                                                                               {'track_pro': False,
                                                                                                'by_sys': False,
                                                                                                'swt_val': value1,
                                                                                                'product': rec.description_picking,
                                                                                                'table': self.table,'error': error})

                                            else:
                                                error = "Tel weight must be less then product actual weight."
                                                return http.request.render('vidya.enter_weight_page',
                                                                           {'track_pro': False, 'by_sys': False,
                                                                            'swt_val': value1,'lot_name': num_ser,
                                                                            'product': rec.description_picking,
                                                                            'table': self.table, 'error': error})



                                    ################################ tracking is by Lot and user generated lot number and tolerance not mention########################################################
                                    else:
                                        ################################ tracking is by Lot and user generated lot number and Packing size mention########################################################
                                        if pro_obj.packing_size:
                                            if rec.product_qty == rec.quantity_done:
                                                return http.request.render('vidya.thank_you_page',
                                                                           {'track_pro': True, 'by_sys': False,
                                                                            'pack_size': 10,'lot_name': num_ser,
                                                                            'table': self.table1})
                                            else:
                                                pack_size_qty = float(rec.product_qty) / float(pro_obj.packing_size)
                                                move_obj_line = request.env['stock.move.line'].sudo().create({
                                                    'picking_id': stock_pick_obj.id,
                                                    'move_id': rec.id,
                                                    'location_id': 4,
                                                    'location_dest_id': 8,
                                                    'lot_name': kw['lot'],
                                                    'product_uom_id': 1,
                                                    'product_id': rec.product_id.id,
                                                    'qty_done': pro_obj.packing_size,
                                                    'company_id': 1,
                                                })

                                                name = str(move_obj_line.product_id.name)

                                                # qty = str(move_obj_line.qty_done).encode('utf-8')
                                                des = str(move_obj_line.product_id.description_purchase)
                                                lot = str(move_obj_line.lot_name)
                                                vendor = str(stock_pick_obj.partner_id.name)
                                                re_list = []
                                                for re in stock_pick_obj.move_ids_without_package.move_line_nosuggest_ids:
                                                    if re.product_id.name == request.session['product']:
                                                        re_list.append(re.lot_name)
                                                re = pack_size_qty - len(re_list)
                                                user_obj = request.env['user.ip.address'].sudo().search(
                                                    [('name', '=', request.session['uid'])])
                                                pro_obj = request.env['product.template'].sudo().search(
                                                    [('name', '=', request.session['product'])])
                                                for i in range(int(kw['pr_qty'])):
                                                    from ipaddress import ip_address
                                                    import socket
                                                    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                                    ip_address = user_obj.printer_ip_address
                                                    print("::::::::::::::::::::::::::::::::::::::::::", ip_address)
                                                    port = 9100
                                                    try:
                                                        mysocket.connect((ip_address, port))
                                                        print("neleneleklekelekleklekelke;lekle",
                                                              name)  # connecting to host

                                                        mysocket.send(
                                                             f'^XA^SZ2^JMA^MCY^PMN^PW580~JSN^JZY^LH0,0^LRN^XZ^XA^FT34,60^CI0^A0N,28,38^FDItem Code^FS^FT34,132^A0N,28,38^FDDescription^FS^FT34,204^A0N,28,38^FDVendorName^FS^FT269,60^A0N,28,38^FD:{str(name)}^FS^FT270,132^A0N,28,38^FD:{str(des)}^FS^FT270,204^A0N,28,38^FD:{str(vendor)}^FS^FO227,220^BQN,2,6^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode('utf-8'))  # using bytes
                                                        mysocket.close()  # closing connection



                                                    except:
                                                        print("Error with the connection")
                                                return http.request.render('vidya.enter_weight_page',
                                                                           {'by_sys': False, 'pack_size': 10,
                                                                            'product': rec.description_picking,'lot_name': num_ser,
                                                                            'remain': re})
                                        ################################ tracking is by Lot and user generated lot number and tolerance not mention########################################################
                                        elif rec.tolerance == False or rec.tolerance == '':

                                            if float(kw['we']) > float(kw['tel_we']):
                                                if len(rec.move_line_nosuggest_ids) == 0:
                                                    if rec.product_uom_qty < ( (float(kw['we']) - float(kw['tel_we']))):
                                                        error = f"You can't add more than {self.table[rec.product_id.name][1]} quantity"
                                                        return http.request.render('vidya.enter_weight_page',
                                                                                   {'track_pro': False,
                                                                                    'by_sys': False,
                                                                                    'swt_val': value1,
                                                                                    'product': rec.description_picking,'lot_name': num_ser,
                                                                                    'table': self.table,
                                                                                    'error': error})
                                                    else:
                                                        print("stock production lot and dictionary", self.ser_list1,
                                                              stock_lot)
                                                        if self.ser_list1 == {} and stock_lot and kw['lot'] in request.session['ser_list'] and request.session['product'] != stock_lot.product_id.name:
                                                            error = "This Lot number already exits"
                                                            return http.request.render('vidya.enter_weight_page',
                                                                                       {'track_pro': False,
                                                                                        'by_sys': False,
                                                                                        'swt_val': value1,'lot_name': num_ser,
                                                                                        'product': rec.description_picking,
                                                                                        'table': self.table,'error':error})
                                                        elif self.ser_list1 == {}:
                                                            print("QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ",self.ser_list1)
                                                            move_obj_line = request.env[
                                                                'stock.move.line'].sudo().create({
                                                                'picking_id': stock_pick_obj.id,
                                                                'move_id': rec.id,
                                                                'location_id': 4,
                                                                'location_dest_id': 8,
                                                                'lot_name': kw['lot'],
                                                                'product_uom_id': 1,
                                                                'product_id': rec.product_id.id,
                                                                'qty_done': float(kw['we']) - float(kw['tel_we']),
                                                                'company_id': 1,
                                                            })
                                                            for re in stock_pick_obj.move_ids_without_package.move_line_nosuggest_ids:
                                                                request.session['ser_list'].append(re.lot_name)


                                                            for re in stock_pick_obj.move_ids_without_package.move_line_nosuggest_ids:
                                                                if re.product_id.name in self.ser_list1:
                                                                    self.ser_list1[re.product_id.name].append(
                                                                        re.lot_name)
                                                                else:
                                                                    self.ser_list1[re.product_id.name] = [
                                                                        re.lot_name]
                                                                    print("4444477777777777777777777777777777",
                                                                      self.ser_list1[re.product_id.name])
                                                            name = str(move_obj_line.product_id.name)

                                                            # qty = str(move_obj_line.qty_done).encode('utf-8')
                                                            des = str(move_obj_line.product_id.description_purchase)
                                                            lot = str(move_obj_line.lot_name)
                                                            vendor = str(stock_pick_obj.partner_id.name)

                                                            for move_line in stock_pick_obj.move_ids_without_package:
                                                                if move_line.product_id.name == request.session[
                                                                    'product'] and move_line.line_no == \
                                                                        request.session['line_no']:
                                                                    self.table[move_line.product_id.name] = [
                                                                        move_line.product_uom_qty,
                                                                        abs(round(
                                                                            move_line.product_uom_qty - move_line.quantity_done,
                                                                            3)), request.session['unit']]

                                                            # Printer code start from here#######################################
                                                            user_obj = request.env['user.ip.address'].sudo().search(
                                                                [('name', '=', request.session['uid'])])
                                                            pro_obj = request.env['product.template'].sudo().search(
                                                                [('name', '=', request.session['product'])])
                                                            for i in range(int(kw['pr_qty'])):
                                                                from ipaddress import ip_address
                                                                import socket
                                                                mysocket = socket.socket(socket.AF_INET,
                                                                                         socket.SOCK_STREAM)
                                                                ip_address = user_obj.printer_ip_address
                                                                print("::::::::::::::::::::::::::::::::::::::::::",
                                                                      ip_address)
                                                                port = 9100
                                                                try:
                                                                    mysocket.connect((ip_address, port))
                                                                    print("neleneleklekelekleklekelke;lekle",
                                                                          name)  # connecting to host

                                                                    mysocket.send(
                                                                         f'^XA^SZ2^JMA^MCY^PMN^PW580~JSN^JZY^LH0,0^LRN^XZ^XA^FT34,60^CI0^A0N,28,38^FDItem Code^FS^FT34,132^A0N,28,38^FDDescription^FS^FT34,204^A0N,28,38^FDVendorName^FS^FT269,60^A0N,28,38^FD:{str(name)}^FS^FT270,132^A0N,28,38^FD:{str(des)}^FS^FT270,204^A0N,28,38^FD:{str(vendor)}^FS^FO227,220^BQN,2,6^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode('utf-8'))  # using bytes
                                                                    mysocket.close()  # closing connection

                                                                except:
                                                                    print("Error with the connection")

                                                            # Printer code end from here#######################################

                                                            return http.request.render('vidya.enter_weight_page',
                                                                                       {'track_pro': False,
                                                                                        'by_sys': False,
                                                                                        'swt_val': value1,'lot_name': num_ser,
                                                                                        'product': rec.description_picking,
                                                                                        'table': self.table})
                                                        else:
                                                            print("1st tiome enter lot number>>>>>>>>>>>>>>>>>>>", self.ser_list1,len(stock_move_line))
                                                            for product, lot in self.ser_list1.items():
                                                                if len(stock_move_line) == 0:
                                                                    move_obj_line = request.env[
                                                                        'stock.move.line'].sudo().create(
                                                                        {'picking_id': stock_pick_obj.id,
                                                                            'move_id': rec.id, 'location_id': 4,
                                                                            'location_dest_id': 8,
                                                                             'lot_name': kw['lot'], 'product_uom_id': 1,
                                                                            'product_id': rec.product_id.id,
                                                                            'qty_done': float(kw['we']) - float(
                                                                                kw['tel_we']), 'company_id': 1, })
                                                                    for re in stock_pick_obj.move_ids_without_package.move_line_nosuggest_ids:
                                                                        request.session['ser_list'].append(re.lot_name)


                                                                    for re in stock_pick_obj.move_ids_without_package.move_line_nosuggest_ids:
                                                                        if re.product_id.name in self.ser_list1:
                                                                            self.ser_list1[re.product_id.name].append(
                                                                                re.lot_name)
                                                                        else:
                                                                            self.ser_list1[re.product_id.name] = [
                                                                                re.lot_name]
                                                                    name = str(move_obj_line.product_id.name)

                                                                    # qty = str(move_obj_line.qty_done).encode('utf-8')
                                                                    des = str(
                                                                        move_obj_line.product_id.description_purchase)
                                                                    lot = str(move_obj_line.lot_name)
                                                                    vendor = str(stock_pick_obj.partner_id.name)

                                                                    for move_line in stock_pick_obj.move_ids_without_package:
                                                                        if move_line.product_id.name == request.session[
                                                                            'product'] and move_line.line_no == \
                                                                                request.session['line_no']:
                                                                            self.table[move_line.product_id.name] = [
                                                                                move_line.product_uom_qty, round(
                                                                                    move_line.product_uom_qty - move_line.quantity_done,
                                                                                    3), request.session['unit']]

                                                                    # Printer code start from here#######################################
                                                                    user_obj = request.env[
                                                                        'user.ip.address'].sudo().search(
                                                                        [('name', '=', request.session['uid'])])
                                                                    pro_obj = request.env[
                                                                        'product.template'].sudo().search(
                                                                        [('name', '=', request.session['product'])])
                                                                    for i in range(int(kw['pr_qty'])):
                                                                        from ipaddress import ip_address
                                                                        import socket
                                                                        mysocket = socket.socket(socket.AF_INET,
                                                                            socket.SOCK_STREAM)
                                                                        ip_address = user_obj.printer_ip_address
                                                                        print(
                                                                            "::::::::::::::::::::::::::::::::::::::::::",
                                                                            ip_address)
                                                                        port = 9100
                                                                        try:
                                                                            mysocket.connect((ip_address, port))
                                                                            print("neleneleklekelekleklekelke;lekle",
                                                                                name)  # connecting to host
                                                                            # mysocket.send(
                                                                            #     f'^XA^MMT^PW831^LL1205^LS0^FT671,607^A0B,45,45^FH\^FD{str(vendor)}^FS^FT561,606^A0B,45,45^FH\^FD{str(des)}^FS^FT677,976^A0B,56,55^FH\^FDVendor^FS^FT680,648^A0B,56,55^FH\^FD:^FS^FT566,980^A0B,56,45^FH\^FDItem Description^FS^FT569,653^A0B,56,45^FH\^FD:^FS^FT454,980^A0B,56,55^FH\^FDItem Code^FS^FT446,604^A0B,45,45^FH\^FD{str(name)}^FS^FT457,653^A0B,56,55^FH\^FD:^FS^FT131,769^BQN,2,10^FH\^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode(
                                                                            #         'utf-8'))  # using bytes
                                                                            # mysocket.close()  # closing connection

                                                                            mysocket.send(
                                                                                f'^XA^SZ2^JMA^MCY^PMN^PW580~JSN^JZY^LH0,0^LRN^XZ^XA^FT34,60^CI0^A0N,28,38^FDItem Code^FS^FT34,132^A0N,28,38^FDDescription^FS^FT34,204^A0N,28,38^FDVendorName^FS^FT269,60^A0N,28,38^FD:{str(name)}^FS^FT270,132^A0N,28,38^FD:{str(des)}^FS^FT270,204^A0N,28,38^FD:{str(vendor)}^FS^FO227,220^BQN,2,6^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode(
                                                                                    'utf-8'))  # using bytes
                                                                            mysocket.close()  # closing connection


                                                                        except:
                                                                            print("Error with the connection")

                                                                    # Printer code end from here#######################################

                                                                    return http.request.render(
                                                                        'vidya.enter_weight_page',
                                                                        {'track_pro': False, 'by_sys': False,
                                                                         'swt_val': value1,'lot_name': num_ser,
                                                                         'product': rec.description_picking,
                                                                         'table': self.table})
                                                                else:
                                                                    for re in stock_move_line:
                                                                            print("?????????????????????????????????????????",re.lot_name)
                                                                            if re.product_id.name == request.session['product']:
                                                                                move_obj_line = request.env[
                                                                                    'stock.move.line'].sudo().create({
                                                                                    'picking_id': stock_pick_obj.id,
                                                                                    'move_id': rec.id,
                                                                                    'location_id': 4,
                                                                                    'location_dest_id': 8,
                                                                                    'lot_name': kw['lot'],
                                                                                    'product_uom_id': 1,
                                                                                    'product_id': rec.product_id.id,
                                                                                    'qty_done': float(kw['we']) - float(
                                                                                        kw['tel_we']),
                                                                                    'company_id': 1,
                                                                                })
                                                                                for re in stock_pick_obj.move_ids_without_package.move_line_nosuggest_ids:
                                                                                    request.session['ser_list'].append(
                                                                                        re.lot_name)


                                                                                for re in stock_pick_obj.move_ids_without_package.move_line_nosuggest_ids:
                                                                                    if re.product_id.name in self.ser_list1:
                                                                                        self.ser_list1[
                                                                                            re.product_id.name].append(
                                                                                            re.lot_name)
                                                                                    else:
                                                                                        self.ser_list1[
                                                                                            re.product_id.name] = [
                                                                                            re.lot_name]
                                                                                name = str(move_obj_line.product_id.name)

                                                                                # qty = str(move_obj_line.qty_done).encode('utf-8')
                                                                                des = str(move_obj_line.product_id.description_purchase)
                                                                                lot = str(move_obj_line.lot_name)
                                                                                vendor = str(stock_pick_obj.partner_id.name)

                                                                                for move_line in stock_pick_obj.move_ids_without_package:
                                                                                    if move_line.product_id.name == request.session['product'] and move_line.line_no == request.session['line_no']:
                                                                                        self.table[
                                                                                            move_line.product_id.name] = [
                                                                                            move_line.product_uom_qty,
                                                                                            round(
                                                                                                move_line.product_uom_qty - move_line.quantity_done,
                                                                                                3),
                                                                                            request.session['unit']]

                                                                                # Printer code start from here#######################################
                                                                                user_obj = request.env[
                                                                                    'user.ip.address'].sudo().search(
                                                                                    [('name', '=',
                                                                                      request.session['uid'])])
                                                                                pro_obj = request.env[
                                                                                    'product.template'].sudo().search(
                                                                                    [('name', '=',
                                                                                      request.session['product'])])
                                                                                for i in range(int(kw['pr_qty'])):
                                                                                    from ipaddress import ip_address
                                                                                    import socket
                                                                                    mysocket = socket.socket(
                                                                                        socket.AF_INET,
                                                                                        socket.SOCK_STREAM)
                                                                                    ip_address = user_obj.printer_ip_address
                                                                                    print(
                                                                                        "::::::::::::::::::::::::::::::::::::::::::",
                                                                                        ip_address)
                                                                                    port = 9100
                                                                                    try:
                                                                                        mysocket.connect(
                                                                                            (ip_address, port))
                                                                                        print(
                                                                                            "neleneleklekelekleklekelke;lekle",
                                                                                            name)  # connecting to host
                                                                                        # mysocket.send(
                                                                                        #     f'^XA^MMT^PW831^LL1205^LS0^FT671,607^A0B,45,45^FH\^FD{str(vendor)}^FS^FT561,606^A0B,45,45^FH\^FD{str(des)}^FS^FT677,976^A0B,56,55^FH\^FDVendor^FS^FT680,648^A0B,56,55^FH\^FD:^FS^FT566,980^A0B,56,45^FH\^FDItem Description^FS^FT569,653^A0B,56,45^FH\^FD:^FS^FT454,980^A0B,56,55^FH\^FDItem Code^FS^FT446,604^A0B,45,45^FH\^FD{str(name)}^FS^FT457,653^A0B,56,55^FH\^FD:^FS^FT131,769^BQN,2,10^FH\^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode(
                                                                                        #         'utf-8'))  # using bytes
                                                                                        # mysocket.close()  # closing connection

                                                                                        mysocket.send(
                                                                                             f'^XA^SZ2^JMA^MCY^PMN^PW580~JSN^JZY^LH0,0^LRN^XZ^XA^FT34,60^CI0^A0N,28,38^FDItem Code^FS^FT34,132^A0N,28,38^FDDescription^FS^FT34,204^A0N,28,38^FDVendorName^FS^FT269,60^A0N,28,38^FD:{str(name)}^FS^FT270,132^A0N,28,38^FD:{str(des)}^FS^FT270,204^A0N,28,38^FD:{str(vendor)}^FS^FO227,220^BQN,2,6^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode('utf-8'))  # using bytes
                                                                                        mysocket.close()  # closing connection


                                                                                    except:
                                                                                        print(
                                                                                            "Error with the connection")

                                                                                # Printer code end from here#######################################

                                                                                return http.request.render(
                                                                                    'vidya.enter_weight_page',
                                                                                    {'track_pro': False,
                                                                                     'by_sys': False,'lot_name': num_ser,
                                                                                     'swt_val': value1,
                                                                                     'product': rec.description_picking,
                                                                                     'table': self.table})
                                                                            else:
                                                                                error = "This lot number already exits."
                                                                                return http.request.render(
                                                                                    'vidya.enter_weight_page',
                                                                                    {'track_pro': False,
                                                                                     'by_sys': False,
                                                                                     'swt_val': value1,'lot_name': num_ser,
                                                                                     'product': rec.description_picking,
                                                                                     'table': self.table,
                                                                                     'error': error})

                                                else:
                                                    print("PPPPPPPPPPPPPPPPPPPPPOOOOOOOOOOOOOOOOOOOOOOOOOO",
                                                          rec.product_id.name, rec.line_no)
                                                    for j in rec.move_line_nosuggest_ids:
                                                        print("333333333333333333333333333",rec.quantity_done,
                                                              j.qty_done + (
                                                                      float(kw['we']) - float(kw['tel_we'])))
                                                        if rec.product_uom_qty < (rec.quantity_done + (
                                                                float(kw['we']) - float(kw['tel_we']))):
                                                            error = f"You can't add more than {self.table[rec.product_id.name][1]} quantity"
                                                            return http.request.render('vidya.enter_weight_page',
                                                                                       {'track_pro': False,
                                                                                        'by_sys': False,
                                                                                        'swt_val': value1,'lot_name': num_ser,
                                                                                        'product': rec.description_picking,
                                                                                        'table': self.table,
                                                                                        'error': error})
                                                        else:
                                                            if len(stock_move_line) == 0:
                                                                move_obj_line = request.env[
                                                                    'stock.move.line'].sudo().create(
                                                                    {'picking_id': stock_pick_obj.id, 'move_id': rec.id,
                                                                        'location_id': 4, 'location_dest_id': 8,
                                                                        'lot_name': kw['lot'], 'product_uom_id': 1,
                                                                        'product_id': rec.product_id.id,
                                                                        'qty_done': float(kw['we']) - float(
                                                                            kw['tel_we']), 'company_id': 1, })
                                                                for re in stock_pick_obj.move_ids_without_package.move_line_nosuggest_ids:
                                                                    if re.product_id.name in self.ser_list1:
                                                                        self.ser_list1[re.product_id.name].append(
                                                                            re.lot_name)
                                                                    else:
                                                                        self.ser_list1[re.product_id.name] = [
                                                                            re.lot_name]

                                                                for re in stock_pick_obj.move_ids_without_package.move_line_nosuggest_ids:
                                                                    if re.lot_name not in request.session['ser_list']:
                                                                        request.session['ser_list'].append(re.lot_name)
                                                                print("66666666666666666666666666666666666",
                                                                      request.session['ser_list'])

                                                                name = str(move_obj_line.product_id.name)

                                                                # qty = str(move_obj_line.qty_done).encode('utf-8')
                                                                des = str(move_obj_line.product_id.description_purchase)
                                                                lot = str(move_obj_line.lot_name)
                                                                vendor = str(stock_pick_obj.partner_id.name)

                                                                for move_line in stock_pick_obj.move_ids_without_package:
                                                                    if move_line.product_id.name == request.session[
                                                                        'product'] and move_line.line_no == \
                                                                            request.session['line_no']:
                                                                        self.table[move_line.product_id.name] = [
                                                                            move_line.product_uom_qty, round(
                                                                                move_line.product_uom_qty - move_line.quantity_done,
                                                                                3), request.session['unit']]

                                                                # Printer code start from here#######################################
                                                                user_obj = request.env['user.ip.address'].sudo().search(
                                                                    [('name', '=', request.session['uid'])])
                                                                pro_obj = request.env['product.template'].sudo().search(
                                                                    [('name', '=', request.session['product'])])
                                                                for i in range(int(kw['pr_qty'])):
                                                                    from ipaddress import ip_address
                                                                    import socket
                                                                    mysocket = socket.socket(socket.AF_INET,
                                                                                             socket.SOCK_STREAM)
                                                                    ip_address = user_obj.printer_ip_address
                                                                    print("::::::::::::::::::::::::::::::::::::::::::",
                                                                        ip_address)
                                                                    port = 9100
                                                                    try:
                                                                        mysocket.connect((ip_address, port))
                                                                        print("neleneleklekelekleklekelke;lekle",
                                                                            name)  # connecting to host
                                                                        # mysocket.send(
                                                                        #     f'^XA^MMT^PW831^LL1205^LS0^FT671,607^A0B,45,45^FH\^FD{str(vendor)}^FS^FT561,606^A0B,45,45^FH\^FD{str(des)}^FS^FT677,976^A0B,56,55^FH\^FDVendor^FS^FT680,648^A0B,56,55^FH\^FD:^FS^FT566,980^A0B,56,45^FH\^FDItem Description^FS^FT569,653^A0B,56,45^FH\^FD:^FS^FT454,980^A0B,56,55^FH\^FDItem Code^FS^FT446,604^A0B,45,45^FH\^FD{str(name)}^FS^FT457,653^A0B,56,55^FH\^FD:^FS^FT131,769^BQN,2,10^FH\^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode(
                                                                        #         'utf-8'))  # using bytes
                                                                        # mysocket.close()  # closing connection

                                                                        mysocket.send(
                                                                            f'^XA^SZ2^JMA^MCY^PMN^PW580~JSN^JZY^LH0,0^LRN^XZ^XA^FT34,60^CI0^A0N,28,38^FDItem Code^FS^FT34,132^A0N,28,38^FDDescription^FS^FT34,204^A0N,28,38^FDVendorName^FS^FT269,60^A0N,28,38^FD:{str(name)}^FS^FT270,132^A0N,28,38^FD:{str(des)}^FS^FT270,204^A0N,28,38^FD:{str(vendor)}^FS^FO227,220^BQN,2,6^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode(
                                                                                'utf-8'))  # using bytes
                                                                        mysocket.close()  # closing connection
                                                                    except:
                                                                        print("Error with the connection")

                                                                # Printer code end from here#######################################

                                                                return http.request.render('vidya.enter_weight_page',
                                                                    {'track_pro': False, 'by_sys': False,
                                                                     'swt_val': value1,'lot_name': num_ser,
                                                                     'product': rec.description_picking,
                                                                     'table': self.table, })
                                                            # print("vvvvvvvvvvvvvvvvvvvvvvvvvv",self.ser_list1,request.session['ser_list'])
                                                            # if self.ser_list1 == {} and kw['lot'] in request.session['ser_list'] and stock_lot and request.session['product'] != stock_lot.product_id.name:
                                                            #     error="This serial number already exits."
                                                            #     return http.request.render(
                                                            #         'vidya.enter_weight_page',
                                                            #         {'track_pro': False,
                                                            #          'by_sys': False,
                                                            #          'swt_val': value1,
                                                            #          'product': rec.description_picking,
                                                            #          'table': self.table,'error':error
                                                            #          })
                                                            # elif self.ser_list1 == {}:
                                                            #     print("elif code >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                                                            #     move_obj_line = request.env[
                                                            #         'stock.move.line'].sudo().create({
                                                            #         'picking_id': stock_pick_obj.id,
                                                            #         'move_id': rec.id,
                                                            #         'location_id': 4,
                                                            #         'location_dest_id': 8,
                                                            #         'lot_name': kw['lot'],
                                                            #         'product_uom_id': 1,
                                                            #         'product_id': rec.product_id.id,
                                                            #         'qty_done': float(kw['we']) - float(
                                                            #             kw['tel_we']),
                                                            #         'company_id': 1,
                                                            #     })
                                                            #
                                                            #     for re in stock_pick_obj.move_ids_without_package.move_line_nosuggest_ids:
                                                            #         if re.product_id.name in self.ser_list1:
                                                            #             self.ser_list1[re.product_id.name].append(re.lot_name)
                                                            #         else:
                                                            #             self.ser_list1[re.product_id.name] = [re.lot_name]
                                                            #
                                                            #
                                                            #     for re in stock_pick_obj.move_ids_without_package.move_line_nosuggest_ids:
                                                            #         request.session['ser_list'].append(re.lot_name)
                                                            #     print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&",request.session['ser_list'])
                                                            #
                                                            #     name = str(move_obj_line.product_id.name)
                                                            #
                                                            #     # qty = str(move_obj_line.qty_done).encode('utf-8')
                                                            #     des = str(
                                                            #         move_obj_line.product_id.description_purchase)
                                                            #     lot = str(move_obj_line.lot_name)
                                                            #     vendor = str(stock_pick_obj.partner_id.name)
                                                            #
                                                            #     for move_line in stock_pick_obj.move_ids_without_package:
                                                            #         if move_line.product_id.name == request.session['product'] and move_line.line_no ==request.session['line_no']:
                                                            #             self.table[move_line.product_id.name] = [
                                                            #                 move_line.product_uom_qty,
                                                            #                 abs(round(
                                                            #                     move_line.product_uom_qty - move_line.quantity_done,
                                                            #                     3)), request.session['unit']]
                                                            #
                                                            #     # Printer code start from here#######################################
                                                            #     user_obj = request.env[
                                                            #         'user.ip.address'].sudo().search(
                                                            #         [('name', '=', request.session['uid'])])
                                                            #     pro_obj = request.env[
                                                            #         'product.template'].sudo().search(
                                                            #         [('name', '=', request.session['product'])])
                                                            #     for i in range(int(kw['pr_qty'])):
                                                            #         from ipaddress import ip_address
                                                            #         import socket
                                                            #         mysocket = socket.socket(socket.AF_INET,
                                                            #                                  socket.SOCK_STREAM)
                                                            #         ip_address = user_obj.printer_ip_address
                                                            #         print(
                                                            #             "::::::::::::::::::::::::::::::::::::::::::",
                                                            #             ip_address)
                                                            #         port = 9100
                                                            #         try:
                                                            #             mysocket.connect((ip_address, port))
                                                            #             print("neleneleklekelekleklekelke;lekle",
                                                            #                   name)  # connecting to host
                                                            #             # mysocket.send(
                                                            #             #     f'^XA^MMT^PW831^LL1205^LS0^FT671,607^A0B,45,45^FH\^FD{str(vendor)}^FS^FT561,606^A0B,45,45^FH\^FD{str(des)}^FS^FT677,976^A0B,56,55^FH\^FDVendor^FS^FT680,648^A0B,56,55^FH\^FD:^FS^FT566,980^A0B,56,45^FH\^FDItem Description^FS^FT569,653^A0B,56,45^FH\^FD:^FS^FT454,980^A0B,56,55^FH\^FDItem Code^FS^FT446,604^A0B,45,45^FH\^FD{str(name)}^FS^FT457,653^A0B,56,55^FH\^FD:^FS^FT131,769^BQN,2,10^FH\^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode(
                                                            #             #         'utf-8'))  # using bytes
                                                            #             # mysocket.close()  # closing connection
                                                            #
                                                            #             mysocket.send(
                                                            #                 f'^XA^SZ2^JMA^MCY^PMN^PW580~JSN^JZY^LH0,0^LRN^XZ^XA^FT34,60^CI0^A0N,28,38^FDItem Code^FS^FT34,132^A0N,28,38^FDDescription^FS^FT34,204^A0N,28,38^FDVendorName^FS^FT269,60^A0N,28,38^FD:{str(name)}^FS^FT270,132^A0N,28,38^FD:{str(des)}^FS^FT270,204^A0N,28,38^FD:{str(vendor)}^FS^FO227,220^BQN,2,6^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode('utf-8')) # using bytes
                                                            #             mysocket.close()  # closing connection
                                                            #
                                                            #         except:
                                                            #             print("Error with the connection")
                                                            #
                                                            #     # Printer code end from here#######################################
                                                            #
                                                            #     return http.request.render(
                                                            #         'vidya.enter_weight_page',
                                                            #         {'track_pro': False,
                                                            #          'by_sys': False,
                                                            #          'swt_val': value1,
                                                            #          'product': rec.description_picking,
                                                            #          'table': self.table,
                                                            #          })
                                                            # else:
                                                            #     temp = {}
                                                            else:
                                                                for product, lot in self.ser_list1.items():
                                                                    for re in stock_move_line:
                                                                        print("<<<<<<<<<<<?????????????????>>>>>>>>>>>>>>>>>>>>>>")
                                                                        if re.product_id.name == request.session['product']:
                                                                            print("tesing1111111111111111111111111>>>>>>>>>>>>>>>>>>>>>>>",re.product_id.name,request.session['product'])
                                                                            move_obj_line = request.env[
                                                                                'stock.move.line'].sudo().create({
                                                                                'picking_id': stock_pick_obj.id,
                                                                                'move_id': rec.id,
                                                                                'location_id': 4,
                                                                                'location_dest_id': 8,
                                                                                'lot_name': kw['lot'],
                                                                                'product_uom_id': 1,
                                                                                'product_id': rec.product_id.id,
                                                                                'qty_done': float(kw['we']) - float(
                                                                                    kw['tel_we']),
                                                                                'company_id': 1,
                                                                            })
                                                                            for re in stock_pick_obj.move_ids_without_package.move_line_nosuggest_ids:
                                                                                if re.product_id.name in self.ser_list1:
                                                                                    self.ser_list1[re.product_id.name].append(re.lot_name)
                                                                                else:
                                                                                    self.ser_list1[re.product_id.name] = [re.lot_name]

                                                                            for re in stock_pick_obj.move_ids_without_package.move_line_nosuggest_ids:
                                                                                if re.lot_name not in request.session['ser_list']:
                                                                                    request.session['ser_list'].append(re.lot_name)
                                                                            print("66666666666666666666666666666666666",request.session['ser_list'])

                                                                            name = str(move_obj_line.product_id.name)

                                                                            # qty = str(move_obj_line.qty_done).encode('utf-8')
                                                                            des = str(
                                                                                move_obj_line.product_id.description_purchase)
                                                                            lot = str(move_obj_line.lot_name)
                                                                            vendor = str(stock_pick_obj.partner_id.name)

                                                                            for move_line in stock_pick_obj.move_ids_without_package:
                                                                                if move_line.product_id.name == \
                                                                                        request.session[
                                                                                            'product'] and move_line.line_no == \
                                                                                        request.session['line_no']:
                                                                                    self.table[
                                                                                        move_line.product_id.name] = [
                                                                                        move_line.product_uom_qty,
                                                                                        round(
                                                                                            move_line.product_uom_qty - move_line.quantity_done,
                                                                                            3), request.session['unit']]

                                                                            # Printer code start from here#######################################
                                                                            user_obj = request.env[
                                                                                'user.ip.address'].sudo().search(
                                                                                [('name', '=', request.session['uid'])])
                                                                            pro_obj = request.env[
                                                                                'product.template'].sudo().search(
                                                                                [('name', '=',
                                                                                  request.session['product'])])
                                                                            for i in range(int(kw['pr_qty'])):
                                                                                from ipaddress import ip_address
                                                                                import socket
                                                                                mysocket = socket.socket(socket.AF_INET,
                                                                                                         socket.SOCK_STREAM)
                                                                                ip_address = user_obj.printer_ip_address
                                                                                print(
                                                                                    "::::::::::::::::::::::::::::::::::::::::::",
                                                                                    ip_address)
                                                                                port = 9100
                                                                                try:
                                                                                    mysocket.connect((ip_address, port))
                                                                                    print(
                                                                                        "neleneleklekelekleklekelke;lekle",
                                                                                        name)  # connecting to host
                                                                                    # mysocket.send(
                                                                                    #     f'^XA^MMT^PW831^LL1205^LS0^FT671,607^A0B,45,45^FH\^FD{str(vendor)}^FS^FT561,606^A0B,45,45^FH\^FD{str(des)}^FS^FT677,976^A0B,56,55^FH\^FDVendor^FS^FT680,648^A0B,56,55^FH\^FD:^FS^FT566,980^A0B,56,45^FH\^FDItem Description^FS^FT569,653^A0B,56,45^FH\^FD:^FS^FT454,980^A0B,56,55^FH\^FDItem Code^FS^FT446,604^A0B,45,45^FH\^FD{str(name)}^FS^FT457,653^A0B,56,55^FH\^FD:^FS^FT131,769^BQN,2,10^FH\^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode(
                                                                                    #         'utf-8'))  # using bytes
                                                                                    # mysocket.close()  # closing connection

                                                                                    mysocket.send(
                                                                                         f'^XA^SZ2^JMA^MCY^PMN^PW580~JSN^JZY^LH0,0^LRN^XZ^XA^FT34,60^CI0^A0N,28,38^FDItem Code^FS^FT34,132^A0N,28,38^FDDescription^FS^FT34,204^A0N,28,38^FDVendorName^FS^FT269,60^A0N,28,38^FD:{str(name)}^FS^FT270,132^A0N,28,38^FD:{str(des)}^FS^FT270,204^A0N,28,38^FD:{str(vendor)}^FS^FO227,220^BQN,2,6^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode('utf-8'))  # using bytes
                                                                                    mysocket.close()  # closing connection
                                                                                except:
                                                                                    print("Error with the connection")

                                                                            # Printer code end from here#######################################

                                                                            return http.request.render(
                                                                                'vidya.enter_weight_page',
                                                                                {'track_pro': False,
                                                                                 'by_sys': False,
                                                                                 'swt_val': value1,'lot_name': num_ser,
                                                                                 'product': rec.description_picking,
                                                                                 'table': self.table,
                                                                                 })
                                                                        else:
                                                                            error = "this lot number already exits."
                                                                            return http.request.render(
                                                                                'vidya.enter_weight_page',
                                                                                {'track_pro': False,
                                                                                 'by_sys': False,
                                                                                 'swt_val': value1,'lot_name': num_ser,
                                                                                 'product': rec.description_picking,
                                                                                 'table': self.table,
                                                                                 'error': error,
                                                                                 })

                                            else:
                                                error = "Tel weight must be less then product actual weight."
                                                return http.request.render('vidya.enter_weight_page',
                                                                           {'track_pro': False, 'by_sys': False,
                                                                            'swt_val': value1,'lot_name': num_ser,
                                                                            'product': rec.description_picking,
                                                                            'table': self.table, 'error': error})




                        ################################ tracking is by serial number#########################################################################################################
                        elif rec.product_id.tracking == "serial":
                            # stock_lot1 = request.env['stock.production.lot'].sudo().search([('name', '=', kw['ser'])])
                            # for re in stock_pick_obj.move_line_nosuggest_ids:
                            #     if rec.product_id.id == re.product_id.id:
                            #         ser_list.append(re.lot_name)
                            ################################ tracking is by serial number system genertaed serial number#########################################################################################################
                            if pro_obj.by_system == True:
                                used = request.env['num.ser'].sudo().search(
                                    [('series_code', '=', pro_obj.default_code)])
                                num_ser = used.last_number_used
                                if rec.product_uom_qty == rec.quantity_done:
                                    print("fggggggggggggggggggggggggnnnnnnnnnnnnnnnnnnnnnnnnnnnnn",
                                          self.table)
                                    error = f"You can't add more than {self.table[rec.product_id.name][1]} quantity"
                                    return http.request.render('vidya.enter_weight_page',
                                                           {'track_pro': True, 'by_sys': True,'lot_name': num_ser,
                                                            'product': rec.description_picking, 'table': self.table,'error':error})

                                else:
                                    used = request.env['num.ser'].sudo().search(
                                        [('series_code', '=', pro_obj.default_code)])
                                    num_ser = used.last_number_used
                                    # num_ser = pro_obj.last_number_used
                                    last_digit = num_ser.split("-")[-1]
                                    ser = int((num_ser.split("-")[-1])) + used.increment_by
                                    ser1 = str(ser).zfill(len(last_digit))
                                    print("KJJJGDHSDGSDSDGDFSDFDSFFFFADFDFFFFFF", ser1)

                                    move_obj_line = request.env['stock.move.line'].sudo().create({
                                        'picking_id': stock_pick_obj.id,
                                        'move_id': rec.id,
                                        'location_id': 4,
                                        'location_dest_id': 8,
                                        'lot_name': (num_ser.split("-")[0] + "-" + num_ser.split("-")[1] + "-" + ser1),
                                        'product_uom_id': 1,
                                        'product_id': rec.product_id.id,
                                        'qty_done': 1,
                                        'company_id': 1,
                                    })
                                    used.write({
                                        'last_number_used': move_obj_line.lot_name,
                                    })
                                    for move_line in stock_pick_obj.move_ids_without_package:
                                        if move_line.product_id.name == request.session['product'] and move_line.line_no == \
                                                request.session['line_no']:
                                            self.table[move_line.product_id.name] = [
                                                move_line.product_uom_qty,
                                                abs(round(
                                                    move_line.product_uom_qty - move_line.quantity_done,
                                                    3)), request.session['unit']]

                                    name = str(move_obj_line.product_id.name)
                                    # qty = str(move_obj_line.qty_done).encode('utf-8')
                                    des = str(move_obj_line.product_id.description_purchase)
                                    lot = str(move_obj_line.lot_name)
                                    vendor = str(stock_pick_obj.partner_id.name)
                                    user_obj = request.env['user.ip.address'].sudo().search(
                                        [('name', '=', request.session['uid'])])
                                    pro_obj = request.env['product.template'].sudo().search(
                                        [('name', '=', request.session['product'])])
                                    for i in range(int(kw['pr_qty'])):
                                        from ipaddress import ip_address
                                        import socket
                                        mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                        ip_address = user_obj.printer_ip_address
                                        print("::::::::::::::::::::::::::::::::::::::::::", ip_address)
                                        port = 9100
                                        try:
                                            mysocket.connect((ip_address, port))
                                            print("neleneleklekelekleklekelke;lekle",
                                                  name)  # connecting to host
                                            # mysocket.send(
                                            #     f'^XA^MMT^PW831^LL1205^LS0^FT671,607^A0B,45,45^FH\^FD{str(vendor)}^FS^FT561,606^A0B,45,45^FH\^FD{str(des)}^FS^FT677,976^A0B,56,55^FH\^FDVendor^FS^FT680,648^A0B,56,55^FH\^FD:^FS^FT566,980^A0B,56,45^FH\^FDItem Description^FS^FT569,653^A0B,56,45^FH\^FD:^FS^FT454,980^A0B,56,55^FH\^FDItem Code^FS^FT446,604^A0B,45,45^FH\^FD{str(name)}^FS^FT457,653^A0B,56,55^FH\^FD:^FS^FT131,769^BQN,2,10^FH\^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode(
                                            #         'utf-8'))  # using bytes
                                            # mysocket.close()  # closing connection

                                            mysocket.send(
                                                f'^XA^SZ2^JMA^MCY^PMN^PW580~JSN^JZY^LH0,0^LRN^XZ^XA^FT34,60^CI0^A0N,28,38^FDItem Code^FS^FT34,132^A0N,28,38^FDDescription^FS^FT34,204^A0N,28,38^FDVendorName^FS^FT269,60^A0N,28,38^FD:{str(name)}^FS^FT270,132^A0N,28,38^FD:{str(des)}^FS^FT270,204^A0N,28,38^FD:{str(vendor)}^FS^FO227,220^BQN,2,6^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode(
                                                    'utf-8'))  # using bytes
                                            mysocket.close()  # closing connection

                                        except:
                                            print("Error with the connection")

                                    return http.request.render('vidya.enter_weight_page',
                                                               {'track_pro': True, 'by_sys': True,'lot_name': num_ser,
                                                                'product': rec.description_picking, 'table': self.table})
                            ################################ tracking is by serial number############################################################################################
                            else:
                                used = request.env['num.ser'].sudo().search(
                                    [('series_code', '=', pro_obj.default_code)])
                                num_ser = used.last_number_used
                                stock_lot1 = request.env['stock.lot'].sudo().search(
                                    [('name', '=', kw['ser'])])
                                print("IIIIIIIIIIIIIIIIIIIIIUUUUUUUUUUUUUUuuuuuuuuu", request.session['ser_list'],stock_lot1)
                                if kw['ser'] in request.session['ser_list']:
                                    error = "This serial number already assign"
                                    return http.request.render('vidya.enter_weight_page',
                                                               {'track_pro': True, 'by_sys': False,'lot_name': num_ser,
                                                                'product': rec.description_picking,
                                                                'error': error,
                                                                'table': self.table})
                                else:
                                    move_obj_line = request.env['stock.move.line'].sudo().create({
                                        'picking_id': stock_pick_obj.id,
                                        'move_id': rec.id,
                                        'location_id': 4,
                                        'location_dest_id': 8,
                                        'lot_name': kw['ser'],
                                        'product_uom_id': 1,
                                        'product_id': rec.product_id.id,
                                        'qty_done': 1,
                                        'company_id': 1,
                                    })
                                    for re in stock_pick_obj.move_ids_without_package.move_line_nosuggest_ids:
                                        request.session['ser_list'].append(re.lot_name)

                                    self.table1 = {}
                                    for move_line in stock_pick_obj.move_ids_without_package:
                                        if move_line.product_id.name == request.session[
                                            'product'] and move_line.line_no == request.session['line_no']:
                                            self.table1[move_line.product_id.name] = [move_line.product_uom_qty, round(
                                                move_line.product_uom_qty - move_line.quantity_done, 3),
                                                                                      request.session['unit']]

                                    name = str(move_obj_line.product_id.name)
                                    # qty = str(move_obj_line.qty_done).encode('utf-8')
                                    des = str(move_obj_line.product_id.description_purchase)
                                    lot = str(move_obj_line.lot_name)
                                    vendor = str(stock_pick_obj.partner_id.name)
                                    user_obj = request.env['user.ip.address'].sudo().search(
                                        [('name', '=', request.session['uid'])])
                                    pro_obj = request.env['product.template'].sudo().search(
                                        [('name', '=', request.session['product'])])
                                    for i in range(int(kw['pr_qty'])):
                                        from ipaddress import ip_address
                                        import socket
                                        mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                        ip_address = user_obj.printer_ip_address
                                        print("::::::::::::::::::::::::::::::::::::::::::", ip_address)
                                        port = 9100
                                        try:
                                            mysocket.connect((ip_address, port))
                                            print("neleneleklekelekleklekelke;lekle",
                                                  name)  # connecting to host
                                            # mysocket.send(
                                            #     f'^XA^MMT^PW831^LL1205^LS0^FT671,607^A0B,45,45^FH\^FD{str(vendor)}^FS^FT561,606^A0B,45,45^FH\^FD{str(des)}^FS^FT677,976^A0B,56,55^FH\^FDVendor^FS^FT680,648^A0B,56,55^FH\^FD:^FS^FT566,980^A0B,56,45^FH\^FDItem Description^FS^FT569,653^A0B,56,45^FH\^FD:^FS^FT454,980^A0B,56,55^FH\^FDItem Code^FS^FT446,604^A0B,45,45^FH\^FD{str(name)}^FS^FT457,653^A0B,56,55^FH\^FD:^FS^FT131,769^BQN,2,10^FH\^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode(
                                            #         'utf-8'))  # using bytes
                                            # mysocket.close()  # closing connection

                                            mysocket.send(
                                                f'^XA^SZ2^JMA^MCY^PMN^PW580~JSN^JZY^LH0,0^LRN^XZ^XA^FT34,60^CI0^A0N,28,38^FDItem Code^FS^FT34,132^A0N,28,38^FDDescription^FS^FT34,204^A0N,28,38^FDVendorName^FS^FT269,60^A0N,28,38^FD:{str(name)}^FS^FT270,132^A0N,28,38^FD:{str(des)}^FS^FT270,204^A0N,28,38^FD:{str(vendor)}^FS^FO227,220^BQN,2,6^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode(
                                                    'utf-8'))  # using bytes
                                            mysocket.close()  # closing connection

                                        except:
                                            print("Error with the connection")

                                    if rec.product_uom_qty == rec.quantity_done:
                                        return http.request.render('vidya.thank_you_page',
                                                                   {'track_pro': True, 'by_sys': False,'lot_name': num_ser,
                                                                    'table': self.table1})
                                    return http.request.render('vidya.enter_weight_page',
                                                               {'track_pro': True, 'by_sys': False,'lot_name': num_ser,
                                                                'product': rec.description_picking,
                                                                'table': self.table})
                        ################################ tracking is by No tracking############################################################################################

                        else:
                            ################################ tracking is by No tracking and tolerance is mention############################################################################################
                            if rec.tolerance:
                                print("jigijigijigijigi",rec.tolerance,type(rec.tolerance))
                                tol = (rec.tolerance)
                                tolerance_obj = rec.product_uom_qty + ((rec.product_uom_qty * float(tol)) / 100)
                                if (rec.quantity_done + float(kw['we'])) > tolerance_obj:
                                    error = "You can't add more weights."
                                    return http.request.render('vidya.enter_weight_page',
                                                               {'track_pro': 5, 'by_sys': True,
                                                                'swt_val': value1, 'product': rec.description_picking,
                                                                'error': error, 'table': self.table})
                                move_obj_line = request.env['stock.move.line'].sudo().create({
                                    'picking_id': stock_pick_obj.id,
                                    'move_id': rec.id,
                                    'location_id': 4,
                                    'location_dest_id': 8,
                                    'product_uom_id': 1,
                                    'product_id': rec.product_id.id,
                                    'qty_done': kw['we'],
                                    'company_id': 1,
                                })
                                name = str(move_obj_line.product_id.name)
                                qty = str(move_obj_line.qty_done).encode('utf-8')
                                lot = str(move_obj_line.lot_name)
                                vendor = str(stock_pick_obj.partner_id.name)
                                self.table = {}
                                for move_line in stock_pick_obj.move_ids_without_package:
                                    if move_line.product_id.name == request.session['product'] and move_line.line_no == \
                                            request.session['line_no']:
                                        self.table[move_line.product_id.name] = [
                                            move_line.product_uom_qty,
                                            abs(round(
                                                move_line.product_uom_qty - move_line.quantity_done,
                                                3)), request.session['unit']]

                                # return http.request.render('vidya.enter_weight_page',
                                #                            {'track_pro': False, 'swt_val': value1,
                                #                             'product': rec.product_id.name,'table':self.table})

                                # Printer code start from here for notracking product without qrcode#######################################
                                for i in range(int(kw['pr_qty'])):
                                    from ipaddress import ip_address
                                    import socket
                                    mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                    ip_address = user_obj.printer_ip_address
                                    port = 9100
                                    name = str(move_obj_line.product_id.name)

                                    # qty = str(move_obj_line.qty_done).encode('utf-8')
                                    des = str(move_obj_line.product_id.description_purchase)

                                    vendor = str(stock_pick_obj.partner_id.name)
                                    try:
                                        mysocket.connect((ip_address, port))  # connecting to host
                                        mysocket.send(
                                             f'^XA^SZ2^JMA^MCY^PMN^PW580~JSN^JZY^LH0,0^LRN^XZ^XA^FT34,60^CI0^A0N,28,38^FDItem Code^FS^FT34,132^A0N,28,38^FDDescription^FS^FT34,204^A0N,28,38^FDVendorName^FS^FT269,60^A0N,28,38^FD:{str(name)}^FS^FT270,132^A0N,28,38^FD:{str(des)}^FS^FT270,204^A0N,28,38^FD:{str(vendor)}^Y^XZ'.encode(
                                                                'utf-8'))  # using bytes
                                        mysocket.close()  # closing connection

                                        # mysocket.send(
                                        #      f'^XA^SZ2^JMA^MCY^PMN^PW580~JSN^JZY^LH0,0^LRN^XZ^XA^FT34,60^CI0^A0N,28,38^FDItem Code^FS^FT34,132^A0N,28,38^FDDescription^FS^FT34,204^A0N,28,38^FDVendorName^FS^FT269,60^A0N,28,38^FD:{str(name)}^FS^FT270,132^A0N,28,38^FD:{str(des)}^FS^FT270,204^A0N,28,38^FD:{str(vendor)}^FS^FO227,220^BQN,2,6^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode('utf-8')) # using bytes
                                        # mysocket.close()  # closing connection

                                    except:
                                        print("Error with the connection")

                                return http.request.render('vidya.enter_weight_page',
                                                           {'swt_val': value1, 'track_pro': 5,
                                                            'product': rec.description_picking, 'table': self.table})
                            ################################ tracking is by No tracking and tolerance not is mention############################################################################################

                            else:
                                if len(rec.move_line_nosuggest_ids) == 0:
                                    if rec.product_uom_qty < rec.quantity_done + (float(kw['we'])):
                                        error = f"You can't add more than {self.table[rec.product_id.name][1]} quantity"
                                        return http.request.render('vidya.enter_weight_page',
                                                                   {'track_pro': False, 'swt_val': value1,
                                                                    'track_pro': 5,
                                                                    'product': rec.description_picking,
                                                                    'table': self.table, 'error': error})
                                    else:
                                        print("!!no tracking tpollence not mentionjjjjjjjjjjjjjjjjjmmm")
                                        move_obj_line = request.env['stock.move.line'].sudo().create({
                                            'picking_id': stock_pick_obj.id,
                                            'move_id': rec.id,
                                            'location_id': 4,
                                            'location_dest_id': 8,
                                            'product_uom_id': 1,
                                            'product_id': rec.product_id.id,
                                            'qty_done': kw['we'],
                                            'company_id': 1,
                                        })
                                        name = str(move_obj_line.product_id.name)

                                        # qty = str(move_obj_line.qty_done).encode('utf-8')
                                        des = str(move_obj_line.product_id.description_purchase)
                                        lot = str(move_obj_line.lot_name)
                                        vendor = str(stock_pick_obj.partner_id.name)
                                        self.table = {}
                                        for move_line in stock_pick_obj.move_ids_without_package:
                                            if move_line.product_id.name == request.session[
                                                'product'] and move_line.line_no == request.session['line_no']:
                                                self.table[move_line.product_id.name] = [
                                                    move_line.product_uom_qty,
                                                    abs(round(
                                                        move_line.product_uom_qty - move_line.quantity_done,
                                                        3)), request.session['unit']]

                                        user_obj = request.env['user.ip.address'].sudo().search(
                                            [('name', '=', request.session['uid'])])
                                        pro_obj = request.env['product.template'].sudo().search(
                                            [('name', '=', request.session['product'])])
                                        for i in range(int(kw['pr_qty'])):
                                            from ipaddress import ip_address
                                            import socket
                                            mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                            ip_address = user_obj.printer_ip_address
                                            print("::::::::::::::::::::::::::::::::::::::::::", ip_address)
                                            port = 9100
                                            try:
                                                mysocket.connect((ip_address, port))
                                                print("neleneleklekelekleklekelke;lekle", name)  # connecting to host
                                                # mysocket.send(
                                                #     f'^XA^MMT^PW831^LL1205^LS0^FT671,607^A0B,45,45^FH\^FD{str(vendor)}^FS^FT561,606^A0B,45,45^FH\^FD{str(des)}^FS^FT677,976^A0B,56,55^FH\^FDVendor^FS^FT680,648^A0B,56,55^FH\^FD:^FS^FT566,980^A0B,56,45^FH\^FDItem Description^FS^FT569,653^A0B,56,45^FH\^FD:^FS^FT454,980^A0B,56,55^FH\^FDItem Code^FS^FT446,604^A0B,45,45^FH\^FD{str(name)}^FS^FT457,653^A0B,56,55^FH\^FD:^FS^FT131,769^BQN,2,10^FH\^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode(
                                                #         'utf-8'))  # using bytes
                                                # mysocket.close()  # closing connection

                                                mysocket.send(
                                                    f'^XA^SZ2^JMA^MCY^PMN^PW580~JSN^JZY^LH0,0^LRN^XZ^XA^FT34,60^CI0^A0N,28,38^FDItem Code^FS^FT34,132^A0N,28,38^FDDescription^FS^FT34,204^A0N,28,38^FDVendorName^FS^FT269,60^A0N,28,38^FD:{str(name)}^FS^FT270,132^A0N,28,38^FD:{str(des)}^FS^FT270,204^A0N,28,38^FD:{str(vendor)}^Y^XZ'.encode(
                                                        'utf-8'))  # using bytes
                                                mysocket.close()  # closing connection

                                            except:
                                                print("Error with the connection")
                                        print("NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNnn",self.table)
                                        return http.request.render('vidya.enter_weight_page',
                                                                   {'track_pro': False, 'swt_val': value1,
                                                                    'track_pro': 5,
                                                                    'product': rec.description_picking,
                                                                    'table': self.table})
                                else:
                                    for j in rec.move_line_nosuggest_ids:
                                        if rec.product_uom_qty < (rec.quantity_done + float(kw['we'])):
                                            error = f"You can't add more than {self.table[rec.product_id.name][1]} quantity"
                                            return http.request.render('vidya.enter_weight_page',
                                                                       {'track_pro': False, 'swt_val': value1,
                                                                        'track_pro': 5,
                                                                        'product': rec.description_picking,
                                                                        'table': self.table, 'error': error})
                                        else:
                                            print("!!no tracking tpollence not mentionjjjjjjjjjjjjjjjjjmmm")
                                            move_obj_line = request.env['stock.move.line'].sudo().create({
                                                'picking_id': stock_pick_obj.id,
                                                'move_id': rec.id,
                                                'location_id': 4,
                                                'location_dest_id': 8,
                                                'product_uom_id': 1,
                                                'product_id': rec.product_id.id,
                                                'qty_done': kw['we'],
                                                'company_id': 1,
                                            })
                                            name = str(move_obj_line.product_id.name)

                                            # qty = str(move_obj_line.qty_done).encode('utf-8')
                                            des = str(move_obj_line.product_id.description_purchase)
                                            lot = str(move_obj_line.lot_name)
                                            vendor = str(stock_pick_obj.partner_id.name)
                                            self.table = {}
                                            for move_line in stock_pick_obj.move_ids_without_package:
                                                if move_line.product_id.name == request.session[
                                                    'product'] and move_line.line_no == request.session['line_no']:
                                                    self.table[move_line.product_id.name] = [
                                                        move_line.product_uom_qty,
                                                        abs(round(
                                                            move_line.product_uom_qty - move_line.quantity_done,
                                                            3)), request.session['unit']]

                                            user_obj = request.env['user.ip.address'].sudo().search(
                                                [('name', '=', request.session['uid'])])
                                            pro_obj = request.env['product.template'].sudo().search(
                                                [('name', '=', request.session['product'])])
                                            for i in range(int(kw['pr_qty'])):
                                                from ipaddress import ip_address
                                                import socket
                                                mysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                                ip_address = user_obj.printer_ip_address
                                                print("::::::::::::::::::::::::::::::::::::::::::", ip_address)
                                                port = 9100
                                                try:
                                                    mysocket.connect((ip_address, port))
                                                    print("neleneleklekelekleklekelke;lekle",
                                                          name)  # connecting to host
                                                    # mysocket.send(
                                                    #     f'^XA^MMT^PW831^LL1205^LS0^FT671,607^A0B,45,45^FH\^FD{str(vendor)}^FS^FT561,606^A0B,45,45^FH\^FD{str(des)}^FS^FT677,976^A0B,56,55^FH\^FDVendor^FS^FT680,648^A0B,56,55^FH\^FD:^FS^FT566,980^A0B,56,45^FH\^FDItem Description^FS^FT569,653^A0B,56,45^FH\^FD:^FS^FT454,980^A0B,56,55^FH\^FDItem Code^FS^FT446,604^A0B,45,45^FH\^FD{str(name)}^FS^FT457,653^A0B,56,55^FH\^FD:^FS^FT131,769^BQN,2,10^FH\^FDLA,{str(lot)}^FS^PQ1,0,1,Y^XZ'.encode(
                                                    #         'utf-8'))  # using bytes
                                                    # mysocket.close()  # closing connection

                                                    mysocket.send(
                                                        f'^XA^SZ2^JMA^MCY^PMN^PW580~JSN^JZY^LH0,0^LRN^XZ^XA^FT34,60^CI0^A0N,28,38^FDItem Code^FS^FT34,132^A0N,28,38^FDDescription^FS^FT34,204^A0N,28,38^FDVendorName^FS^FT269,60^A0N,28,38^FD:{str(name)}^FS^FT270,132^A0N,28,38^FD:{str(des)}^FS^FT270,204^A0N,28,38^FD:{str(vendor)}^Y^XZ'.encode(
                                                            'utf-8'))# using bytes
                                                    mysocket.close()  # closing connection




                                                except:
                                                    print("Error with the connection")
                                            return http.request.render('vidya.enter_weight_page',
                                                                       {'track_pro': False, 'swt_val': value1,
                                                                        'track_pro': 5,
                                                                        'product': rec.description_picking,
                                                                        'table': self.table})



            else:
                error = "This product does not exists."
                return http.request.render('vidya.select_product_page',
                                           {'error': error, 'table': self.table})

        return http.request.render('vidya.select_product_page',
                                   {})
        # except:
        #     import werkzeug.utils
        #     action_id = request.env.ref('stock.action_picking_tree_ready')
        #     return werkzeug.utils.redirect(
        #         '/web#id={}&menu_id=178&action={}&active_id=1&model=stock.picking&view_type=form'.format(
        #             stock_pick_obj.id,
        #             action_id.id))

    @http.route('/done', website=True, auth="public", csrf=False, type='http')
    def done(self, **kw):
        return http.request.render('vidya.select_product_page',
                                   {})

    @http.route('/get_weight', website=True, auth="public", csrf=False, type='http')
    def set_weight(self, **kw):
        user_obj = request.env['user.ip.address'].sudo().search([('name', '=', request.session['uid'])])
        pro_obj = request.env['product.template'].sudo().search([('name', '=', request.session['product'])])
        we_list = []

        # #Jaineel's code
        # import socket
        # new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # new_socket.connect(("192.168.0.7", 23))
        # final_data = ""
        # while True:
        #     raw_data = new_socket.recv(512).decode('unicode_escape').strip()
        #     if len(raw_data) < 9:
        #         if raw_data.startswith("+"):
        #             final_data = raw_data
        #         elif "." in raw_data:
        #             final_data += raw_data
        #         elif "." not in raw_data and "+" in raw_data:
        #             final_data += raw_data[:2]
        #
        #     if "+" in final_data and "." in final_data and final_data.find("+") < final_data.find("."):
        #         if len(final_data.split(".")[1]) == 2:
        #             final_data = final_data.replace("+", '').strip()
        #             print(final_data)
        #             break
        # return http.request.render('vidya.enter_weight_page',
        #                                                               {'track_pro': request.session['track_pro'],
        #                                                                'by_sys': request.session['by_sys'], 'swt_val': final_data,
        #                                                                'product': pro_obj.name, 'table': self.table})
        #
        # print("\n\n\n\nJaineel :::  ",final_data,"\n\n\n\n")

        # weight scale using ip adress as per ther user code start from here#######################
        import socket, time
        TCP_IP = user_obj.ip_address
        TCP_PORT = 4321
        BUFFER_SIZE = 1024
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((TCP_IP, TCP_PORT))
            time.sleep(1)
            data = s.recv(BUFFER_SIZE)
            data1 = data.decode()
            we_list.append(data1)
            tmpl = data1.split('\n')
            print("444444444444444444444444", tmpl, data1)
            we_list2 = []
            for i in tmpl:
                we_list2.append(i.replace('\x02', '').replace("\r", "").replace(" ", ''))
            we_list2.remove('')
            # print("---------------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>",we_list2,we_list2[-1])

            try:
                j = we_list2[-1]
                request.session['j'] = j
                return http.request.render('vidya.enter_weight_page',
                                           {'track_pro': request.session['track_pro'],
                                            'by_sys': request.session['by_sys'], 'swt_val': request.session['j'],
                                            'product': pro_obj.name, 'table': self.table})

            except:
                return http.request.render('vidya.enter_weight_page',
                                           {'track_pro': request.session['track_pro'],
                                            'by_sys': request.session['by_sys'], 'swt_val': 0.0,
                                            'product': pro_obj.name, 'table': self.table})

        except:
            error = "You can't connect to weight scale"
            return http.request.render('vidya.enter_weight_page',
                                       {'track_pro': request.session['track_pro'],
                                        'by_sys': request.session['by_sys'], 'swt_val': 0.0,
                                        'product': pro_obj.name, 'error': error, 'table': self.table})

    @http.route('/back_button', website=True, auth="public", csrf=False, type='http')
    def back_button(self, **kw):
        stock_pick_obj = request.env['stock.picking'].sudo().search([('id', '=', request.session['id'])])
        print("??????????????????????????????????????????????????",stock_pick_obj.name)
        import werkzeug.utils
        action_id = request.env.ref('stock.action_picking_tree_ready')
        return werkzeug.utils.redirect(
            '/web#id={}&cids=1&menu_id=178&action={}&active_id=1&model=stock.picking&view_type=form'.format(
                stock_pick_obj.id, action_id.id))