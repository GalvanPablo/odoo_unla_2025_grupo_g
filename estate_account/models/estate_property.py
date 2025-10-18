from odoo import models, Command
from odoo.exceptions import UserError

class EstateProperty(models.Model):
    _inherit = "estate.property" # Extiende de estate_property

    # Intercepta la acción de estate_property de real_state y la inyecta la creacción de un account_move
    # def action_mark_sold(self):
    #     for property in self
    #         self.env["account.move"].create({
    #             "partner_id": property.buyer_id.id,
    #             "move_type": "out_invoice",
    #             "property_id": property.id,
    #             "line_ids": [
    #                 Command.create({
    #                     "name": property.name,
    #                     "quantity": 1,
    #                     "price_unit": property.selling_price
    #                 }),
    #                 Command.create({
    #                     "name": "Gastos administrativos",
    #                     "quantity": 1,
    #                     "price_unit": 100
    #                 })
    #             ]
    #         })
    #     return super().action_mark_sold()

    def action_mark_sold(self):
        for property in self:
            if property.state in ('canceled', 'sold'):
                continue 

            if not property.buyer_id:
                raise UserError("Una propiedad debe tener un comprador para ser marcada como vendida y facturada.")
            
            self.env["account.move"].create({
                "partner_id": property.buyer_id.id,
                "move_type": "out_invoice",
                "line_ids": [
                    Command.create({
                        "name": property.name,
                        "quantity": 1,
                        "price_unit": property.selling_price,
                    }),
                    Command.create({
                        "name": "Gastos administrativos",
                        "quantity": 1,
                        "price_unit": 100.0
                    })
                ]
            })
        return super(EstateProperty, self).action_mark_sold()

        # https://youtu.be/UwtjbN0Qs3g
        # Segun un comentario que me hizo Javi, el account_move no es necesario crearlo ya que existe como tal
        # Esto solo atrapa la accion y crea el registro de movimiento de cuenta para la facturación