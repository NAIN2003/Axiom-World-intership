from odoo import fields, models


class ResUsersInherited(models.Model):
    _inherit = "res.users"

    property_ids = fields.One2many(
        "estate.property",  # Target model
        "salesperson_id",  # Inverse field name in the target model
        string="Properties"
    )
