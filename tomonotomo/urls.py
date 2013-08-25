from django.conf.urls import patterns, include, url

from tomonotomo import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='default'),
    url(r'^home$', views.index, name='index'),
    url(r'^friend/(\d+)$', views.friend, name='friend'),
    url(r'^tntAction/(\d+)/(\d+)/(\d+)$', views.tntAction, name='tntAction'),
    url(r'^friend$', views.friendrandom, name='friendrandom'),
    url(r'^about$', views.about, name='about'),
    url(r'^join$', views.join, name='join'),
    url(r'^loggedin$', views.loggedin, name='loggedin'),
    url(r'^logout$', 'django.contrib.auth.views.logout',{'next_page': 'home'}),
    url(r'^auth/', include('social_auth.urls')),
    url(r'^betathanks$', views.betathanks, name='betathanks'),
)

