from django.http import HttpResponse, Http404
from django.template import RequestContext, loader
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from tomonotomo.models import UserTomonotomo, UserFeedback

from tomonotomo import dbutils

import urllib

def index(request):
    return render(request, 'tomonotomo/index.html')

@login_required(login_url='index')
def friendrandom(request):
    loggedid = UserTomonotomo.objects.get(username=request.user.username).userid
    fbid = dbutils.getRandFoF(loggedid)
    return friend(request, fbid)

def friend(request, fbid):
    #fbid = 717323242
    if request.user.id:
        loggedid = UserTomonotomo.objects.get(username=request.user.username).userid
        mutualfriends = map(dbutils.getFriendName, dbutils.getMutualFriends(loggedid, fbid))
    else:
        mutualfriends = []

    template = loader.get_template('tomonotomo/friend.html')
    try:
        profile = UserTomonotomo.objects.get(userid=fbid)
    except ObjectDoesNotExist:
        raise Http404

    context = RequestContext(request, {
		'fbid': fbid,
		'fullname': profile.get_full_name,
		'age': profile.get_age,
		'location': profile.location,
		'worklist': profile.work.split('---'),
		'educationlist': profile.education.split('---'),
		'mutualfriends': mutualfriends
		})
    return HttpResponse(template.render(context))

def about(request):
    return render(request, 'tomonotomo/about.html')

def join(request):
    return render(request, 'tomonotomo/join.html')

@login_required(login_url='index')
def loggedin(request):
    fbid = UserTomonotomo.objects.get(username=request.user.username).userid
    template = loader.get_template('tomonotomo/loggedin.html')
    context = RequestContext(request, {
		'degree1': len(dbutils.getFriendsonTnT(fbid)),
		'degree2': len(dbutils.getFriendsofFriends(fbid)),
		})
    return HttpResponse(template.render(context))

@login_required(login_url='index')
def tntAction(request, fbid, action, fbfriend):
    ##fbid = 717323242
    ##action = 1
    ##userid = 717323242

    fbid = int(fbid)
    action = int(action)
    userinfo = UserTomonotomo.objects.get(username=request.user.username)
    userid = userinfo.userid

    feedback = UserFeedback(
        userid = userid,
        fbid = fbid,
        action = action
    )
    feedback.save()

    if action == 1:
        dbutils.sendemailFriend(userid, fbid, friendid)
    if action == 2:
        mutualfriendlist = dbutils.getMutualFriends(userid, fbid)
        dbutils.sendemailFoF(userid, fbid, mutualfriendlist)
    
    return redirect('tomonotomo/friend')
