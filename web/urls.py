from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns




urlpatterns = patterns('',
     url(r'^api/1/', include('zooapi.urls')),
     url(r'^', include('zoo.urls')),
)

urlpatterns += staticfiles_urlpatterns()