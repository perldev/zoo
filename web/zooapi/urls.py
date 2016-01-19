from django.conf.urls import patterns, include, url

from web.сommon_system_state import  CommonSystemRoute
from web.zooapi.views.product import product_list
from web.zooapi.views.tag import tag_list
from web.zooapi.views.website import website_list, server_root, website_item, website_path
from web.zooapi.views.engine import engine_list, config
from web.zooapi.views.webapppool import pool_list
from web.zooapi.views.install import install, uninstall, upgrade
from web.zooapi.views.task import task_list, task, rerun, cancel, log
from web.zooapi.views.console import create, cancel, read, write
from web.zooapi.views.db import check
from web.zooapi.views.settings import settings
from web.zooapi.views.core import state, logs_clear, logs, cache, cache_clear, has_upgrade, sync
"""
REST API.
Описание урлов и хендлеров для них.
"""



urlpatterns = patterns('',

    # список продуктов
    url(r'^product/list/$', CommonSystemRoute(product_list).run,
        name='zooapi.views.product.product_list'),
    #url(r'^product/id/(?P<prod_id>[\w\.]+)/$', name='zooapi.views.product.product_id'),

    # спсико тегов
    url(r'^tag/list/$',  CommonSystemRoute(tag_list).run,
        name='zooapi.views.tag.tag_list'),

    # список сайтов для страницы инсталляции не переопределяем его
    url(r'^server/list/$', website_list,
        name='zooapi.views.website.website_list'),

    #url(r'^server/create/$', name='zooapi.views.website.website_create'),

    # список сайтов для дерева сервера
    url(r'^server/root/$', CommonSystemRoute(server_root).run,
        name='zooapi.views.website.server_root'),
    # список узлов внутри сайта
    url(r'^server/root/(?P<name>[^/]+)/$', CommonSystemRoute(website_item).run,
        name='zooapi.views.website.website_item'),
    # список узлов в поддиректориях сайта
    url(r'^server/root/(?P<name>[^/]+)(?P<path>/.*)?$', CommonSystemRoute(website_path).run,
        name='zooapi.views.website.website_path'),

    # спсиков энжинов
    url(r'^engine/list/$', CommonSystemRoute(engine_list).run,
        name='zooapi.views.engine.engine_list'),
    # конфиг для энжина
    url(r'^engine/id/(?P<name>[^/]+)/config/$', CommonSystemRoute(config).run,
        name='zooapi.views.engine.config'),

    # спсиок пуллов IIS
    url(r'^webapppool/list/$', pool_list,
        name='zooapi.views.webapppool.pool_list'),

    # инсталляция продуктов
    url(r'^install/$', CommonSystemRoute(install).run,
        name='zooapi.views.install.install'),
    # апгрейд
    url(r'^upgrade/$', CommonSystemRoute(upgrade).run,
        name='zooapi.views.install.upgrade'),
    # деинсталляция
    url(r'^uninstall/$', CommonSystemRoute(uninstall).run,
        name='zooapi.views.install.uninstall'),

    # спсиок задач
    url(r'^task/list/$', CommonSystemRoute(task_list).run,
        name='zooapi.views.task.task_list'),
    # получить детали задачи
    url(r'^task/id/(?P<task_id>[\w\.]+)/$', task,
        name='zooapi.views.task.task'),
    # отменить задачу
    url(r'^task/id/(?P<task_id>[\w\.]+)/cancel/$', CommonSystemRoute(cancel).run,
        name='zooapi.views.task.cancel'),
    # перезапустить задачу
    url(r'^task/id/(?P<task_id>[\w\.]+)/rerun/$', CommonSystemRoute(rerun).run,
        name='zooapi.views.task.rerun'),
    # вренуть логи задачи
    url(r'^task/id/(?P<task_id>[\w\.]+)/log/$', log,
        name='zooapi.views.task.log'),


    # создать консоль
    url(r'^console/create/$', CommonSystemRoute(create).run,
        name='zooapi.views.console.create'),
    # получить выхлоп из консоли
    url(r'^console/read/$', CommonSystemRoute(read).run,
        name='zooapi.views.console.read'),
    # написать в консоль
    url(r'^console/write/$', CommonSystemRoute(write).run,
        name='zooapi.views.console.write'),
    # закрыть консоль
    url(r'^console/cancel/$', CommonSystemRoute(cancel).run,
        name='zooapi.views.console.cancel'),

    # проверка коннекта в бд, используется на мастере инсталляции приложения
    url(r'^db/check', CommonSystemRoute(check).run,
        name='zooapi.views.db.check'),

    # настройки
    url(r'^settings/$', CommonSystemRoute(settings).run,
        name='zooapi.views.settings.settings'),

    # состояние ядра (загружается, загружено, с ошибками)
    url(r'^core/state/$', CommonSystemRoute(state).run,
        name='zooapi.views.core.state'),
    # проверяет, есть ли обновление для нас
    url(r'^core/upgrade/$', CommonSystemRoute(has_upgrade).run,
        name='zooapi.views.core.has_upgrade'),

    url(r'^core/sync/$', CommonSystemRoute(sync).run,
        name='zooapi.views.core.sync'),
    # размер директории кеша
    url(r'^core/cache/$', CommonSystemRoute(cache).run,
        name='zooapi.views.core.cache'),
    # очистить директорию кеша
    url(r'^core/cache/clear/$', CommonSystemRoute(cache_clear).run,
        name='zooapi.views.core.cache_clear'),
    # размер директории логов
    url(r'^core/logs/$', CommonSystemRoute(logs).run,
        name='zooapi.views.core.logs'),
    # очистить директорию логов
    url(r'^core/logs/clear/$', CommonSystemRoute(logs_clear).run,
        name='zooapi.views.core.logs_clear'),
)
