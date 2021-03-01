from odoo import fields, models, api
from odoo.exceptions import ValidationError


#Add date field in Recruitment job field	
class JobRecruitment(models.Model):
    
    _inherit = 'hr.job'
	
    target_date = fields.Date(string="Target Date")
	#for department interview form which will use inside applicant
    dept_survey_id = fields.Many2one(
        'survey.survey', "Department Form",
        help="Choose an interview form for this job position and you will be able to print/answer this interview from all applicants who apply for this job")    	
    #assessment_ids = fields.One2many('hr.assessment.items', 'assessment_id')  
"""   
    @api.one
    @api.constrains('weight_line_ids')
    def _check_weight(self):
        ''' To check the total weightage and raises validation error, if total is not 100.'''
        total = [x.weight for x in self.weight_line_ids if x.weight != 0]
        if (total and sum(total) != 100):
            raise ValidationError('Total weightage should be equal to 100.')
            
            
    weight_line_ids = fields.One2many('weight.lines','weight_line_id',string="Weightages")
     
    _sql_constraints = [('name_uniq','unique(name)','The Job Position must be unique.')]
    
class AssessmentWeightageLines(models.Model):
    _name = "weight.lines"
    _description = 'weight Lines'

    assessment_id = fields.Many2one('assessment.config',"Assessment")
    weight = fields.Integer(string="Weightage")
    weight_line_id = fields.Many2one('hr.job',"weight_line_id")

    @api.onchange('weight')
    def onchange_score(self):
        ''' On change func() over the field 'Weightage' to restrict entering the negative values.'''
        if self.weight < 0:
            self.weight = 0
            return {'warning':{'title':('Warning!'),'message':('Value cannot be negative.')}}
        return {}
"""
"""
#Assessment Items(HR Assessment)
class HrAssessment_Items(models.Model):
    _name = 'hr.assessment.items'
	
    assessment_id = fields.Many2one('hr.job')
    assessment_name_id	= fields.Many2one('hr.assessment', 'Assessment Name')
    maximum_mark = 	fields.Integer(string = "Maximum")
    minimum_mark = 	fields.Integer(string = "Threshold")
    actual_score = fields.Integer(string = "Actual")
    notes = fields.Text("Notes")	
	


#Assessment(HR Assessment)
class HrAssessment(models.Model):
    _name = 'hr.assessment'
	
  
    name = fields.Char(string="Name")
    category = 	fields.Char(string="Category")
    measure = fields.Char(string="Mesure / Rating")
"""


