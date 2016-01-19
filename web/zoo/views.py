# -*- coding: utf-8 -*-

import os.path
import mimetypes

from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import ensure_csrf_cookie

from core.core import Core
from core.core_loader import CoreLoader
from web.taskqueue.models import Task
from web.zooapi.views.master_product import MasterProduct
from web.сommon_system_state import CommonSystemState
from django.template import RequestContext, loader

@ensure_csrf_cookie
def home(request):
    return render_to_response('home.html', RequestContext(request))


@ensure_csrf_cookie
def server(request):
    return render_to_response('server.html', RequestContext(request))


@ensure_csrf_cookie
def gallery(request):
    return render_to_response('gallery.html', RequestContext(request))


def settings_view(request):
    return render_to_response('settings.html', RequestContext(request))


def icon(request, product_name):
    """
    Возвращает иконку (бинарное содерживое файла) для продукта
    """

    # находим путь к иконке
    core = Core.get_instance()
    product = core.feed.get_product(product_name)
    icon_path = product.icon

    if not icon_path:
        raise Http404()

    # если путь урл — отсылаеи редирект
    if icon_path.startswith('http'):
        return HttpResponseRedirect(icon_path)

    if not os.path.exists(icon_path):
        # такого пути нет - 404
        raise Http404()

    # получаем миме-тип иконки
    mimetype = mimetypes.guess_type(os.path.basename(icon_path))[0]

    # читаем содержимое файла иконки
    with open(icon_path, 'rb') as fh:
        response = HttpResponse(fh.read(), mimetype=mimetype)

    # ставим кеширующий хидер
    response['Cache-Control'] = 'public,max-age=3600'
    return response


# this function starts MasterProduct application
# after that all requests are processing by them
def install(request):
    t = loader.get_template('install2.html')
    context = RequestContext(request)
    return HttpResponse(t.render(context))



def upgrade(request):
    return render_to_response('upgrade.html', RequestContext(request))


def uninstall(request):
    t = loader.get_template('uninstall.html')
    context = RequestContext(request)
    context["master_title"] = _("Uninstalling Product(s)")
    return HttpResponse(t.render(context))





def task_list(request):
    return render_to_response('task_list.html', RequestContext(request))


def task(request, task_id):
    t = get_object_or_404(Task, id=task_id)
    return render_to_response('task.html', RequestContext(request, {'task': t}))


def task_log(request, task_id):
    # получаем объект таска
    t = get_object_or_404(Task, id=task_id)
    # и его логи
    logs = t.get_logs(None)
    # рендерим логи в джанго-шаблоне
    return render_to_response('task_log.html', RequestContext(request, {'task': t, 'logs': logs}))


@ensure_csrf_cookie
def console(request):
    return render_to_response('console.html', RequestContext(request))


def update(request):
    """
    Запускает апгрейд ядра и редиректит на главную, где показывает процесс создания нового ядра.
    """
    core = Core.get_instance()
    core_loader = CoreLoader.get_instance()
    core_loader.restart(core.settings)
    return redirect(reverse('home'))
