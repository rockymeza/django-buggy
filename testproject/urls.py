from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^buggy/', include('buggy.urls', namespace='buggy')),
    url(r'^admin/', include(admin.site.urls)),
)
