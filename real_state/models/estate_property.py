import random
from odoo import models, fields, api
from odoo.exceptions import UserError
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
    garden_area = fields.Integer(string="Superficie jardín")
    
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
    tag_ids = fields.Many2many(
        comodel_name="estate.property.tag",
        string="Etiquetas"
    )

    total_area = fields.Integer(
        string="Superficie total",
        compute="_compute_total_area",
        store=True
    )

    offer_ids = fields.One2many(
        comodel_name="estate.property.offer",
        inverse_name="property_id",
        string="Ofertas"
    )

    # 🔹 Punto 19: Campo computado que contiene todos los ofertantes de la propiedad
    offer_partner_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Ofertantes',
        compute='_compute_offer_partner_ids',
        # store=True
    )

    @api.depends('offer_ids.partner_id')
    def _compute_offer_partner_ids(self):
        for record in self:
            partners = record.offer_ids.mapped('partner_id')
            record.offer_partner_ids = partners


    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    best_offer = fields.Float(
        string="Mejor Oferta", 
        compute="_compute_best_offer"
    )   

    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
        for record in self:
            if record.offer_ids:
                record.best_offer = max(record.offer_ids.mapped('price'))
            else:
                record.best_offer = 0.0

    # Onchange del jardín
    @api.onchange('garden')
    def _onchange_garden(self):
        """Actualiza automáticamente el área del jardín según el checkbox."""
        if self.garden:
            self.garden_area = 10
        else:
            self.garden_area = 0

    @api.onchange('expected_price')
    def _onchange_expected_price(self):
        if self.expected_price and self.expected_price < 10000:
            return {
                'warning': {
                    'title': "Precio bajo",
                    'message': "El precio esperado ingresado es menor a 10.000. Verificá si no fue un error de tipeo."
                }
            }

    def action_cancel_property(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("No se puede cancelar una propiedad que ya está vendida.")
            record.state = 'canceled'

    def action_mark_sold(self):
        for record in self:
            if record.state == 'canceled':
                raise UserError("No se puede marcar como vendida una propiedad cancelada.")
            if record.state == 'sold':
                raise UserError("No se puede marcar como vendidad una propiedad que ya fue vendida.")
            record.state = 'sold'

    # 🔹 Punto 20: Botón para generar oferta automática
    def action_generate_automatic_offer(self):
        for record in self:
            if not record.expected_price or record.expected_price <= 0:
                raise UserError("La propiedad debe tener un 'Precio esperado' mayor a 0 para generar una oferta automática.")

            # Buscar contactos activos
            partners = self.env['res.partner'].search([('active', '=', True)])

            # Excluir los que ya ofertaron
            excluded_ids = record.offer_partner_ids.ids
            candidates = partners.filtered(lambda p: p.id not in excluded_ids)

            if not candidates:
                raise UserError("No hay contactos activos disponibles que no hayan hecho ofertas sobre esta propiedad.")

            # Elegir un partner al azar
            partner_id = random.choice(candidates.ids)

            # Calcular precio aleatorio (-30% a +30%)
            variation = random.uniform(-0.3, 0.3)
            price = float(record.expected_price * (1 + variation))

            vals = {
                'price': price,
                'partner_id': partner_id,
                'property_id': record.id,
            }

            # Crear la oferta
            self.env['estate.property.offer'].create(vals)

        return True