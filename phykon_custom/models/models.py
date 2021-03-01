# -*- coding: utf-8 -*-
from odoo import fields, models, api
#from odoo.tools.translate import _
from odoo.exceptions import ValidationError

"""
class SurveyToApplicant(models.Model):
    _inherit = 'survey.survey'

    @api.model
    def create(self,vals):
        user = self.env['survey.user_input']
        state = user.state		
        UserInput = super(survey_user_input,self).update(vals)
        #if state=="done":
        vals = {
            'name':"testname",
            'partner_name':"Test Applicant Name",
                
				
        }
        self.env['hr.applicant'].sudo().create(vals)
        return UserInput

"""

class CRMCustom(models.Model):
    _inherit = 'crm.lead'

"""
class CRMLostCustom(models.Model):
    _inherit = 'crm.lead.lost'
"""


#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
# led')),'PIN Status')
	



        


#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
