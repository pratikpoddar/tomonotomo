from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render

from django.contrib.auth.decorators import login_required

from tomonotomo.models import UserTomonotomo

from tomonotomo import dbutils


def index(request):
    return render(request, 'tomonotomo/index.html')

@login_required(login_url='/tomonotono/login/')
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

@login_required(login_url='/tomonotomo/login/')
def loggedin(request):
    #fbid = UserTomonotomo.objects.get(username=request.user.username).userid
    fbid = 717323242
    template = loader.get_template('tomonotomo/loggedin.html')
    context = RequestContext(request, {
		'degree1': dbutils.getNumberofFriends(fbid),
		'degree2': len(dbutils.getFriendsofFriends(fbid)),
		})
    return HttpResponse(template.render(context))