from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_type = fields.Selection([
        ('customer', 'Customer'),
        ('supplier', 'Supplier'),
        ('tenant', 'Tenant'),
        ('other', 'Other'),  # You can add more options as needed
    ], string='Partner Type', default='customer')