# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^status/', include('status.urls', namespace='status')),

    url(r'^checker/api/v1/', include('checker.urls', namespace='checker')),
    url(r'^call_centre/api/v1/', include('call_centre.urls', namespace='call_centre')),
    url(r'^cla_provider/api/v1/', include('cla_provider.urls', namespace='cla_provider')),

    url(r'^oauth2/', include('cla_auth.urls', namespace='oauth2')),

    url(r'^admin/reports/', include('reports.urls', namespace='reports')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^means_test/api/v1/', include('means_test_api.urls', namespace='means_test')),
    )
