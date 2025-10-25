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