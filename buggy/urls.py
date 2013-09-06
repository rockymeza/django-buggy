from django.conf.urls import patterns, url

urlpatterns = patterns('buggy.views',
    url(r'^$', 'bug_list', name='bug_list'),
    url(r'^(?P<pk>\d+)/$', 'bug_detail', name='bug_detail'),
)
