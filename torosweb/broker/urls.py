from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^alert/(?P<grace_id>\w+)/$', views.index, name='alert_detail'),
    url(r'^alert/(?P<grace_id>\w+)/(?P<gcn_pk>\d+)$', views.index, name='alert_detail'),
    url(r'^uploadjson/$', views.uploadjson, name='uploadjson'),
]
