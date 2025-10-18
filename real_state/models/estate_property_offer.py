from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Oferta sobre propiedad"

    _sql_constraints = [
        (
            "unique_partner_property_offer",
            "unique(partner_id, property_id)",
            "Un cliente no puede hacer más de una oferta sobre la misma propiedad."
        )
    ]

    price = fields.Float(
        string="Precio",
        required=True
    )

    status = fields.Selection(
        [
            ("accepted", "Aceptada"),
            ("rejected", "Rechazada")
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

    def action_accept_offer(self):
        for offer in self:
            if offer.status == 'accepted':
                raise UserError("Esta oferta ya fue aceptada.")
            
            # 1. Actualizar la propiedad
            prop = offer.property_id
            prop.selling_price = offer.price
            prop.buyer_id = offer.partner_id
            prop.state = 'offer_accepted'

            # 2. Cambiar estado de esta oferta
            offer.status = 'accepted'

            # 3. Rechazar automáticamente las demás ofertas
            other_offers = self.search([
                ('property_id', '=', prop.id),
                ('id', '!=', offer.id)
            ])
        other_offers.write({'status': 'rejected'})
    
    @api.model
    def create(self, vals):
    
     offer = super(EstatePropertyOffer, self).create(vals)

     for record in offer:
        property_obj = record.property_id

        #Valida el estado de la propiedad
        if property_obj.state not in ('new', 'offer_received'):
            raise UserError(
                "No se puede crear una oferta sobre una propiedad en estado '{}'.".format(property_obj.state)
            )

        max_other_offer=max(
            (o.price for o in property_obj.offer_ids if o.id != record.id),
            default=0
        )
        if record.price <= max_other_offer:
            raise UserError(
                "El valor ofertado debe ser mayor a la mejor oferta actual ({}).".format(max_other_offer)
            )

        #Cambia el estado de la propiedad a 'offer_received' una vez creada
        property_obj.state = 'offer_received'

     return offer
 

