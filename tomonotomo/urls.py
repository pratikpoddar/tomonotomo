from django.conf.urls import patterns, include, url
from tomonotomo import views


urlpatterns = patterns('',
	url(r'^$', views.index, name='default'),
    	url(r'^home$', views.index, name='index'),
	url(r'^friend/(\d+)$', views.profileredir, name='friend'),#temporary
	url(r'^profile/(\d+)$', views.profileredir, name='profileredirect'),
	url(r'^tntAction/(\d+)/(\d+)/(\d+)$', views.tntAction, name='tntAction'),
	url(r'^fof$', views.fofrandom, name='fofrandom'),
	url(r'^about$', views.about, name='about'),
	url(r'^terms$', views.terms, name='terms'),
	url(r'^loggedin$', views.loggedin, name='loggedin'),
	url(r'^loginerror$', views.loginerror, name='loginerror'),
	url(r'^logout$', 'django.contrib.auth.views.logout',{'next_page': 'home'}),
	url(r'^auth/', include('social_auth.urls')),
	url(r'^dbsummary$', views.dbsummary, name='dbsummary'),
	url(r'^profile/([a-z0-9-]+)/(\d+)$', views.profile, name='profile'),
	url(r'^profile$', views.personalprofile, name='personalprofile'),
	url(r'^quotaover$', views.quotaover, name='quotaover'),
	url(r'^quotaincrease$', views.quotaincrease, name='quotaincrease'),
	url(r'^nomatchforyou$', views.nomatchforyou, name='nomatch'),
	url(r'^preparePotentialList$', views.preparePotentialList, name='preparePotentialList'),
)


