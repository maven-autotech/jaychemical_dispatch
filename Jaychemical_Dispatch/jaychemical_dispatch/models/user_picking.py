from odoo import fields,models

class ScanQr(models.Model):
    _name = "user.ip.address"
    _description = "User Details"

    name = fields.Many2one('res.users', string='User Name')
    ip_address = fields.Char(string='weight Scale Address')
    printer_ip_address = fields.Char(string='Printer Ip Address')
