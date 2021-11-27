# -*- coding: utf-8 -*-

# Copyright © 2021 42loc Creation (<https://odoo-42loc.com/>)
# @author: Eugen Zahoruiko (<intuit07@gmail.com>)
# @author: Taras Feshak (<tarasfeshak@gmail.com>)

{
    'name': "Task estimation",
    'author': "42loc",
    'website': "https://odoo-42loc.com/",
    'summary': """
        Tasks estimation""",
    'description': """
        Long description of module's purpose
    """,
    'category': 'Timesheets',
    'version': '13.0',
    'support': 'intuit07@gmail.com, tarasfeshak@gmail.com',
    'license': 'GPL-3',
    'images': ['static/description/banner.png'],
    'depends': [
        'base',
        'hr',
        'project'
    ],
    'data': [
        'security/estimator_security.xml',
        'security/ir.model.access.csv',
        'wizard/wizard_project_view.xml',
        'views/tasks.xml',
        'views/work_units.xml',
        'data/sequence.xml',
    ],
    'demo': [],
}
