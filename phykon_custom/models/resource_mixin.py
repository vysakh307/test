# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
from datetime import timedelta,datetime

from odoo import api, fields, models
from odoo.tools import float_utils
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
import pytz


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


class ResourceMixin(models.AbstractModel):
    _inherit = "resource.mixin"


    def get_work_days_data(self, from_datetime, to_datetime, calendar=None):
        active_tz = self.user_id.tz or self.env.user.tz or 'Asia/Kolkata'

        days_count = 0.0
        actual_leave_hr = 0
        total_work_time = timedelta()
        from_datetime_start = from_datetime
        from_datetime_start = from_datetime_start.replace(hour=00,minute=00)
        to_datetime_end = to_datetime
        to_datetime_end = to_datetime_end.replace(hour=23,minute=59)

        dates = [str((from_datetime_start + timedelta(days=x)).date()) for x in range(
            (to_datetime_end - from_datetime_start).days + 1)]
        
        for date in dates:
            date = datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)
            date_start = date.replace(hour=00,minute=00)
            date_start = to_naive_utc(date_start, self.with_context(tz=active_tz))
            date_stop = date.replace(hour=23,minute=59)
            date_stop = to_naive_utc(date_stop, self.with_context(tz=active_tz))
            domain = ['&', ('employee_id', "=", self.id), '|', '&',
                  ('start', '>=', date_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('start', '<=', date_stop.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), '|', '&',
                  ('stop', '>=', date_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('stop', '<=', date_stop.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), '&',
                  ('start', '<=', date_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('stop', '>=', date_stop.strftime(DEFAULT_SERVER_DATETIME_FORMAT))]
            
            shift_ids = self.env['hr.shift.schedule.complete'].search(domain)
            shift_ids = shift_ids.filtered(lambda shift: shift.start >= date_start.strftime(DEFAULT_SERVER_DATETIME_FORMAT))

            actual_working_time = 0
            leave_time = 0

            for shift in shift_ids:
                shift_start = datetime.strptime(shift.start, DEFAULT_SERVER_DATETIME_FORMAT)
                shift_stop = datetime.strptime(shift.stop, DEFAULT_SERVER_DATETIME_FORMAT)
                # shift_difference = timedelta(hours=24)
                shift_difference = shift_stop - shift_start
                # if shift_start >= date_start and shift_stop <= date_stop:
                #     shift_difference = shift_stop - shift_start
                # if shift_start < date_start and shift_stop <= date_stop:
                #     shift_difference = shift_stop - date_start
                # if shift_start >= date_start and shift_stop > date_stop:
                #     shift_difference = date_stop - shift_start
                actual_working_time += shift_difference / timedelta(hours=1)

                leave_difference = 0
                if from_datetime > shift_stop or to_datetime < shift_start:
                    continue
                if  shift_start <= from_datetime and to_datetime <= shift_stop:
                    leave_difference = to_datetime - from_datetime
                elif from_datetime <= shift_start and to_datetime <= shift_stop:
                    leave_difference = to_datetime - shift_start
                elif shift_start <=  from_datetime and shift_stop <= to_datetime:
                    leave_difference = shift_stop - from_datetime
                else:
                    leave_difference = shift_stop - shift_start
                leave_time += leave_difference / timedelta(hours=1)


            if actual_working_time:
                attendance_fract = leave_time / actual_working_time
                if attendance_fract: 
                    # 0.025 for a relaxation of 6 minutes for every 4 hr
                    if attendance_fract > 0.525:
                        days_count += 1
                    else:
                        days_count += 0.5
                    actual_leave_hr += leave_time
        return {
            'days': days_count,
            'hours': actual_leave_hr,
        }