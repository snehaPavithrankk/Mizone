from odoo import models, fields, api


class Building(models.Model):
    _name = 'building.building'
    _description = 'building Master'
    _rec_name = 'bl_name'
    inherit = 'mail.thread'

    image = fields.Binary(string='Image')
    bl_name = fields.Char(string='Building Name', required=True)
    bld_code = fields.Integer(string='Code')
    street1 = fields.Char()
    street2 = fields.Char()
    # country = fields.Char()
    # city = fields.Char()
    # states = fields.Char()
    # zip = fields.Integer('Zip')
    add_image = fields.Binary(string=" Image")

    comment = fields.Text()

    country = fields.Many2one('res.country', required=True)
    city = fields.Char(required=True)
    states = fields.Many2one('res.country.state', required=True)
    zip = fields.Char()

    latitude = fields.Float(string="Latitude")
    longitude = fields.Float(string="Longitude")

    def open_google_maps(self):
        # Replace latitude and longitude with your desired location
        latitude = '37.7749'
        longitude = '-122.4194'

        # Construct the Google Maps URL
        maps_url = f'https://www.google.com/maps?q={latitude},{longitude}'

        # Open Google Maps in a right-side panel
        return {
            'name': 'Google Maps',
            'type': 'ir.actions.act_window',
            'res_model': 'ir.actions.act_url',
            'view_mode': 'form',
            'view_id': self.env.ref('web.view_url_form').id,
            'view_type': 'form',
            'target': 'new',
            'res_id': False,
            'context': {'default_url': maps_url},
            }