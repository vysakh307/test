# -*- coding: utf-8 -*-
{
    'name': "Phykon Custom Applications",

    'summary': """
        Phykon Custom Applications""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Phykon",
    'website': "http://www.phykon.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'hr',
                'base_setup',
                'mail',
                'resource',
                'hr_recruitment',
		        'survey',
                'web',
                'hr_applicant' ,
                'hr_holidays',
	],

     # always loaded
    'data': [
        
        'security/hr_security.xml',
        'security/recruitment_security.xml',
        'security/hr_applicant_security.xml',
        'security/analytic_security.xml',
        'security/hr_holiday.xml',
        'security/survey_security.xml',
        'security/attendance_security.xml',
        'security/hr_employee_security.xml',
        #'security/attendance_security.xml',
        #'views/assessment.xml',
        'views/views.xml',
        'views/hr_job_view.xml',
        #'views/crm_view.xml',
        'views/hr_applicant_view.xml',
        'views/hr_employee_view.xml',
        'views/survey_view.xml',
        'views/templates.xml',
        'views/timesheet_view.xml',
        'views/scheduler.xml',
        'views/attendance_view.xml',
        'views/hr_holidays_view.xml',
        'views/project_view.xml',
        'views/hr_employee_contract_view.xml',
        'views/calendar_view.xml',
        'views/hr_exit_view.xml',
        #'wizard/letter_email_compose_message.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
	'installable': True,
    'application': True,
    'auto_install': False,
}