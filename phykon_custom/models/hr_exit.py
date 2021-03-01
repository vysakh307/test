import time

from openerp import models, fields, api, _
from openerp.exceptions import Warning
import logging

class hr_exit_checklist_modified(models.Model):
    _inherit = 'hr.exit.checklist'
    
    department_id = fields.Many2many('hr.department', string="Departments")
    
	
	
	
	
	
	
	
class hr_exit_line_inherit(models.Model):
    _inherit = 'hr.exit.line'

    employee_id = fields.Many2one(related="exit_id.employee_id",string="Employee", type='many2one', relation='hr.employee')
	
	
class hr_exit_inherit(models.Model):
    _inherit = 'hr.exit'
	
    # @api.multi
    # def get_confirm(self):
        # self.state = 'confirm'
        # self.confirm_date = time.strftime('%Y-%m-%d')
        # self.confirm_by_id = self.env.user.id
        # checklist_data = self.env['hr.exit.checklist'].search([('department_id', '=', self.department_id.id)])
        # logging.error('%s', checklist_data)	
	
    @api.multi
    def get_apprv_dept_manager(self):
        self.state = 'approved_dept_manager'
        self.dept_approved_date = time.strftime('%Y-%m-%d')
        self.dept_manager_by_id = self.env.user.id
        checklist_data = self.env['hr.exit.checklist'].search([('department_id', '=', self.department_id.id)])
        logging.error('%s', checklist_data)
        for checklist in checklist_data:
            vals= {'checklist_id': checklist.id,
                   'exit_id':self.id,
                   'state': 'confirm',
                   'responsible_user_id': checklist.responsible_user_id.id,
                   'checklist_line_ids': [(6, 0, checklist.checklist_line_ids.ids)]}
            self.env['hr.exit.line'].create(vals)    
			
			
			