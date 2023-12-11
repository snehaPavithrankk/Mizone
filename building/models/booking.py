from odoo import models, fields, api, _

class BuildingInventory(models.Model):
    _name = 'building.booking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Building Booking'

    # product_lines = fields.One2many('building.booking.product.line', 'booking_id', string='Products', compute='_compute_product_lines', store=True)
    sequence_number = fields.Char(string='Sequence Number', copy=False, readonly=True
                        , default=lambda self: _('Booking Form'))
    customer = fields.Many2one('res.partner', string='Customer', domain=[('partner_type', '=', 'tenant')])
    phone_number = fields.Char(string='Phone Number')
    booking_type = fields.Selection(
        selection=[('room', 'Room'), ('products', 'Inventory')],
        string='Booking Type',
        default='room')
    building_id = fields.Many2one('building.building', string='Building')
    room_id = fields.Many2one('building.room', string='Room/Inventory',domain="[('building_id', '=', building_id)]")
    product_ids = fields.Many2many('product.template', string='Product', widget="many2many_tags")
    booking_date = fields.Date(string='Booking Date', default=lambda self: fields.Date.today())
    rent_start_date = fields.Date(string="Rent start Date")
    billing = fields.Selection(
        [('monthly', 'Monthly'), ('yearly', 'Yearly')],
        string="Billing",
        default='monthly',
    )

    street1 = fields.Char()
    street2 = fields.Char()
    # country = fields.Many2one('res.country', required=True)
    country = fields.Many2one('res.country', required=True)
    city = fields.Char(required=True)
    state = fields.Many2one('res.country.state', required=True)
    zip = fields.Char()
    rent = fields.Float(string='Rent', readonly=True, store=True)

    untaxed_amount = fields.Float(string='Untaxed Amount', compute='_compute_untaxed_amount' , currency_field='currency_id')
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency')

    product_lines = fields.One2many('building.booking.product.line', 'booking_id', string='Products',
                                    compute='_compute_product_lines', store=True, copy=False)

    @api.onchange('booking_type', 'room_id', 'product_ids')
    def _onchange_booking_type(self):

        if self.booking_type == 'room' and self.room_id:
            # Clear existing product lines
            self.product_lines = [(5, 0, 0)]
            product_lines = []

            # Get the selected product IDs
            selected_product_ids = self.product_ids.ids
            # selected_product_ids = self.product_lines.mapped('product_ids.id')

            # Filter available products based on what hasn't been selected
            available_products = self.room_id.product_ids.filtered(
                lambda product: product.id not in selected_product_ids)

            for product in available_products:
                line = self.env['building.booking.product.line'].new({
                    'product_ids': product.id,
                    'label': product.name,
                    'quantity': 1,
                })
                line._onchange_product_ids()  # Trigger the onchange to compute price and subtotal
                product_lines.append((0, 0, line._convert_to_write(line._cache)))
            self.product_lines = product_lines

    @api.depends('booking_type', 'room_id.product_ids')
    def _compute_product_lines(self):
        for booking in self:
            if booking.booking_type == 'room' and booking.room_id:
                product_lines = []
                for product in booking.room_id.product_ids:
                    line = self.env['building.booking.product.line'].new({
                        'product_ids': product.id,
                        'label': product.name,
                        'quantity': 1,
                    })
                    line._onchange_product_ids()  # Trigger the onchange to compute price and subtotal
                    product_lines.append((0, 0, line._convert_to_write(line._cache)))
                booking.product_lines = product_lines
            else:
                booking.product_lines = []

    @api.depends('product_lines.subtotal')
    def _compute_untaxed_amount(self):
        for record in self:
            record.untaxed_amount = sum(line.price for line in record.product_lines)

    @api.depends('product_lines.subtotal')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(line.subtotal for line in record.product_lines)

    def action_print_booking(self):
        self.ensure_one()
        action = self.env.ref('building.action_report_building_booking')
        return action.report_action(self)

    # @api.onchange('product_ids', 'room_id')
    # def _onchange_product_or_room(self):
    #     if self.booking_type == 'room' and self.room_id:
    #         total_rent = self.room_id.sales_price
    #         if self.product_ids:
    #             product_prices = self.product_ids.mapped('list_price')
    #             total_rent += sum(product_prices)
    #         self.rent = total_rent
    #     else:
    #         self.rent = 0

    # @api.onchange('product_ids', 'room_id')
    # def _onchange_product_or_room(self):
    #     if self.room_id:
    #         total_rent = self.room_id.sales_price
    #         if self.product_ids:
    #             product_prices = self.product_ids.mapped('list_price')
    #             total_rent += sum(product_prices)
    #         self.rent = total_rent
    #     else:
    #         self.rent = 0
    #

    status = fields.Selection(
        selection=[('draft', 'Draft'), ('sold', 'Sold')],
        string='Status',
        default='draft')

    room_s_field = fields.Selection(
        related='room_id.s_field',
        string='Room Status',
        readonly=True,
        store=False
    )

    product_s_field = fields.Selection(
        related='product_ids.s_field',
        string='Product Status',
        readonly=True,
        store=False
    )

    # def action_set_to_sold(self):
    #     self.status = 'sold'
    #     if self.room_id:
    #         self.room_id.write({'s_field': 'sold'})
    #     if self.product_ids:
    #         self.product_ids.write({'s_field': 'sold'})

    def action_set_to_sold(self):
        for booking in self:
            booking.status = 'sold'
            # Update s_field of selected products to 'sold'
            for product_line in booking.product_lines:
                product_line.product_ids.action_sold()

            # Update s_field of selected room to 'sold'
            if booking.booking_type == 'room' and booking.room_id:
                booking.room_id.s_field = 'sold'

            return True

    # @api.model
    # def create(self, vals):
    #     if vals.get('sequence_number', 'New') == 'New':
    #         vals['sequence_number'] = self.env['ir.sequence'].next_by_code('building.booking.sequence') or 'New'
    #     return super(BuildingInventory, self).create(vals)

    @api.model
    def create(self, vals):
        if vals.get('sequence_number', _('New')) == _('New'):
            vals['sequence_number'] = self.env['ir.sequence'].next_by_code('building.booking')
        return super(BuildingInventory, self).create(vals)

    def name_get(self):
        res = []
        for record in self:
            name = record.sequence_number
            res.append((record.id, name))
        return res

    @api.onchange('building_id')
    def onchange_building_id(self):
        if self.building_id:
            available_rooms = self.env['building.room'].search(
                [('building_id', '=', self.building_id.id), ('s_field', '=', 'available')])
            return {'domain': {'room_id': [('id', 'in', available_rooms.ids)]}}

    @api.onchange('customer')
    def _onchange_customer(self):
        if self.customer:
            self.street1 = self.customer.street
            self.street2 = self.customer.street2
            self.country = self.customer.country_id
            self.city = self.customer.city
            self.state = self.customer.state_id
            self.zip = self.customer.zip
            self.phone_number = self.customer.mobile



