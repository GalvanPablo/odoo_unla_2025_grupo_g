from odoo import models, fields, api
from datetime import timedelta

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Oferta sobre propiedad"

    price = fields.Float(
        string="Precio",
        required=True
    )

    status = fields.Selection(
        [
            ("accepted", "Aceptada"),
            ("refused", "Rechazada")
        ],
        string="Estado"
    )

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Ofertante",
        required=True
    )

    property_id = fields.Many2one(
        comodel_name="estate.property",
        string="Propiedad",
        required=True
    )

    
    property_type_id = fields.Many2one(
        related="property_id.property_type_id",
        store=True,
        string="Tipo de propiedad"
    )

    validity = fields.Integer(
        string="Validez (días)",
        default=7
    )

    date_deadline = fields.Date(
        string="Fecha límite",
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
        store=True
    )

    @api.depends("validity", "create_date")
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date.date() + timedelta(days=record.validity)
            else:
                record.date_deadline = fields.Date.today() + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            if record.date_deadline and record.create_date:
                delta = record.date_deadline - record.create_date.date()
                record.validity = delta.days



  
