from odoo import fields, models

from odoo.exceptions import ValidationError

from odoo import api, fields, models

Class EstateProperties(models.Model):

	_name = "estate.property"

	_description = "Model for Real-Estate Properties"


	name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    data_availability = fields.Date(default=lambda self: fields.Date.today() + relativedelta(months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True)
    bedrooms = fields.Integer(default=2, copy=False)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),
    ])


@api.onchange('garden')
def onchange_garden(self):
    if self.garden:
        self.garden_area = 10.0
        self.garden_orientation = 'north'
    else:
        self.garden_area = 0.0
        self.garden_orientation = False
    state = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('canceled', 'Canceled'),
    ], required=True, copy=False, default='new')
     name = fields.Char(string="Title", required=True)
     buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
     salesperson_id = fields.Many2one(
    "res.users",
    string="Salesperson",
    default=lambda self: self.env.user,
    readonly=True,
    copy=False,
)
tag_ids = fields.Many2many(
        "estate.property.tag",
        string="Tags",
        help="Tags associated with the property",
        widget="many2many_tags",
)
price = fields.Float(string="Price", required=True)
    status = fields.Selection(
        [("accepted", "Accepted"), ("refused", "Refused")],
        string="Status",
        required=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Buyer",
        required=True,
        ondelete="cascade",
        index=True,
        domain="[('customer', '=', True)]",
    )
    property_id = fields.Many2one(
        "estate.property",
        string="Property",
        required=True,
        ondelete="cascade",
        index=True,
    )


def action_accept_offer(self):
    self.ensure_one()
    if self.state != 'accepted':
        self.state = 'accepted'
        self.property_id.state = 'offer_accepted'
        self.property_id.buyer_id = self.buyer_id
        self.property_id.selling_price = self.price


def action_refuse_offer(self):
    self.ensure_one()
    if self.state != 'refused':
        self.state = 'refused'
        self.property_id.state = 'offer_received'


@api.onchange('property_id')
def onchange_property_id(self):
    if self.property_id:
        self.buyer_id = self.property_id.buyer_id
        self.price = self.property_id.selling_price

# Rest of the fields...

def _check_salesperson_employee(self):
    for record in self:
        if record.salesperson_id and not record.salesperson_id.employee:
            raise ValidationError("Salesperson must be an employee.")



_sql_constraints = [
    ("salesperson_employee_check", "CHECK (1=1)", "Salesperson must be an employee.")
]

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"

    living_area = fields.Float(string="Living Area (sqm)", track_visibility="onchange")
    garden_area = fields.Float(string="Garden Area (sqm)", track_visibility="onchange")
    total_area = fields.Float(compute="_compute_total_area", string="Total Area (sqm)", store=True)

    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    highest_offer = fields.Float(compute="_compute_highest_offer", string="Highest Offer", store=True)
    _sql_constraints = [
        ("positive_expected_price", "CHECK (expected_price > 0)", "Expected price must be strictly positive!"),
        ("positive_selling_price", "CHECK (selling_price >= 0)", "Selling price must be positive!"),
    ]

    class EstatePropertyTag(models.Model):
        _name = "estate.property.tag"
        _description = "Real Estate Property Tag"

        name = fields.Char(string="Name")

        _sql_constraints = [
            ("unique_property_tag_name", "UNIQUE (name)", "Property tag name must be unique!"),
        ]

    class EstatePropertyType(models.Model):
        _name = "estate.property.type"
        _description = "Real Estate Property Type"

        name = fields.Char(string="Name")

        _sql_constraints = [
            ("unique_property_type_name", "UNIQUE (name)", "Property type name must be unique!"),
        ]

    class EstatePropertyOffer(models.Model):
        _name = "estate.property.offer"
        _description = "Real Estate Property Offer"

        price = fields.Float(string="Price")

        _sql_constraints = [
            ("positive_offer_price", "CHECK (price > 0)", "Offer price must be strictly positive!"),
        ]

        @api.constrains("expected_price", "selling_price")
        def _check_selling_price(self):
            for record in self:
                if record.selling_price < (record.expected_price * 0.9):
                    raise ValidationError("Selling price cannot be lower than 90% of the expected price!")

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_highest_offer(self):
        for record in self:
            record.highest_offer = max(record.offer_ids.mapped("price"))

    class EstatePropertyOffer(models.Model):
        _name = "estate.property.offer"
        _description = "Property Offer"

        property_id = fields.Many2one("estate.property", string="Property")
        price = fields.Float(string="Price")
        validity = fields.Integer(string="Validity", default=7)
        date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline",
                                    string="Validity Date", store=True)

        @api.depends("create_date", "validity")
        def _compute_date_deadline(self):
            for record in self:
                if record.create_date and record.validity:
                    record.date_deadline = record.create_date + relativedelta(days=record.validity)

        def _inverse_date_deadline(self):
            for record in self:
                if record.date_deadline and record.create_date:
                    record.validity = (record.date_deadline - record.create_date).days

    from odoo import fields, models

    class ResUsersInherited(models.Model):
        _inherit = "res.users"

        property_ids = fields.One2many(
            "estate.property",
            "salesperson_id",
            string="Properties"
        )

        available_property_ids = fields.One2many(
            related="property_ids",
            domain=[("state", "in", ["New", "Offer Received"])],
            string="Available Properties",
        )
