from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^alert/(?P<alert_name>\w+)$', views.index, name='alert_detail'),
    url(r'^uploadjson$', views.uploadjson, name='uploadjson'),
]
