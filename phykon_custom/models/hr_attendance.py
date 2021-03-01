from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import calendar
import pytz
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class HRAttendance1(models.Model):
    _inherit = 'hr.attendance'

    date_from = fields.Date(string='Date from', default="2020-08-01")
    date_to = fields.Date(string='Date to', default="2020-08-28")


"""
    def _default_my_date1(self):
        return fields.Date.context_today(self)
    
    def _default_my_date2(self):
        return fields.Date.context_today(self)

    my_date = fields.Date(string='My Date', default=_default_my_date)

    date_from = fields.Datetime(default=timezone('Asia/Baghdad').localize(dt.datetime.today()).replace(hour=1,minute=20))
    date_to = fields.datetime(string="Date to")
"""

class HRAttendancedatewise(models.Model):
    _name = 'hr.attendance.datewise'

    #employee_id = fields.Many2one('hr.employee', string="Employee")
    date_from = fields.Date("Date from")
    date_to = fields.Date("Date to")
    attendance_sheet_ids = fields.One2many("hr.attendance.datewise.line", "name_id")

    @api.multi
    def get_attendance(self, data):
        """Get Attendance History Of Employee."""
        attendance_ids = self.env['hr.attendance'].search([
            ('check_in', '=', self.date_from)])
        lst = []
        vals = {}
        date_from = datetime.strptime(
            self.date_from, DEFAULT_SERVER_DATE_FORMAT)

        employee_ids = self.env['hr.employee']
        self.attendance_sheet_ids.unlink()

        for emp in employee_ids:
            vals = {}
            if emp not in lst:
                lst.append(emp)
                #vals = self._calc_current_attendance(attendance_ids, date)
                vals.update({'name_id': self.id, 'date': date})
                vals.update({'status': 'weekday'})

                flage=True
                if flage and vals:
                    self.env['hr.attendance.datewise.line'].create(vals)
        self.date_from.attendance_sheet_id = self.id or False


class Attendancesheetline(models.Model):
    """Attendance Sheet Line."""

    _name = 'hr.attendance.datewise.line'
    _description = "Attendance Sheet Line"

    date = fields.Date("Date")
    note = fields.Text("Note")
    name_id = fields.Many2one("hr.attendance.datewise", string="name")
