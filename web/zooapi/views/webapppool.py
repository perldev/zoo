# -*- coding: utf-8 -*-

from django.http import HttpResponseNotAllowed

from core.core import Core
from web.helpers.json import json_response, json_request


@json_response
def pool_list(request):
    """
    Хендлер. Получить список пулов ииса
    :param request:
    :return:
    """
    core = Core.get_instance()
    pools = core.api.os.web_server.get_app_pool_list()
    return [pool.to_dict() for pool in pools]

