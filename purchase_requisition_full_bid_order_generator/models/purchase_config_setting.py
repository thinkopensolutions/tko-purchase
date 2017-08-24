# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################

from odoo import models, api, fields


class purchase_config_settings(models.TransientModel):
    _inherit = 'purchase.config.settings'

    rfq_to_suppliers = fields.Selection([('a', 'Create RFQ to only suppliers, with all the products'),
                                         ('s', 'Create RFQ to all the suppliers with available products')],
                                        string='RFQ from Bids')

    def get_default_rfq_to_suppliers(self, fields):
        rfq_to_suppliers = self.env['ir.config_parameter'].get_param('rfq_to_suppliers', default=False)
        return dict(rfq_to_suppliers=rfq_to_suppliers)

    def set_default_rfq_to_suppliers(self):
        self.env.user.company_id.write({'rfq_to_suppliers': self.rfq_to_suppliers})
        self.env['ir.config_parameter'].set_param(
            'rfq_to_suppliers', (self.rfq_to_suppliers), groups=['base.group_system'])
