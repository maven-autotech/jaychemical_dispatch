#-*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
from datetime import datetime, timedelta
import logging
import json
from odoo.http import request



class SeqSource(models.Model):
    _name = 'seq.source'

    lot_number = fields.Char("Lot Number")
    counter = fields.Integer("Sequnce No")