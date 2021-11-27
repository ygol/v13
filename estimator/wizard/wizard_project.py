# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class WizardProjectUser(models.TransientModel):
    _name = 'estimator.wizard.project.user'
    _description = 'Wizard pop up window add new user into command'

    name = fields.Many2one('res.users', string="Author")
    role_id = fields.Many2one('estimator.command_roles', string='Role')

    def add_new_user_into_command(self):
        self.env['estimator.command'].create({
            'name': self.name.id,
            'role_id': self.role_id.id
        })