class BuildingBookingProductLine(models.Model):
    _name = 'building.booking.product.line'
    _description = 'Building Booking Product Line'

    product_ids = fields.Many2one('product.template', string='Product', domain="[('s_field', '=', 'available')]")
    label = fields.Char(string='Label')
    quantity = fields.Integer(string='Quantity', default=1)
    price = fields.Float(string='Price', related='product_ids.list_price', readonly=True)
    subtotal = fields.Float(string='Subtotal')
    tax_ids = fields.Many2many('account.tax', string='Taxes', domain=[('type_tax_use', '=', 'sale')])

    booking_id = fields.Many2one('building.booking', string='Booking')

    # def _compute_subtotal(self):
    #     for line in self:
    #         taxes = line.tax_ids.mapped('amount')
    #         subtotal = line.quantity * line.price * (1 + sum(taxes) / 100.0)
    #         line.subtotal = subtotal

    # def _compute_tax_amount(self):
    #     for line in self:
    #         taxes = line.tax_ids.compute_all(line.price, quantity=line.quantity)['taxes']
    #         line.tax_amount = sum(tax['amount'] for tax in taxes)

    # @api.onchange('product_ids', 'quantity', 'tax_ids')
    # def _onchange_product_ids(self):
    #     if self.product_ids:
    #         self.price = self.product_ids.list_price
    #         self.tax_ids = self.product_ids.taxes_id
    #         self._compute_subtotal()

    @api.onchange('product_ids', 'quantity', 'tax_ids')
    def _onchange_product_ids(self):
        if self.product_ids:
            self.price = self.product_ids.list_price
            self.tax_ids = self.product_ids.taxes_id
            self._compute_subtotal()

        # Update domain for product_ids field to exclude already selected products
        selected_product_ids = self.booking_id.product_lines.mapped('product_ids.id')
        available_products = self.env['product.template'].search([
            ('id', 'not in', selected_product_ids),
            ('s_field', '=', 'available')
        ])

        domain = {'domain': {'product_ids': [('id', 'in', available_products.ids)]}}
        return domain

    def _compute_subtotal(self):
        for line in self:
            taxes = line.tax_ids.compute_all(line.price, quantity=line.quantity)['taxes']
            line.subtotal = line.quantity * line.price + sum(tax['amount'] for tax in taxes)

    @api.model
    def create(self, vals):
        line = super(BuildingBookingProductLine, self).create(vals)
        line._compute_subtotal()
        return line