from odoo import models, fields, api

class SaleOrder(models.Model):
    # Hereda de 'sale.order' para agregar la funcionalidad de Canales de Venta.
    _inherit = 'sale.order'

    # --- Punto 2a: Agregar campo sale_channel_id (obligatorio) ---
    sale_channel_id = fields.Many2one(
        comodel_name='sale.channel', 
        string='Canal de Venta',
        required=True,
        tracking=True,
        help="Seleccione el canal de venta para esta orden."
    )

    # --- Punto 2b: Implementar @api.onchange ---
    @api.onchange('sale_channel_id')
    def _onchange_sale_channel_id(self):
        # Al cambiar el canal de venta, se actualiza automáticamente
        # el depósito (almacén) de la orden de venta.
        if self.sale_channel_id:
            # Asigna el depósito definido en el canal a la orden de venta
            self.warehouse_id = self.sale_channel_id.warehouse_id
        else:
            # Si se quita el canal, se limpia el campo de depósito
            self.warehouse_id = False

        # --- Punto 2b (segunda mitad): Forzar que el picking use el depósito del canal ---
    def _create_delivery_group(self):
        """Sobrescribimos este método para asegurarnos que el grupo de entregas 
        use el almacén correcto del canal."""
        res = super()._create_delivery_group()
        if self.sale_channel_id and self.procurement_group_id:
            self.procurement_group_id.warehouse_id = self.sale_channel_id.warehouse_id
        return res

    def _create_picking(self):
        """Asegurar que las entregas creadas hereden el canal y almacén correcto."""
        pickings = super()._create_picking()
        for picking in pickings:
            picking.sale_channel_id = self.sale_channel_id.id
            if self.sale_channel_id.warehouse_id:
                picking.picking_type_id = self.sale_channel_id.warehouse_id.out_type_id
        return pickings

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # --- Punto 2d (parte stock): Propagar el canal de venta ---
    sale_channel_id = fields.Many2one(
        comodel_name='sale.channel',
        string='Canal de Venta',
        readonly=True,
        help="Canal de venta desde el cual se originó esta entrega."
    )
    
class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_channel_id = fields.Many2one(
        'sale.channel',
        string='Canal de Venta',
        readonly=True,
        copy=False
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Cuando se crean facturas desde una orden de venta,
        se hereda el canal y el diario del canal."""
        moves = super().create(vals_list)
        for move in moves:
            if move.invoice_origin:
                sale_order = self.env['sale.order'].search([('name', '=', move.invoice_origin)], limit=1)
                if sale_order and sale_order.sale_channel_id:
                    move.sale_channel_id = sale_order.sale_channel_id
                    if sale_order.sale_channel_id.journal_id:
                        move.journal_id = sale_order.sale_channel_id.journal_id
        return moves