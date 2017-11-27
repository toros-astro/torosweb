from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^upload$', views.upload, name='upload'),
    url(r'^uploadjson$', views.uploadjson, name='uploadjson'),
    url(r'^circular/(?P<alert_name>\w+)$', views.circular, name='circular'),
]
