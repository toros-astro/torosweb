from django.conf.urls import url
from . import views
from django.views.generic.base import TemplateView


urlpatterns = [
    url(r'signup/$', views.SignUp.as_view(), name='signup'),
    url(r'profile/(?P<username>.+)/$', views.profilepage, name='profile'),
    url(r'pending/$', TemplateView.as_view(template_name='pending.html'), name='pending'),
]
