from odoo import models, fields, api
from odoo.exceptions import UserError

class BuildingRoom(models.Model):
    _name = 'building.room'
    _description = 'Building Room'

    image = fields.Binary(string='Image')
    name = fields.Char(string='Room Name', required=True)
    room_number = fields.Char(string='Room Number')
    floor = fields.Integer(string='Floor')
    capacity = fields.Integer(string='Capacity')
    building_id = fields.Many2one('building.building', string='Building')
    sales_price = fields.Char(string='Sales Price')
    product_ids = fields.Many2many(
        'product.template',
        string='Products',
        help="Select the products for this room",
        domain="[('s_field', '=', 'available')]"
    )
    # product_ids = fields.Many2many('product.template', string='Products', help="Select the products for this room.")

    @api.model
    def create(self, values):
        # Create the room
        room = super(BuildingRoom, self).create(values)

        # Update the status of selected products to 'sold'
        for product in room.product_ids:
            if product.s_field == 'available':
                product.s_field = 'sold'

        return room

    def write(self, values):
        if 'product_ids' in values:
            new_products = self.env['product.template'].browse(values['product_ids'][0][2])
            for product in new_products:
                if product.s_field == 'available':
                    product.s_field = 'sold'

            # Update the status of products that were removed
            removed_products = self.product_ids - new_products
            for product in removed_products:
                if product.s_field == 'available':
                    product.s_field = 'sold'

        return super(BuildingRoom, self).write(values)
    room_type = fields.Selection([
        ('office', 'Office'),
        ('conference', 'Conference Room'),
        ('meeting', 'Meeting Room'),
        ('break', 'Break Room'),
        ('other', 'Other')
    ], string='Room Type', default='office')
    facilities = fields.Text(string='Facilities')

    s_field = fields.Selection([
            ('available', 'Available'),
            ('sold', 'Sold')
        ], string='Status', default='available')

    def action_available(self):
        for x in self:
            x.s_field = 'available'

    def action_sold(self):
        for x in self:
            x.s_field = 'sold'

    # @api.constrains('product_ids')
    # def _check_duplicate_products(self):
    #     for room in self:
    #         duplicate_products = room.product_ids.filtered(lambda p: p in self.env['building.room'].search(
    #             [('id', '!=', room.id), ('product_ids', 'in', p.ids)]).mapped('product_ids'))
    #         if duplicate_products:
    #             raise UserError("The following products are already selected in other rooms: %s" % (
    #                 ", ".join(duplicate_products.mapped('name'))))