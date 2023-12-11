from odoo import models, fields, api

class ProjectInherit(models.Model):
    _inherit = 'product.template'

    deposits = fields.Char(string="Deposits")
    rent = fields.Date(string="Rent")
    status = fields.Char()
    free_wifi = fields.Char()
    ac = fields.Char()
    furnitured = fields.Char()
    is_yes = fields.Boolean(string='Yes')
    is_no = fields.Boolean(string='No')
    is_in_construction = fields.Boolean(string='In Construction')

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


