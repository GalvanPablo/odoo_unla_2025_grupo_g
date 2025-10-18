from odoo import models, fields

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Tipos de propiedad"

    name = fields.Char(string="Título", required=True)

    _sql_constraints = [
        (
            "unique_type_name",
            "unique(name)",
            "El nombre del tipo de propiedad debe ser único."
        )
    ]