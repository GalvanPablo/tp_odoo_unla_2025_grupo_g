import random
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SaleChannel(models.Model):
    _name = "sale.channel"
    _description = "Canal de Venta"
    _rec_name = "name"

    name = fields.Char(string="Nombre", required=True)
    code = fields.Char(string="Código", required=True)
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Depósito",
        required=True
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Diario contable",
        required=True
    )

    _sql_constraints = [
        ("unique_code", "unique(code)", "El código del canal debe ser único.")
    ]

    @api.constrains('code')
    def _check_code_not_empty(self):
        for record in self:
            if not record.code or not record.code.strip():
                raise ValidationError("El código no puede estar vacío.")

