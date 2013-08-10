from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render

from tomonotomo.models import UserTomonotomo

from social_auth.signals import pre_update
from social_auth.backends.facebook import FacebookBackend

from tomonotomo import dbutils

# from profile.models import Profile

def index(request):
    return render(request, 'tomonotomo/index.html')

def friend(request, fbid):
	#fbid = 717323242
	template = loader.get_template('tomonotomo/friend.html')
	profile = UserTomonotomo.objects.get(userid=fbid)
	context = RequestContext(request, {
		'fbid': fbid,
		'fullname': profile.get_full_name,
		'age': profile.get_age,
		'location': profile.location,
		'worklist': profile.work.split('---'),
		'educationlist': profile.education.split('---'),
		'mutualfriends': map(dbutils.getFriendName, dbutils.getMutualFriends(fbid, fbid)),
		})
	return HttpResponse(template.render(context))

def about(request):
    return render(request, 'tomonotomo/about.html')

def join(request):
    return render(request, 'tomonotomo/join.html')


