# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.http import HttpResponseNotAllowed

from web.helpers.json import json_response, json_request
from web.taskqueue.manager import TaskManager
from web.taskqueue.models import Task


@json_response
def task_list(request):
    """
    Получить список заданий

    :param request:
    :return:
    """
    return [t.to_dict() for t in Task.objects.all()]


@json_response
def task(request, task_id):
    """
    Получить конкретное задание по номеру task_id
    :param request:
    :param task_id:
    :return:
    """
    t = get_object_or_404(Task, id=task_id)
    return t.to_dict()


@json_response
def cancel(request, task_id):
    """
    Отменить конкретное задание по номеру task_id
    :param request:
    :param task_id:
    :return:
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    t = get_object_or_404(Task, id=task_id)
    return t.cancel()


@json_response
def rerun(request, task_id):
    """
    Повторно выполнить конкретное задание по номеру task_id
    :param request:
    :param task_id:
    :return:
    """
    t = get_object_or_404(Task, id=task_id)
    task_manager = TaskManager.get_instance()
    task_manager.rerun_task(t)
    return {'task': t.to_dict()}


@json_response
def log(request, task_id):
    """
    получить логи конкретного задания по номеру
    из базы данных
    если задание выполняется, то логи могут расти

    :param request:
    :param task_id:
    :return:
    """
    t = get_object_or_404(Task, id=task_id)
    since = request.GET.get('since')
    resp = {
        'task': t.to_dict(),
        'log_messages': [lm.to_dict() for lm in t.get_logs(since)]
    }
    return resp
