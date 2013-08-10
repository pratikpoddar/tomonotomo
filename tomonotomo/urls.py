from django.conf.urls import patterns, include, url

from tomonotomo import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='default'),
    url(r'^home$', views.index, name='index'),
    url(r'^friend/(\d+)$', views.friend, name='friend'),
    url(r'^about$', views.about, name='about'),
    url(r'^join$', views.join, name='join'),
    url(r'^auth/', include('social_auth.urls'))    
)

