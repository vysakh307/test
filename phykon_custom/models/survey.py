from odoo import fields, models, api
from odoo.exceptions import ValidationError


class Deptsurvey(models.Model):
    _inherit = 'survey.survey'
    @api.multi
    def action_start_dept_survey(self):
        """ Open the website page with the survey form """
        self.ensure_one()
        token = self.env.context.get('survey_token')
        trail = "/%s" % token if token else ""
        return {
            'type': 'ir.actions.act_url',
            'name': "Start Survey",
            'target': 'self',
            'url': self.with_context(relative_url=True).public_url + trail
        }	
	
    @api.multi
    def action_print_dept_survey(self):
        """ Open the website page with the survey printable view """
        self.ensure_one()
        token = self.env.context.get('survey_token')
        trail = "/" + token if token else ""
        return {
            'type': 'ir.actions.act_url',
            'name': "Print Survey",
            'target': 'self',
            'url': self.with_context(relative_url=True).print_url + trail
        }