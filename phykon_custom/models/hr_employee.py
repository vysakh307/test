from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, Warning
import pytz
from datetime import datetime, timedelta
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT




def to_naive_user_tz(datetime, record):
    tz_name = record._context.get('tz') or record.env.user.tz
    if not tz_name:
        raise ValidationError(_("Please set the User's Timezone."))
    tz = tz_name and pytz.timezone(tz_name) or pytz.UTC
    return pytz.UTC.localize(datetime.replace(tzinfo=None), is_dst=False).astimezone(tz).replace(tzinfo=None)


def to_naive_utc(datetime, record):
    tz_name = record._context.get('tz') or record.env.user.tz
    if not tz_name:
        raise ValidationError(_("Please set the User's Timezone."))
    tz = tz_name and pytz.timezone(tz_name) or pytz.UTC
    return tz.localize(datetime.replace(tzinfo=None), is_dst=False).astimezone(pytz.UTC).replace(tzinfo=None)


def get_working_shift(self, start, stop, employee_id, shift_id):
    active_tz = self.env.user.tz or "Asia/Kolkata"
    shift_list = []
    while start <= stop:
        working_hours = self.env['resource.calendar.attendance'].search(
                [('dayofweek', '=', start.weekday()), ('calendar_id', '=', shift_id.id)], order='hour_from')

        for working_hour in working_hours:
            shift_dict = {}
            hour_from = working_hour.hour_from
            hour_to = working_hour.hour_to

            if hour_from <= hour_to:
                shift_start = start.replace(hour=int(hour_from), minute=int((hour_from-int(hour_from))*60))
                shift_start = to_naive_utc(shift_start, self.with_context(tz=active_tz))
                shift_start = shift_start.replace(tzinfo=None)

                shift_dict['shift_start'] = shift_start
                    
                shift_end = start.replace(hour=int(hour_to), minute=int((hour_to-int(hour_to))*60))
                shift_end = to_naive_utc(shift_end, self.with_context(tz=active_tz))
                shift_end = shift_end.replace(tzinfo=None)

                shift_dict['shift_end'] = shift_end
                        
                if shift_dict:
                    shift_list.append(shift_dict)
            else:
                shift_start = start.replace(hour=int(hour_from), minute=int((hour_from-int(hour_from))*60))
                shift_start = to_naive_utc(shift_start, self.with_context(tz=active_tz))
                shift_start = shift_start.replace(tzinfo=None)

                shift_dict['shift_start'] = shift_start

                wd = start.weekday()
                date_count = 0
                for x in range(7):
                    date_count += 1
                    if wd == 6:
                        wd = 0
                    else:
                        wd += 1
                    next_working_hour = self.env['resource.calendar.attendance'].search(
                    [('dayofweek', '=', wd), ('calendar_id', '=', shift_id.id)], order='hour_from', limit=1)
                    if next_working_hour:
                        hour_to = next_working_hour.hour_to
                        break
                shift_end = start + timedelta(days=date_count)
                shift_end = shift_end.replace(hour=int(hour_to), minute=int((hour_to-int(hour_to))*60))
                shift_end = to_naive_utc(shift_end, self.with_context(tz=active_tz))
                shift_end = shift_end.replace(tzinfo=None)

                shift_dict['shift_end'] = shift_end
                        
                if shift_dict:
                    shift_list.append(shift_dict)
        start = start + timedelta(days=1)
    return shift_list


#psuedo name field in hr.employee
class HrEmployeePseudo(models.Model):
    _inherit = 'hr.employee'
    
    PsuedoNameEmp = fields.Char(string="Aka")
    resource_calendar_ids = fields.Many2one('resource.calendar', 'Working Hours')
    shift_schedule = fields.One2many('hr.shift.schedule', 'rel_hr_schedule', string="Shift Schedule")
    complete_shift_schedule = fields.One2many('hr.shift.schedule.complete', 'employee_id', string="Complete Shift Schedule")
    working_hours = fields.Many2one('resource.calendar', string='Working Schedule')
    department_id = fields.Many2one('hr.department', string="Department",  required=True)


