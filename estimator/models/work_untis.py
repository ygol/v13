from odoo import models, fields, api, _


class WorkUnits(models.Model):
    _name = "task_estimation.work_units"
    _description = 'task_estimation.work_units'

    name = fields.Char(string="Name of Unit")
    minutes_to_do = fields.Float(string="Time to do (hh:mm)")
    name_seq = fields.Char(string='Work Unit Reference', required=True, copy=False, readonly=True, index=True,
                           default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('estimator.work_units.sequence') or _('New')

        result = super(WorkUnits, self).create(vals)
        return result
