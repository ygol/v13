# -*- coding: utf-8 -*-
# from odoo import http


# class TaskEstimation(http.Controller):
#     @http.route('/task_estimation/task_estimation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/task_estimation/task_estimation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('task_estimation.listing', {
#             'root': '/task_estimation/task_estimation',
#             'objects': http.request.env['task_estimation.task_estimation'].search([]),
#         })

#     @http.route('/task_estimation/task_estimation/objects/<model("task_estimation.task_estimation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('task_estimation.object', {
#             'object': obj
#         })
