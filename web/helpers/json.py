# -*- coding: utf-8 -*-

import json
import traceback
from django.http import HttpResponse, Http404


def master_product_json_response(func):

    def decorator(self, *args, **kwargs):
        http_status = 200
        try:
            result = func(self, *args, **kwargs)
            if isinstance(result, HttpResponse):
                return result
            result = {'data': result, 'master_status': self.get_state()}
        except Http404:
            raise
        except Exception as ex:
            result = {
                'data': None,
                'error': {
                    'class': ex.__class__.__name__,
                    'args': '{0}'.format(ex),
                    'traceback': traceback.format_exc()
                }
            }
            http_status = 500
            traceback.print_exc()

        data = json.dumps(result, indent=1)
        response = HttpResponse(data, content_type='application/json', status=http_status)
        response['Cache-Control'] = 'no-cache,no-store,must-revalidate,max-age=0'
        return response

    return decorator


def json_response(func):
    """
    A decorator thats takes a view response and turns it
    into json. If a callback is added through GET or POST
    the response is JSONP.
    """
    def decorator(request, *args, **kwargs):
        http_status = 200
        try:
            result = func(request, *args, **kwargs)
            if isinstance(result, HttpResponse):
                return result
            result = {'data': result}
        except Http404:
            raise
        except Exception as ex:
            result = {
                'data': None,
                'error': {
                    'class': ex.__class__.__name__,
                    'args': '{0}'.format(ex),
                    'traceback': traceback.format_exc()
                }
            }
            http_status = 500
            traceback.print_exc()

        try:
            data = json.dumps(result, indent=1)
            if 'callback' in request.REQUEST:
                # a jsonp response!
                data = '%s(%s);' % (request.REQUEST['callback'], data)
                response = HttpResponse(data, content_type='text/javascript')
                response['Cache-Control'] = 'no-cache,no-store,must-revalidate,max-age=0'
                return response
        except Exception:
            raise

        response = HttpResponse(data, content_type='application/json', status=http_status)
        response['Cache-Control'] = 'no-cache,no-store,must-revalidate,max-age=0'
        return response
    return decorator


def json_request(request):
    """
    Парсит тело http-запроса из джейсона в питоньи объекты (словари и списки)
    """
    s = request.body
    if isinstance(s, bytes):
        s = s.decode('utf-8')
    return json.loads(s)
