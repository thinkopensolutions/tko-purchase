# -*- coding: utf-8 -*-
from odoo import models, fields


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')], related='order_id.invoice_status')
