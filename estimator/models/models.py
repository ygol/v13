# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, _


class Estimator(models.Model):
    _name = 'estimator.task_estimation'
    _description = 'task_estimation.task_estimation'

    project_id = fields.Many2one('project.project', string='Project:', readonly=True)
    name = fields.Many2one('project.task', string="Task Name")
    basic_index = fields.Float(string="Basic Index")
    technical_risks = fields.Selection([
        ('1.1', '1.1'),
        ('1.2', '1.2'),
        ('1.4', '1.4'),
    ], string="Technical risks", default='1.1')
    comprehension_index = fields.Selection([
        ('1.2', '1.2'),
        ('1.5', '1.5'),
        ('1.7', '1.7'),
    ], string="Comprehension index", default='1.2')
    hours_perfect = fields.Float(store=True, compute="total_task_calc", string="Perfect (hours)")
    hours_real_time = fields.Float(store=True, compute="calc_peal_time", string="Real Time (hours)")
    hours_low_performance = fields.Float(store=True, compute="calc_ow_performance", string="Low performance (hours)")
    notes = fields.Text(string="Description")
    unit_works_lines = fields.One2many('task_estimation.lines', 'task_id', string="Tasks Lines")
    name_task_seq = fields.Char(string='Task Estimation Reference', required=True, copy=False, readonly=True,
                                index=True,
                                default=lambda self: _('New'))
    units_id = fields.Many2one('task_estimation.work_units', string='Units ID')
    author = fields.Many2one('estimator.command', string="Author")
    total_task_time = fields.Float(store=True, string="Total Time (hh:mm)")
    tasks_count = fields.Integer(string='Count of author tasks', compute='get_count_tasks')
    task_id = fields.Many2one('estimator.project')
    role = fields.Many2one('estimator.command_roles', string='Role', compute='_compute_author_role', store=True)

    @api.depends('author')
    def _compute_author_role(self):
        for rec in self:
            write_data = rec.env['estimator.command'].search([('id', '=', rec.author.id)])
            rec.role = write_data.role_id

    @api.depends('unit_works_lines')
    def total_task_calc(self):
        for task in self:
            total = 0.0
            for line in task.unit_works_lines:
                total += line.total_time
            task.hours_perfect = total
            task.total_task_time = total

    @api.model
    def create(self, vals):
        if vals.get('name_task_seq', _('New')) == _('New'):
            vals['name_task_seq'] = self.env['ir.sequence'].next_by_code(
                'estimator.task_estimation.sequence') or _('New')

        result = super(Estimator, self).create(vals)
        return result

    @api.depends('hours_perfect', 'comprehension_index', 'technical_risks')
    def calc_peal_time(self):
        self.hours_real_time = self.hours_perfect * float(self.technical_risks) * float(self.comprehension_index)

    @api.depends('hours_perfect')
    def calc_ow_performance(self):
        self.hours_low_performance = self.hours_perfect * 1.4 * 1.7

    def tasks_count_author(self):
        return {
            'name': _('Count_tasks'),
            'domain': [('author.id', '=', self.author.id)],
            'res_model': 'estimator.task_estimation',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def get_count_tasks(self):
        count = self.env['estimator.task_estimation'].search_count([('author.id', '=', self.author.id)])
        self.tasks_count = count


class TaskEstimationLines(models.Model):
    _name = 'task_estimation.lines'
    _description = 'Task Lines'

    workunit_id = fields.Many2one('task_estimation.work_units', string="Work Unit ID", ondelete="cascade")
    quantity = fields.Integer(string="Quantity")
    minutes_to_do = fields.Float(string="Time to perform", related="workunit_id.minutes_to_do")
    task_id = fields.Many2one('estimator.task_estimation')
    total_time = fields.Float(string="Total Time")

    @api.onchange('quantity')
    def total_calc(self):
        for record in self:
            record.total_time = record.workunit_id.minutes_to_do * record.quantity


class Command(models.Model):
    _name = 'estimator.command'
    _description = 'Command'

    name = fields.Many2one('res.users', string="Author")
    role_id = fields.Many2one('estimator.command_roles', string='Role')


class CommandRoles(models.Model):
    _name = 'estimator.command_roles'
    _description = 'Command Roles'

    name = fields.Char('Role')


class Project(models.Model):
    _name = 'estimator.project'
    _description = 'Project'

    name = fields.Many2one('project.project', string='Project:')
    company = fields.Many2one('res.partner', string="Company name", required=True)
    create_date = fields.Datetime(string='Date of creation')
    note = fields.Text(string='Description')
    total_perfect_hours = fields.Float(string="Total Perfect Hours", compute='total_calc_per_hours')
    total_perfect_hours_by_role = fields.Float('Total Perfect Hours by Role', compute='_compute_total_hours_by_role')
    total_real_time = fields.Float(string="Total Real Time", compute='total_calc_real_time')
    total_real_time_by_role = fields.Float(string="Total Real Time by Role", compute='_compute_total_hours_by_role')
    total_low_performance = fields.Float(string="Total Low Performance", compute='total_calc_low_performance')
    total_low_performance_by_role = fields.Float(string="Total Low Performance by Role", compute='_compute_total_hours_by_role')
    tasks = fields.One2many('estimator.task_estimation', 'task_id', string="List of Tasks")
    role_id = fields.Many2one('estimator.command_roles')
    project_risk = fields.Integer('Project Risk, %')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
        ], default='draft', string="Status")

    def add_command(self):
        return {
            "name": _('Command'),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_id": False,
            "res_model": "estimator.command",
            "view_mode": "tree,form",
            "domain": [],
        }

    @api.depends('role_id')
    def _compute_total_hours_by_role(self):
        records = self.env['estimator.task_estimation'].search([('role', '=', self.role_id.id),
                                                                ('project_id', '=', self.name.id)])
        for rec in records:
            self.total_perfect_hours_by_role += rec.hours_perfect
            self.total_real_time_by_role += rec.hours_real_time
            self.total_low_performance_by_role += rec.hours_low_performance
        self.env['estimator.project'].write({
            'total_perfect_hours_by_role': self.total_perfect_hours_by_role,
            'total_real_time_by_role': self.total_real_time_by_role,
            'total_low_performance_by_role': self.total_low_performance_by_role
        })

    @api.depends('tasks.hours_perfect')
    def total_calc_per_hours(self):
        for task in self:
            total = 0.0
            for line in task.tasks:
                total += line.hours_perfect
            task.total_perfect_hours = total
            if task.project_risk:
                task.total_perfect_hours = task.total_perfect_hours+(task.total_perfect_hours*task.project_risk/100)

    @api.depends('tasks.hours_real_time')
    def total_calc_real_time(self):
        for task in self:
            total = 0.0
            for line in task.tasks:
                total += line.hours_real_time
            task.total_real_time = total
            if task.project_risk:
                task.total_real_time = task.total_real_time+(task.total_real_time*task.project_risk/100)

    @api.depends('tasks.hours_low_performance')
    def total_calc_low_performance(self):
        for task in self:
            total = 0.0
            for line in task.tasks:
                total += line.hours_low_performance
            task.total_low_performance = total
            if task.project_risk:
                task.total_low_performance = task.total_low_performance+(task.total_low_performance*task.project_risk/100)


