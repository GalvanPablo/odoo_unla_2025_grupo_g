from odoo import models, fields

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Etiqueta de propiedad"

    name = fields.Char(string="Nombre", required=True)

    _sql_constraints = [
        (
            "unique_tag_name",
            "unique(name)",
            "El nombre de la etiqueta debe ser único."
        )
    ]