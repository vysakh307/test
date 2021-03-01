from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, Warning


# URL field for calendar
class CustomCalendar(models.Model):
    _inherit = 'calendar.event'

    url = fields.Char(string="Virtual Location Link")