class ProjectInherit(models.Model):
    _inherit = 'project.task'

    def estimation(self):
        author = False
        work_units = self.env['estimator.command'].search([])
        for rec in work_units:
            if self.user_id.name == rec.name.name:
                author = rec.id
        if not author:
            return {
                'name': _('First add this user into your command'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'estimator.wizard.project.user',
                'target': 'new',
                # 'context': {'new_user': True}
            }
        rec = self.env['estimator.project'].search([('name', '=', self.project_id.id)])
        if not rec:
            rec = self.env['estimator.project'].sudo().create({
                'name': self.project_id.id,
                'create_date': datetime.now(),
                'company': self.user_id.company_id.id,
                'state': 'confirm'
            })
        task_id = self.env['estimator.task_estimation'].search([('name', '=', self.id)])
        if task_id:
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_id': task_id.id,
                'view_id': self.env.ref('estimator.task_estimation_project_form', False).id,
                'res_model': 'estimator.task_estimation',
                'target': 'new',
            }
        view_id = self.env['estimator.task_estimation']
        vals = {
            'name': self.id,
            'author': author,
            'project_id': self.project_id.id,
            'task_id': rec.id
        }
        new = view_id.create(vals)
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_id': new.id,
            'view_id': self.env.ref('estimator.task_estimation_project_form', False).id,
            'res_model': 'estimator.task_estimation',
            'target': 'new',
        }
