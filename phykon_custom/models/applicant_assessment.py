# -*- coding: utf-8 -*- 
from odoo import fields,models,api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError

class AssessmentConfig(models.Model):
    _name = "assessment.config"
    _description = "Assessment Config"
    
    assessment_seq=fields.Char(string="Assessment Sequence No")
    name = fields.Char(string="Assessment Name")
    assessment_ids = fields.One2many('assessment.lines','assessment_id',string="Assessments")

    _sql_constraints = [ ( 'name_uniq','unique(name)','Assessment name should be unique.')]

    @api.model
    def create(self,vals):
        ''' Method Overridden to
        1) Creates the weightage lines of the related job.
        2) Creates the assessment values.
    '''
        vals['assessment_seq']=self.env['ir.sequence'].next_by_code('assessment.config') or '/'
        obj = super(AssessmentConfig,self).create(vals)
        lst = []
        lis = []
    ### Creates the weightage lines of the related job.
        for line in obj.assessment_ids:
            if line.job_id.id in lst:
                raise ValidationError(_("No duplication of Job position selection"))
            else:
                lst.append(line.job_id.id)

            job_obj = self.env['hr.job'].search([('name','=',line.job_id.name)])
            dic = {
                  'weight_line_ids':[ (0,0,{'assessment_id':obj.id}) ]
                  }
            job_obj.write(dic)
            lis.append((obj.id, line.job_id.id, line.score))

    ### Creates the sequence of Rating values.
        assessment_val_pool = self.env['assessment.values']
        for tup in lis:
            if tup[2] != 0:
                assessment_val_pool.create({'job_id':tup[1], 'assessment_id':tup[0], 'name':'0'})
                for i in range(0, tup[2]):
                    assessment_val_pool.create({'job_id':tup[1], 'assessment_id':tup[0], 'name':i+0.5})
                    assessment_val_pool.create({'job_id':tup[1], 'assessment_id':tup[0], 'name':i+1})                    
        return obj


    @api.multi
    def write(self,vals):
        ''' Method Overridden to
            1) Creates the weightage lines of the related job.
            2) Creates/Updates the  assessment values.
        '''
        job_list=[]
        for line in self.assessment_ids:
            job_list.append(line.job_id.id)

        obj = super(AssessmentConfig,self).write(vals)
        lst = []
        lis = []
        new_job_list = []
    ### Creates the weightage lines of the related department.
        for line in self.assessment_ids:
            new_job_list.append(line.job_id.id)
            if line.job_id.id in lst:
                raise ValidationError(_("No duplication of Job position selection"))
            else:
                lst.append(line.job_id.id)
            if line.job_id.id not in job_list:
                job_obj = self.env['hr.job'].search([('name','=',line.job_id.name)])
                dic = {
                     'weight_line_ids':[ (0,0,{'assessment_id':self.id}) ]
                      }
                job_obj.write(dic)
            lis.append((self.id, line.job_id.id, line.score))

    ### Creates/Updates the  Rating values.
        if vals.get('assessment_ids'):
            assessment_val_pool = self.env['assessment.values']
            for tup in lis:
                assessment_value = assessment_val_pool.search([('job_id','=',tup[1]),('assessment_id','=',tup[0])], limit=1, order = "name desc") or False
                if assessment_value: 
                    if tup[2] > float(assessment_value.name):
                        for i in range(int(float(assessment_value.name)), tup[2]):
                            assessment_val_pool.create({'job_id':tup[1], 'assessment_id':tup[0], 'name':i+0.5})
                            assessment_val_pool.create({'job_id':tup[1], 'assessment_id':tup[0], 'name':i+1})   
                else:
                    if tup[2] != 0:
                        assessment_val_pool.create({'job_id':tup[1], 'assessment_id':tup[0], 'name':'0'})
                        for i in range(0, tup[2]):
                            assessment_val_pool.create({'job_id':tup[1], 'assessment_id':tup[0], 'name':i+0.5})
                            assessment_val_pool.create({'job_id':tup[1], 'assessment_id':tup[0], 'name':i+1})     
        for x in job_list:
            if x not in new_job_list:               job_obj = self.env['hr.job'].browse(x)
        for line in job_obj.weight_line_ids:
                    if line.assessment_id.id == self.id:
                        dic = {
                                'weight_line_ids':[ (2,line.id,0) ]
                              }
                        job_obj.write(dic)
        return obj

    @api.multi
    def unlink(self):
        ''' To restrict the deletion of records which are been referencing from other objects.'''
        for obj in self:
            obj_found = self.env['apl.assessment.lines'].search([('assessment_label_id','=',obj.id),('assessment_id','!=',False)], limit=1) or False
            if obj_found:
                raise ValidationError("You cannot delete the Assessment, as it is Process.")
        return super(AssessmentConfig,self).unlink()


class AssessmentLines(models.Model):
    _name="assessment.lines"
    _description = "Assessment Lines"

    job_id=fields.Many2one('hr.job',string="Job Position")
    score=fields.Integer(string="Full Score",default=3)
    comment=fields.Text(string="Note")
    assessment_id=fields.Many2one('assessment.config', 'Assessment')

    @api.onchange('score')
    def onchange_score(self):
        ''' On change func() over the field 'Full Score' to restrict entering the zero/negative values.'''
        if self.score <= 0:
            self.score = 10
            return {'warning':{'title':('Warning!'),'message':('Value cannot be zero/negative.')}}
        return {}

 

class AssessmentValues(models.Model):
    _name = "assessment.values"
    _description = "Assessment Values"

    name = fields.Char('Value')
    job_id = fields.Many2one('hr.job', 'Job Position')
    assessment_id = fields.Many2one('assessment.config', 'Assessment')


    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        ''' Method Overridden to populate the assessment values in the Evaluation Form lines.'''
        if args is None:
            args = []
        context = self.env.context
        if context is None:
            context={}
        if context.get('eval_job_id') and context.get('eval_assessment_id') and context.get('full_score'):
            full_score = self.env['assessment.values'].browse(context['full_score']).name
            if float(full_score) > 0:
                score_ids = self.env['assessment.values'].search([('job_id','=',context['eval_job_id']),('assessment_id','=',context['eval_assessment_id']),('name','<=',str(full_score))]) or False
                if score_ids:
                    args += [('id','in',score_ids.ids)]
                else:
                    args = [('id','=',False)]
            else:
                args = [('id','=',False)]


        return super(AssessmentValues, self).name_search(name, args=args, operator=operator, limit=limit)

