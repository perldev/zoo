# -*- coding: utf-8 -*-

from django.http import HttpResponseNotAllowed, Http404

from core.core import Core
from web.helpers.json import json_response, json_request


@json_response
def website_list(request):
    """
    хендлер для запроса, показать список сайтов.

    :param request:
    :return:
    """
    core = Core.get_instance()
    sites = core.api.os.web_server.get_list_of_sites()
    return [site.to_dict() for site in sites]


@json_response
def website_create(request):
    """
    хендлер для запроса, создать сайт
    создает и возвращает сайт, или ошибка

    :param request:
    :return:
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    req = json_request(request)
    name = req['name']
    ip_address = req['ip_address']
    port = req['port']
    hostname = req['hostname']

    # 127.0.0.1:8085:localhost1.helicontech.com
    binding = 'http/{0}:{1}:{2}'.format(
        ip_address, port, hostname
    )

    core = Core.get_instance()
    try:
        path = core.api.os.web_server.create_physical_path_for_virtual_path(name)
        core.api.os.web_server.site_create(name, path, binding)
        website_object = core.api.os.web_server.get_site(name)
        response = {
            'error': None,
            'website': website_object.to_dict()
        }
    except Exception as e:
        response = {
            'error': str(e),
            'website': None
        }

    return response


@json_response
def server_root(request):
    """
    хендлер для запроса, показать дочерние узлы для корня сервера,
    т.е. список сайтов
    :param request:
    :return:
    """
    core = Core.get_instance()
    # list of sites
    return {
        'node': core.api.os.web_server.get_server_node(),
        'children': core.api.os.web_server.get_directories(None, None)
    }


@json_response
def website_item(request, name):
    """
    хендлер для запроса, узла дерева - сайт
    GET  - получить дочерние узлы
    POST - обновить zoo_config с переданными значаниями

    :param request:
    :param name:
    :return:
    """
    core = Core.get_instance()
    if request.method == 'POST':
        req = json_request(request)
        core.api.os.web_server.update_zoo_config(name, "/", req)

    return {
        'node': core.api.os.web_server.get_site_node(name),
        'children': core.api.os.web_server.get_directories(name, "/")
    }


@json_response
def website_path(request, name, path):
    """
  хендлер для запроса, узла дерева - папка под сайтом
    GET  - получить дочерние узлы
    POST - обновить zoo_config с переданными значаниями

    :param request:
    :param name:
    :param path:
    :return:
    """
    core = Core.get_instance()
    if request.method == 'POST':
        req = json_request(request)
        core.api.os.web_server.update_zoo_config(name, path, req)

    return {
        'node': core.api.os.web_server.get_path_node(name, path),
        'children': core.api.os.web_server.get_directories(name, path)
    }

