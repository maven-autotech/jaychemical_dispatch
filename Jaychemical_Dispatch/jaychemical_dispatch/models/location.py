from odoo import fields, models, api
from odoo.exceptions import UserError
import datetime


class LocationCode(models.Model):
    _name = "location.code"

    location_code = fields.Char(string="Location Code")
    location_name = fields.Char(string="Location Name")