import logging
import math
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools import float_compare, float_round
from odoo.tools.translate import _
import datetime
from datetime import datetime
import pytz

from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT


_logger = logging.getLogger(__name__)

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


class Holidays(models.Model):
    _inherit = 'hr.holidays'


    from_date = fields.Date('Start Date', readonly=True, index=True, copy=False,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, track_visibility='onchange')
    to_date = fields.Date('End Date', readonly=True, copy=False,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, track_visibility='onchange')
    from_time = fields.Float('Start Time', readonly=True, copy=False,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, track_visibility='onchange')
    to_time = fields.Float('Start Time', readonly=True, copy=False,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, track_visibility='onchange')


    @api.multi
    def _check_security_action_approve(self):
        if not self.env.user.has_group('phykon_custom.group_leave_approver') and not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only Approver or HR can approve leave requests t.'))


    @api.multi
    def _check_security_action_validate(self):
        if not self.env.user.has_group('phykon_custom.group_leave_approver') and not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only Approver can approve leave requests.'))

    @api.multi
    def _check_security_action_refuse(self):
        if not self.env.user.has_group('phykon_custom.group_leave_approver') and not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only Approver or HR can approve leave requests.'))

    def _check_state_access_right(self, vals):
        if vals.get('state') and vals['state'] not in ['draft', 'confirm', 'cancel'] and not self.env.user.has_group('hr_holidays.group_hr_holidays_user') and not self.env[
            'res.users'].has_group('phykon_custom.group_leave_approver'):
            return False
        return True

    @api.multi
    def _notification_recipients(self, message, groups):
        """ Handle HR users and officers recipients that can validate or refuse holidays
        directly from email. """
        groups = super(Holidays, self)._notification_recipients(message, groups)

        self.ensure_one()
        hr_actions = []
        if self.state == 'confirm':
            app_action = self._notification_link_helper('controller', controller='/hr_holidays/validate')
            hr_actions += [{'url': app_action, 'title': _('Approve')}]
        if self.state in ['confirm', 'validate', 'validate1']:
            ref_action = self._notification_link_helper('controller', controller='/hr_holidays/refuse')
            hr_actions += [{'url': ref_action, 'title': _('Refuse')}]

        new_group = (
            'group_hr_holidays_user', lambda partner: bool(partner.user_ids) and any(
                user.has_group('phykon_custom.group_leave_approver') or user.has_group('hr_holidays.group_hr_holidays_user') for user in partner.user_ids), {
                'actions': hr_actions,
            })

        return [new_group] + groups

    @api.multi
    def action_approve(self):
        # if double_validation: this method is the first approval approval
        # if not double_validation: this method calls action_validate() below
        self._check_security_action_approve()

        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)


        for holiday in self:
            if holiday.state != 'confirm':
                raise UserError(_('Leave request must be confirmed ("To Approve") in order to approve it.'))
            if holiday.employee_id.user_id.id == self.env.uid:
               raise UserError(_('Can not approve own Leave!'))

            if holiday.double_validation:
                return holiday.write({'state': 'validate1', 'first_approver_id': current_employee.id})
            else:
                holiday.action_validate()

    @api.model
    def create(self, values):
        res = super(Holidays, self.with_context(holiday_create=True)).create(values)
        return res

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        res = super(Holidays, self)._onchange_employee_id()
        employee_id = self.employee_id
        if employee_id and self.date_from and not self._context.get('holiday_create', False):
            active_tz = employee_id.user_id.tz or self.env.user.tz or 'Asia/Kolkata'
            date = datetime.strptime(self.date_from, DEFAULT_SERVER_DATETIME_FORMAT)
            calendar_date_start = date.replace(hour=0,minute=0, second=0)
            date_start = to_naive_utc(calendar_date_start, self.with_context(tz=active_tz))
            date_stop = date.replace(hour=23,minute=59, second=59)
            date_stop = to_naive_utc(date_stop, self.with_context(tz=active_tz))
            domain = ['&', ('employee_id', "=", employee_id.id), '|', '&',
                  ('start', '>=', date_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('start', '<=', date_stop.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), '|', '&',
                  ('stop', '>=', date_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('stop', '<=', date_stop.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), '&',
                  ('start', '<=', date_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('stop', '>=', date_stop.strftime(DEFAULT_SERVER_DATETIME_FORMAT))]
            
            # shift_ids = self.env['hr.shift.schedule.complete'].search(domain, limit=1, order='start')
            shift_ids = self.env['hr.shift.schedule.complete'].search(domain, order='start')
            for shift in shift_ids:
                shift_start_temp = to_naive_user_tz(datetime.strptime(shift.start, DEFAULT_SERVER_DATETIME_FORMAT), self.with_context(tz=active_tz))
                if shift_start_temp >= calendar_date_start:
                    shift_id = shift
                    
            if shift_id:
                shift_start = datetime.strptime(shift_id.start, DEFAULT_SERVER_DATETIME_FORMAT)
                shift_stop = datetime.strptime(shift_id.stop, DEFAULT_SERVER_DATETIME_FORMAT)

                
                naive_shift_start = to_naive_user_tz(shift_start, self.with_context(tz=active_tz))
                naive_shift_stop = to_naive_user_tz(shift_stop, self.with_context(tz=active_tz))

                self.date_from = naive_shift_start.replace(hour=shift_start.hour,minute=shift_start.minute)
                self.date_to = naive_shift_stop.replace(hour=shift_stop.hour,minute=shift_stop.minute)

                self.from_date = naive_shift_start.date()
                self.to_date = naive_shift_stop.date()

                self.from_time = naive_shift_start.hour+naive_shift_start.minute/60
                self.to_time = naive_shift_stop.hour+naive_shift_stop.minute/60
        self._onchange_date_from()
        self._onchange_date_to()
        return res



    @api.onchange('from_date')
    def _onchange_from_date(self):
        if self.from_date and self.employee_id:
            employee_id = self.employee_id
            active_tz = employee_id.user_id.tz or self.env.user.tz or 'Asia/Kolkata'
            if employee_id:
                date = datetime.strptime(self.from_date, DEFAULT_SERVER_DATE_FORMAT)
                calendar_date_start = date.replace(hour=0,minute=0, second=0)
                date_start = to_naive_utc(calendar_date_start, self.with_context(tz=active_tz))
                date_stop = date.replace(hour=23,minute=59, second=59)
                date_stop = to_naive_utc(date_stop, self.with_context(tz=active_tz))
                domain = ['&', ('employee_id', "=", employee_id.id), '|', '&',
                      ('start', '>=', date_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('start', '<=', date_stop.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), '|', '&',
                      ('stop', '>=', date_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('stop', '<=', date_stop.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), '&',
                      ('start', '<=', date_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('stop', '>=', date_stop.strftime(DEFAULT_SERVER_DATETIME_FORMAT))]
                
                # shift_id = self.env['hr.shift.schedule.complete'].search(domain, limit=1)
                shift_ids = self.env['hr.shift.schedule.complete'].search(domain, order='start')
                for shift in shift_ids:
                    shift_start_temp = to_naive_user_tz(datetime.strptime(shift.start, DEFAULT_SERVER_DATETIME_FORMAT), self.with_context(tz=active_tz))
                    if shift_start_temp >= calendar_date_start:
                        shift_id = shift

                if shift_id:
                    shift_start = datetime.strptime(shift_id.start, DEFAULT_SERVER_DATETIME_FORMAT)
                    self.date_from = shift_start.replace(hour=shift_start.hour,minute=shift_start.minute)
                    naive_shift_start = to_naive_user_tz(shift_start, self.with_context(tz=active_tz))
                    self.from_time = naive_shift_start.hour+naive_shift_start.minute/60


    @api.onchange('to_date')
    def _onchange_to_date(self):
        if self.to_date and self.employee_id:
            employee_id = self.employee_id
            active_tz = employee_id.user_id.tz or self.env.user.tz or 'Asia/Kolkata'
            if employee_id:
                date = datetime.strptime(self.to_date, DEFAULT_SERVER_DATE_FORMAT)
                date_start = date.replace(hour=0,minute=0, second=0)
                date_start = to_naive_utc(date_start, self.with_context(tz=active_tz))
                calendar_date_stop = date.replace(hour=23,minute=59, second=59)
                date_stop = to_naive_utc(calendar_date_stop, self.with_context(tz=active_tz))
                domain = ['&', ('employee_id', "=", employee_id.id), '|', '&',
                      ('start', '>=', date_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('start', '<=', date_stop.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), '|', '&',
                      ('stop', '>=', date_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('stop', '<=', date_stop.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), '&',
                      ('start', '<=', date_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('stop', '>=', date_stop.strftime(DEFAULT_SERVER_DATETIME_FORMAT))]
                
                # shift_id = self.env['hr.shift.schedule.complete'].search(domain, limit=1)
                shift_ids = self.env['hr.shift.schedule.complete'].search(domain, order='stop')
                for shift in shift_ids:
                    shift_stop_temp = to_naive_user_tz(datetime.strptime(shift.stop, DEFAULT_SERVER_DATETIME_FORMAT), self.with_context(tz=active_tz))
                    if shift_stop_temp <= calendar_date_stop:
                        shift_id = shift
                if shift_id:
                    shift_stop = datetime.strptime(shift_id.stop, DEFAULT_SERVER_DATETIME_FORMAT)
                    self.date_to = shift_stop.replace(hour=shift_stop.hour,minute=shift_stop.minute)
                    naive_shift_stop = to_naive_user_tz(shift_stop, self.with_context(tz=active_tz))
                    self.to_time = naive_shift_stop.hour+naive_shift_stop.minute/60

    @api.onchange('from_time')
    def _onchange_from_time(self):
        if self.from_time and self.employee_id:
            if self.from_time >= 24:
                raise ValidationError(_('Please check the time format'))
            active_tz = self.employee_id.user_id.tz or self.env.user.tz or 'Asia/Kolkata'
            date_from = datetime.strptime(self.date_from, DEFAULT_SERVER_DATETIME_FORMAT)
            date_from = to_naive_user_tz(date_from, self.with_context(tz=active_tz))
            date_from = date_from.replace(hour=int(self.from_time),minute=int(round((self.from_time-int(self.from_time))*60, 2)))
            self.date_from = to_naive_utc(date_from, self.with_context(tz=active_tz))

    @api.onchange('to_time')
    def _onchange_to_time(self):
        if self.to_time and self.employee_id:
            if self.to_time >= 24:
                raise ValidationError(_('Please check the time format'))
            active_tz = self.employee_id.user_id.tz or self.env.user.tz or 'Asia/Kolkata'
            date_to = datetime.strptime(self.date_to, DEFAULT_SERVER_DATETIME_FORMAT)
            date_to = to_naive_user_tz(date_to, self.with_context(tz=active_tz))
            date_to = date_to.replace(hour=int(self.to_time),minute=int(round((self.to_time-int(self.to_time))*60, 2)))
            self.date_to = to_naive_utc(date_to, self.with_context(tz=active_tz))
