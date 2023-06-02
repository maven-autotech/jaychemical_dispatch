from odoo import http,tools,_
from odoo.http import request
import os
from datetime import datetime

########################################## For Other Actions ############################################

class actions(http.Controller):

    @http.route('/scan_complete', website=True, auth="public", csrf=False, type='http')
    def scan_complete_back(self, **kw):
        import werkzeug.utils
        action_id = request.env.ref('stock.stock_picking_type_action')
        return werkzeug.utils.redirect('/web#action={}'.format(action_id.id))


    @http.route('/back_home', website=True, auth="public", csrf=False, type='http')
    def back_button(self, **kw):
        import werkzeug.utils
        action_id = request.env.ref('stock.stock_picking_type_action')
        return werkzeug.utils.redirect('/web#action={}'.format(action_id.id))