class HrCompleteSchedule(models.Model):
    _name = 'hr.shift.schedule.complete'

    @api.depends('employee_id', 'start','stop')
    def compute_name(self):
        active_tz = self.env.user.tz or "Asia/Kolkata"
        for shift in self:
            if shift.start and shift.stop:
                start = to_naive_user_tz(datetime.strptime(shift.start, DEFAULT_SERVER_DATETIME_FORMAT), self.with_context(tz=active_tz))
                stop = to_naive_user_tz(datetime.strptime(shift.stop, DEFAULT_SERVER_DATETIME_FORMAT), self.with_context(tz=active_tz))
                shift.name = shift.employee_id.name + '[' + str(start.hour)+':'+str(start.minute)+'-' + str(stop.hour)+':'+str(stop.minute) + ']'

    @api.depends('start','stop')
    def compute_duration(self):
        for shift in self:
            if shift.start and shift.stop:
                duration = shift._get_duration(shift.start, shift.stop)
                shift.duration = duration



    name = fields.Char(compute='compute_name')
    start = fields.Datetime('Start', required=True, help="Start date of an shift")
    stop = fields.Datetime('Stop', required=True, help="Stop date of an shift")

    duration = fields.Float(compute='compute_duration', string='Duration')

    employee_id = fields.Many2one('hr.employee', required=True)
    hr_shift_id = fields.Many2one('resource.calendar', 'Shift')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)

    def _get_duration(self, start, stop):
        """ Get the duration value between the 2 given dates. """
        if start and stop:
            diff = fields.Datetime.from_string(stop) - fields.Datetime.from_string(start)
            if diff:
                duration = float(diff.days) * 24 + (float(diff.seconds) / 3600)
                return round(duration, 2)
            return 0.0

    @api.multi
    @api.constrains('start','stop')
    def _check_time_overlaping(self):
        for record in self:
            stop = record.stop
            start = record.start
            domain = ['&', '&', ('id','!=',record.id), ('employee_id', "=", record.employee_id.id), '|', '&',
                      ('start', '>=', start), ('start', '<=', stop), '|', '&',
                      ('stop', '>=', start), ('stop', '<=', stop), '&',
                      ('start', '<=', start), ('stop', '>=', stop)]

            shift = self.search(domain)
            if shift:
                raise ValidationError(_('You cannot allot one employee to multiple shift at same time.'))


class HrSchedule(models.Model):
    _name = 'hr.shift.schedule'

    start_date = fields.Date(string="Date From", required=True)
    end_date = fields.Date(string="Date To", required=True)
    rel_hr_schedule = fields.Many2one('hr.employee')
    hr_shift = fields.Many2one('resource.calendar', string="Shift", required=True)
    company_id = fields.Many2one('res.company', string='Company')

    @api.onchange('start_date', 'end_date')
    def get_department(self):
        """Adding domain to  the hr_shift field"""
        hr_department = None
        if self.start_date:
            hr_department = self.rel_hr_schedule.department_id.id
        return {
            'domain': {
                'hr_shift': [('hr_department', '=', hr_department)]
            }
        }

    @api.multi
    def write(self, vals):
        self._check_overlap(vals)
        return super(HrSchedule, self).write(vals)

    @api.model
    def create(self, vals):
        self._check_overlap(vals)
        return super(HrSchedule, self).create(vals)

    def _check_overlap(self, vals):
        if vals.get('start_date', False) and vals.get('end_date', False):
            shifts = self.env['hr.shift.schedule'].search([('rel_hr_schedule', '=', vals.get('rel_hr_schedule'))])
            for each in shifts:
                if each != shifts[-1]:
                    if each.end_date >= vals.get('start_date') or each.start_date >= vals.get('start_date'):
                        raise Warning(_('The dates may not overlap with one another.'))
            if vals.get('start_date') > vals.get('end_date'):
                raise Warning(_('Start date should be less than end date.'))
        return True


class HrEmployeeShift(models.Model):
    _inherit = 'resource.calendar'

    def _get_default_attendance_ids(self):
        return [
            (0, 0, {'name': _('Monday Morning'), 'dayofweek': '0', 'hour_from': 8, 'hour_to': 17}),
            (0, 0, {'name': _('Tuesday Morning'), 'dayofweek': '1', 'hour_from': 8, 'hour_to': 17}),
            (0, 0, {'name': _('Wednesday Morning'), 'dayofweek': '2', 'hour_from': 8, 'hour_to': 17}),
            (0, 0, {'name': _('Thursday Morning'), 'dayofweek': '3', 'hour_from': 8, 'hour_to': 17}),
            (0, 0, {'name': _('Friday Morning'), 'dayofweek': '4', 'hour_from': 8, 'hour_to': 17}),
        ]

    color = fields.Integer(string='Color Index')
    hr_department = fields.Many2one('hr.department', string="Department", required=True)
    #sequence = fields.Integer(string="Sequence", required=True, default=1)
    attendance_ids = fields.One2many(
        'resource.calendar.attendance', 'calendar_id', 'Workingssss Time',
        copy=True, default=_get_default_attendance_ids)

    # @api.constrains('sequence')
    # def validate_seq(self):
        # if self.hr_department.id:
            # record = self.env['resource.calendar'].search([('hr_department', '=', self.hr_department.id),
                                                           # ('sequence', '=', self.sequence),
                                                           # ('company_id', '=', self.company_id.id)
                                                           # ])
            # if len(record) > 1:
                # raise ValidationError("One record with same sequence is already active."
                                      # "You can't activate more than one record  at a time")

"""  
    @api.onchange('department_id')
    def _department_onchange(self):
        res = {}
            res['domain']={'job_id':[('department_id', '=', job_id.department_id.id)]}
        return res
"""	
"""	
#psuedo name field in res.users
class PseudoUser(models.Model):
    
    _inherit = 'res.users'
    
	
    #pseudo_name_res = fields.Char(string="Aka")
    
	#create employee from users

    
    @api.model
    def create(self,vals):
        user = super(res_users,self).create(vals)
        if users:
            vals = {
                'name':user.name,
                'user_id':user.id,
                'address_home_id':user.partner_id and user.partner_id.id or False,
				
            }
            self.env['hr.employee'].sudo().create(vals)
        return user


#'PsuedoNameEmp' :user.PsuedoNameRes	
"""
