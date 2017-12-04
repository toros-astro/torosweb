from django.conf.urls import url
from winnow import views
from django.views.generic.base import TemplateView

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='winnow/index.html'),
        name='index'),
    url(r'^$', TemplateView.as_view(template_name='winnow/about.html'),
        name='about'),
    url(r'^rank/$', views.rank, name='rank'),
    url(r'^object/(?P<object_slug>\w+)/$', views.object_detail, name='object_detail'),
    url(r'^data/$', views.data, name='data'),
    url(r'^rb$', views.rb, name='rb'),
]
