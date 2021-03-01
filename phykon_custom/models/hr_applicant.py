from odoo import fields, models, api
from odoo.exceptions import ValidationError
import mysql.connector
import logging
_logger = logging.getLogger(__name__)


 
#Assessment(HR Assessment)
class HRApplicantaddon(models.Model):
    _inherit = 'hr.applicant'	
	
    pin_num = fields.Integer(string="Web PIN")
    pin_status = fields.Selection((('active','Active'),('disabled','Disabled')),'PIN Status')
	# department survey form
    dept_survey_id = fields.Many2one('survey.survey', related='job_id.dept_survey_id', string="Survey")
    dept_response_id = fields.Many2one('survey.user_input', "Response", ondelete="set null", oldname="response")
	
	#this function will work when click the button "start dept interview"
    @api.multi
    def action_start_dept_survey(self):
        self.ensure_one()
        # create a response and link it to this applicant
        if not self.dept_response_id:
            response = self.env['survey.user_input'].create({'survey_id': self.dept_survey_id.id, 'partner_id': self.partner_id.id})
            self.dept_response_id = response.id
        else:
            response = self.dept_response_id
        # grab the token of the response and start surveying
        return self.dept_survey_id.with_context(survey_token=response.token).action_start_dept_survey()

	#this function will work when click the button "start dept interview"
    @api.multi
    def action_print_dept_survey(self):
        """ If response is available then print this response otherwise print survey form (print template of the survey) """
        self.ensure_one()
        if not self.dept_response_id:
            return self.dept_survey_id.action_print_dept_survey()
        else:
            response = self.dept_response_id
            return self.dept_survey_id.with_context(survey_token=response.token).action_print_dept_survey()

			
    #This function is called when the scheduler goes off
    @api.model
    def process_Webpin_disable_scheduler(self):
        conn = mysql.connector.connect(
        host="192.168.1.11",
        database='phykon_portal',
        user="portal",
        password="portal"
        )
        cursor = conn.cursor(prepared=True)
        cursor.execute("DELETE from cosmos_webpin")
        conn.commit()
        cursor.close()
			
        if (conn.is_connected()):
            conn.close()

        self.search([
            ('pin_status', '=', 'active'),	
        ]).write({
            'pin_status': 'disabled'
        })
        logging.warning("Scheduler Disable function called")						
	
    @api.model
    def process_Webpin_enable_scheduler(self, context=None):
        conn = mysql.connector.connect(
        host="192.168.1.11",
        database='phykon_portal',
        user="portal",
        password="portal"
        )
        cursor = conn.cursor(prepared=True)
        scheduler_line_ids = self.search([
            ('pin_status', '=', 'active'),	
        ])
        
        for scheduler_line_id in scheduler_line_ids :
            email_from = scheduler_line_id.email_from
            pin_num = scheduler_line_id.pin_num
            status = "active"	
            partner_name = scheduler_line_id.partner_name
            cursor.execute("INSERT into cosmos_webpin (name,email,pin,status) VALUES (%s, %s, %s, %s)",(partner_name, email_from, pin_num, status))
        conn.commit()
        cursor.close()
			
        if (conn.is_connected()):
            conn.close()	
        logging.warning("Scheduler Enable function called")				
		
"""			
        SQL = ("select * from hr_applicant where pin_status = 'active'")
        self.env.cr.execute(SQL)
        for row in self.env.cr.fetchall():
            logging.error('%s',(row[1]))	    		

"""



"""
    @api.model
    def action_send_call_letter(self):
        self.ensure_one()
        if not self.dept_response_id:
            return self.dept_survey_id.action_send_call_letter()
        else:
            response = self.dept_response_id
            return self.dept_survey_id.with_context(survey_token=response.token).action_send_call_letter() 
"""
"""
 @api.model
    def process_Webpin_enable_scheduler(self, context=None):
        conn = mysql.connector.connect(
        host="192.168.1.11",
        database='phykon_portal',
        user="portal",
        password="portal"
        )
        cursor = conn.cursor()		
        cr = self._cr
        uid = self._uid
        testv = self.pool.get('hr.applicant')
        scheduler_line_obj = self
        scheduler_line_ids = scheduler_line_obj.search([
            ('pin_status', '=', 'active'),	
        ])
        
        for scheduler_line_id in scheduler_line_ids :
            scheduler_line = self.env['hr.applicant'].browse(scheduler_line_id)
	    #Contains all details from the record in the variable scheduler_line
            #scheduler_line = scheduler_line_obj.browse(cr, uid, scheduler_line_id)
            #scheduler_line = scheduler_line_obj.browse(scheduler_line_id)
            #testvar = "test msssggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg"			
            #print(scheduler_line)
            #_logger.info('murshid: ' + scheduler_line_id)						
            #email_from = scheduler_line.email_from
            logging.error('%s',(testv))	
            #logging.error('%s raised an error', email_from)
            #log("test log")
            print("Hello world")
            #query ="INSERT into cosmos_webpin (email,status) VALUES (%(email_from)s,'active')"

            #cursor.execute(query)
            conn.commit()
            cursor.close()
			
        if (conn.is_connected()):
            conn.close()
"""

	
"""
    def process_Webpin_status_scheduler(self, cr, uid, context=None):
        scheduler_line_obj = self.pool.get('hr.applicant')
		#Contains all ids for the model scheduler.demo
        #scheduler_line_ids = self.pool.get('hr.applicant').search("pin_status")
        scheduler_line_ids = self.env['hr.applicant'].search([('pin_status', '=', 'active')])
		#Loops over every record in the model scheduler.demo
        for scheduler_line_id in scheduler_line_ids :
		#Contains all details from the record in the variable scheduler_line
            scheduler_line =scheduler_line_obj.browse(cr, uid,scheduler_line_id ,context=context)
            pin_status = "disabled"
			#Update the record
            scheduler_line_obj.write(cr, uid, scheduler_line_id, {'pin_status': (pin_status)}, context=context)

"""