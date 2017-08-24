# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
##############################################################################

from odoo import models, fields, api, _

class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    @api.multi
    def prepare_requisition_purchase_order_line(self, line, product, product_qty, purchase_id, supplier):
        date_order = self.ordering_date or fields.Datetime.now()
        qty = self.env['product.uom'].browse(product.uom_id.id)._compute_quantity(product_qty, product.uom_po_id)
        vals = {'product_id':product.id,
                'product_qty':qty,
                'order_id':purchase_id,
                'product_uom':product.uom_po_id.id,
                'price_unit':product.standard_price,
                'name':product.name,
                'date_planned':fields.Datetime.now()
                }
        line_id = self.env['purchase.order.line'].create(vals)
        return line_id

    @api.multi
    def create_purchase_order(self):
        # Create RFQ to all supplie    rs with products they have from Requisition line
        if self.company_id.rfq_to_suppliers == 's':
            suppliers_dict = {}
            for line in self.line_ids:
                for supplier in line.product_id.seller_ids:
                    supplier_id = supplier.name.id
                    if supplier_id not in suppliers_dict.keys():
                        suppliers_dict[supplier_id] = [{line.product_id: line.product_qty}]
                    else:
                        if suppliers_dict[supplier_id][0].has_key(line.product_id):
                            suppliers_dict[supplier_id][0][line.product_id] = suppliers_dict[supplier_id][0][
                                                                                  line.product_id] + line.product_qty
                        else:
                            suppliers_dict[supplier_id].append({line.product_id: line.product_qty})

            for supplier, product_list in suppliers_dict.iteritems():
                res_partner = self.env['res.partner']
                supplier = res_partner.browse(supplier)
                # create purcahse order
                purchase = self.make_purchase_order(supplier, requisition=False)
                for product_dict in product_list:
                    for product, qty in product_dict.iteritems():
                        # create purchase order line
                        line = self.env['purchase.requisition.line'].search(
                            [('product_id', '=', product.id), ('requisition_id', '=', self.id)], limit=1)
                        p_line = self.prepare_requisition_purchase_order_line(line, product, qty, purchase.id, supplier)
                        p_line.onchange_product_id()
        else:
            # Create RFQ to the supplier which has all the products
            supplier_obj = self.env['res.partner']
            supplierinfo_obj = self.env['product.supplierinfo']
            # Start with all suppliers
            suppliers = supplier_obj.search([('supplier', '=', True)])
            for line in self.line_ids:
                sinfos = supplierinfo_obj.search(
                    [('product_tmpl_id', '=', line.product_id.product_tmpl_id.id)])
                suppliers &= sinfos.mapped('name')
                # Stop condition to avoid the full loop if we don't have suppliers
                if not suppliers:
                    break
            for supplier in suppliers:
                self.make_purchase_order(supplier, requisition=True)

    @api.multi
    def make_purchase_order(self, supplier, requisition):
        vals = {
                'partner_id':supplier.id,
                'requisition_id':self.id,
                }
        purchase_order_id = self.env['purchase.order'].create(vals)
        purchase_order_id.onchange_partner_id()
        if requisition:
            purchase_order_id._onchange_requisition_id()
        return purchase_order_id