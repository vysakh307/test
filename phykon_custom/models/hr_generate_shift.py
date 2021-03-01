# -*- coding: utf-8 -*-
###################################################################################
#    A part of OpenHrms Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Saritha Sahadevan (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
from odoo import models, fields, api
from datetime import timedelta, date
from datetime import datetime
#from dateutil.relativedelta import relativedelta
import logging
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT

from odoo.addons.phykon_custom.models.hr_employee import get_working_shift


class HrGenerateShift(models.Model):
    _name = 'hr.shift.generate'

    hr_department = fields.Many2one('hr.department', string="Department", required=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    company_id = fields.Many2one('res.company', string='Company')
    hr_shift = fields.Many2one('resource.calendar', string="Shift", required=True)
    employee_ids = fields.Many2many('hr.employee', 'shift_employee_rel', 'employee_id', 'hr_shift', string="Employee")

    @api.onchange('hr_department')
    def get_shift(self):
        hr_department = None
        hr_department = self.hr_department.id
        self.employee_ids = None
        self.hr_shift = None
        return {
            'domain': {
                'hr_shift': [('hr_department', '=', hr_department)],
                'employee_ids':[('department_id', '=', hr_department)]
            }
        }


    def action_schedule_shift(self):
        """Create mass schedule for all departments based on the shift scheduled in corresponding employee's """

        if self.hr_department:
            for employee_id in self.employee_ids:

                start_date = datetime.strptime(self.start_date, DEFAULT_SERVER_DATE_FORMAT)
                end_date = datetime.strptime(self.end_date, DEFAULT_SERVER_DATE_FORMAT)

                shift_list = get_working_shift(self, start_date, end_date, employee_id, self.hr_shift)

                print ('shift_list===========',shift_list)
                # print (sdfsdf)
                shift_ids = []
                for shift in shift_list:
                    shift_ids.append((0, 0, {
                                'hr_shift_id': self.hr_shift.id,
                                'start': shift.get('shift_start'),
                                'stop': shift.get('shift_end'),
                                }))

                employee_id.write({'complete_shift_schedule': shift_ids})
                #     # else:
                #     #     shift_ids_2 = [(0, 0, {
                #     #         'hr_shift': "OFF",
                #     #         'start_date': start_date,
                #     #         'end_date': start_date
                #     #         })]			

                #     employee_id.complete_shift_schedule = shift_ids_2
                #     start_date = temp_date





