from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import render

from django.contrib.auth.decorators import login_required

from tomonotomo.models import UserTomonotomo, UserFeedback

from tomonotomo import dbutils


def index(request):
    return render(request, 'tomonotomo/index.html')

@login_required(login_url='/tomonotono/login/')
def friendrandom(request):
    loggedid = UserTomonotomo.objects.get(username=request.user.username).userid
    fbid = dbutils.getRandFoF(loggedid)
    return friend(request, fbid)

def friend(request, fbid):
    #fbid = 717323242
    loggedid = UserTomonotomo.objects.get(username=request.user.username).userid
    template = loader.get_template('tomonotomo/friend.html')
    profile = UserTomonotomo.objects.get(userid=fbid)
    context = RequestContext(request, {
		'fbid': fbid,
		'fullname': profile.get_full_name,
		'age': profile.get_age,
		'location': profile.location,
		'worklist': profile.work.split('---'),
		'educationlist': profile.education.split('---'),
		'mutualfriends': map(dbutils.getFriendName, dbutils.getMutualFriends(loggedid, fbid)),
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
		'degree1': len(dbutils.getFriendsonTnT(fbid)),
		'degree2': len(dbutils.getFriendsofFriends(fbid)),
		})
    return HttpResponse(template.render(context))

@login_required(login_url='/tomonotono/login/')
def tntAction(request, fbid, action):
    #fbid = 717323242
    #action = 1
    #userid = 717323242

    userid = UserTomonotomo.objects.get(username=request.user.username).userid

    feedback = UserFeedback(
        userid = userid,
        fbid = fbid,
        action = action
    )
    feedback.save()

    if action == 1:
        tolist = ','.join(dbutils.getMutualFriends(userid, fbid))
        link = 'http://www.tomonotomo.com/friend/' + str(fbid)
        redirect_uri = 'http://localhost:8080/tomonotomo/friend'
        finallink = 'https://www.facebook.com/dialog/send?app_id=1398031667088132&link=' + link + '&redirect_uri=' + redirect_uri + '&to=' + tolist
        return redirect(finallink)

    if action == 2:
        tolist = fbid
        link = 'http://www.tomonotomo.com/friend/' + str(userid)
        redirect_uri = 'http://localhost:8080/tomonotomo/friend'
        finallink = 'https://www.facebook.com/dialog/send?app_id=1398031667088132&link=' + link + '&redirect_uri=' + redirect_uri + '&to=' + tolist
        return redirect(finallink)

    if action == 3:
        return redirect('http://localhost:8080/tomonotomo/friend')

    if action == 4:
        return redirect('http://localhost:8080/tomonotomo/friend')

    return