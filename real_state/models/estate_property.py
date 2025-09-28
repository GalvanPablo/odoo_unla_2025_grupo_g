from odoo import models, fields
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Propiedad"

    name = fields.Char(string="Título", required=True)
    description = fields.Text(string="Descripción")
    postcode = fields.Char(string="Código postal")
    date_availability = fields.Date(
        string="Fecha disponibilidad",
        copy=False,
        default=lambda self: fields.Date.context_today(self) + relativedelta(months=3)
    )
    expected_price = fields.Float(string="Precio esperado")
    selling_price = fields.Float(
        string="Precio de venta",
        copy=False
    )
    bedrooms = fields.Integer(string="Habitaciones", default=2)
    living_area = fields.Integer(string="Superficie cubierta")
    facades = fields.Integer(string="Fachadas")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Jardín")
    garden_orientation = fields.Selection(
        string="Orientación del jardín",
        selection=[
            ('north', 'Norte'),
            ('south', 'Sur'),
            ('east', 'Este'),
            ('west', 'Oeste')
        ],
        default="north"
    )
    gardenArea = fields.Integer(string="Superficie jardín")
    
    # Campo state - Ejercicio 21
    state = fields.Selection(
        selection=[
            ("new", "Nuevo"),
            ("offer_received", "Oferta recibida"),
            ("offer_accepted", "Oferta aceptada"),
            ("sold", "Vendido"),
            ("canceled", "Cancelado"),
        ],
        string="Estado",
        required=True,
        copy=False,
        default="new",
    )

    property_type_id = fields.Many2one(
        comodel_name="estate.property.type",
        string="Tipo Propiedad",
        required=True
    )
    
    buyer_id = fields.Many2one(
        "res.partner",
        string="Comprador"
    )

    salesman_id = fields.Many2one(
        'res.users',
        string="Vendedor",
        default=lambda self: self.env.user,
        copy=False,
        index=True
    )
    tag_ids =fields.Many2many(
        comodel_name="estate.property.tag",
        string="Etiquetas"
    )

    offer_ids = fields.One2many(
    comodel_name="estate.property.offer",
    inverse_name="property_id",
    string="Ofertas"
)
