from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic.base import TemplateView
from wiki.urls import get_pattern as get_wiki_pattern
from django_nyt.urls import get_pattern as get_nyt_pattern

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.core import urls as wagtail_urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
    url(r'^account/', include('account.urls', namespace="account")),
    url(r'^account/', include('django.contrib.auth.urls')),
    url(r'^broker/', include('broker.urls', namespace='broker')),
    url(r'^wiki/notifications/', get_nyt_pattern()),
    url(r'^wiki/', get_wiki_pattern()),
    url(r'^winnow/', include('winnow.urls', namespace='winnow')),
    url(r'^comments/', include('fluent_comments.urls')),
    url(r'^inauguration/', include('ctmoinaug.urls', namespace='ctmoinaug')),
    url(r'^cms/', include(wagtailadmin_urls)),
    # url(r'^documents/', include(wagtaildocs_urls)),
    url(r'', include(wagtail_urls)),
]

from django.conf import settings

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
