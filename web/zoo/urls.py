from django.conf.urls import patterns, include, url
from web.сommon_system_state import  CommonSystemRoute

"""
По всем этим урлам отдаётся простая html-страничка,
вся логика веб-интерфейса находится в джсе.
Исключение — 'zoo.views.task_log'. Для скорости богатый цветной лог таска рендерится на сервере,
с помощью джанго-шаблона.
"""
from web.zoo.views import home, server, gallery, install
from web.zoo.views import upgrade, uninstall, task_list, task, task_log
from web.zoo.views import settings_view, console, icon, update



urlpatterns = patterns('',
    url(r'^$', CommonSystemRoute(home).run, name="home"),
    url(r'^server/$', CommonSystemRoute(server).run, name="server"),
    url(r'^gallery/$', CommonSystemRoute(gallery).run, name="gallery"),
    # url(r'^/master/(<command>[\w]+)/$', 'zoo.views.install'),

    url(r'^install/$', CommonSystemRoute(install).run, name='install'),
    url(r'^cancel_install/$', CommonSystemRoute(install).run, name='cancel_install'),

    url(r'^upgrade/$', CommonSystemRoute(upgrade).run, name='upgrade'),
    url(r'^uninstall/$', CommonSystemRoute(uninstall).run, name='uninstall'),

    url(r'^task/$', CommonSystemRoute(task_list).run, name='task_list'),
    url(r'^task/(?P<task_id>\d+)/$', CommonSystemRoute(task).run, name='task_id'),
    url(r'^task/(?P<task_id>\d+)/log/$', CommonSystemRoute(task_log).run, name='task_id_log'),

    url(r'^settings/$', CommonSystemRoute(settings_view).run, name='settings_view'),
    url(r'^console/$', CommonSystemRoute(console).run, name='console'),
    url(r'^update/$', CommonSystemRoute(update).run, name='update'),
    url(r'^product/(?P<product_name>[^/]+)/icon/', icon, name='icon'),
)
