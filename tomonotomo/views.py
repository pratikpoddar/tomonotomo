from django.http import HttpResponse, Http404
from django.template import RequestContext, loader
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from tomonotomo.models import UserTomonotomo, UserFeedback

from tomonotomo import dbutils

from meta.views import Meta

from django.templatetags.static import static

import urllib

def index(request):
    meta = Meta(
        use_og=1,
        url=request.build_absolute_uri(),
        use_sites=True,
        description='We are revolutionising the way dating happens right now. Please give us a try, if you believe in safe, secure and freindly relationship based on trust and respect',
        keywords=['dating', 'tomonotomo', 'friend'],
        image='tomonotomo/img/logo.jpg',
        title='tomonotomo - meet friends of friends'
    )    
    template = loader.get_template('tomonotomo/index.html')
    context = RequestContext(request, {
        'meta': meta
        })
    return HttpResponse(template.render(context))

@login_required(login_url='index')
def friendrandom(request):
    loggedid = UserTomonotomo.objects.get(username=request.user.username).userid
    gender = UserTomonotomo.objects.get(username=request.user.username).gender
    reqgender = "indifferent"
    if gender=="male":
        reqgender = "female"
    if gender=="female":
        reqgender = "male"
    fbid = dbutils.getRandFoF(loggedid, reqgender)
    if fbid == 0:
        raise Http404
    return friend(request, fbid)

def friend(request, fbid):
    #fbid = 717323242
    if request.user.id:
        loggedid = UserTomonotomo.objects.get(username=request.user.username).userid
        mutualfriends = map(lambda x: {'name': dbutils.getFullName(x), 'id': x}, dbutils.getMutualFriends(loggedid, fbid))
        historyFeedback = dbutils.historyFeedback(loggedid, fbid)
        deactivateList = historyFeedback['deactivate']
        infoList = historyFeedback['info']
    else:
        mutualfriends = []
        deactivateList = [1, 2, 3, 4]
        infoList = []

    template = loader.get_template('tomonotomo/friend.html')
    try:
        profile = UserTomonotomo.objects.get(userid=fbid)
    except ObjectDoesNotExist:
        raise Http404

    if UserTomonotomo.objects.get(userid=fbid).email == None:
        email_exists = 0
    else:
        email_exists = 1

    meta = Meta(
        use_og=1,
        url=request.build_absolute_uri(),
        use_sites=True,
        description='Tomonotomo - We are revolutionising the way dating happens right now. Please give us a try, if you believe in safe, secure and freindly relationship based on trust and respect',
        keywords=['dating', 'tomonotomo', 'friend'],
        image='http://www.facebook.com/'+str(fbid)+'/picture?type=square',
        title= str(profile.get_full_name()) + ' - tomonotomo - meet friends of friends',
    )        

    context = RequestContext(request, {
		'fbid': fbid,
		'fullname': profile.get_full_name(),
		'age': profile.get_age,
		'location': profile.location,
		'worklist': profile.work.split('---'),
		'educationlist': profile.education.split('---'),
		'mutualfriends': mutualfriends,
		'meta': meta,
        'deactivateList': deactivateList,
        'infoList': infoList,
        'email_exists': email_exists
        })

    return HttpResponse(template.render(context))

def about(request):
    meta = Meta(
        use_og=1,
        url=request.build_absolute_uri(),
        use_sites=True,
        description='We are revolutionising the way dating happens right now. Please give us a try, if you believe in safe, secure and freindly relationship based on trust and respect',
        keywords=['dating', 'tomonotomo', 'friend'],
        image='tomonotomo/img/logo.jpg',
        title='tomonotomo - meet friends of friends'
    )    
    template = loader.get_template('tomonotomo/about.html')
    context = RequestContext(request, {
        'meta': meta
        })
    return HttpResponse(template.render(context))

def join(request):
    meta = Meta(
        use_og=1,
        url=request.build_absolute_uri(),
        use_sites=True,
        description='We are revolutionising the way dating happens right now. Please give us a try, if you believe in safe, secure and freindly relationship based on trust and respect',
        keywords=['dating', 'tomonotomo', 'friend'],
        image='tomonotomo/img/logo.jpg',
        title='tomonotomo - meet friends of friends'
    )    
    template = loader.get_template('tomonotomo/join.html')
    context = RequestContext(request, {
        'meta': meta
        })
    return HttpResponse(template.render(context))

@login_required(login_url='index')
def loggedin(request):
    fbid = UserTomonotomo.objects.get(username=request.user.username).userid
    template = loader.get_template('tomonotomo/loggedin.html')
    meta = Meta(
        use_og=1,
        url=request.build_absolute_uri(),
        use_sites=True,
        description='We are revolutionising the way dating happens right now. Please give us a try, if you believe in safe, secure and freindly relationship based on trust and respect',
        keywords=['dating', 'tomonotomo', 'friend'],
        image='tomonotomo/img/logo.jpg',
        title='tomonotomo - meet friends of friends'
    )
    dictin = {
		'degree1': len(dbutils.getFriendsonTnT(fbid)),
		'degree2': len(dbutils.getFriendsofFriends(fbid)),
        'meta': meta
		}

    context = RequestContext(request, dictin)
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

    try:
        feedback = UserFeedback.objects.get(userid=userinfo, fbid=fbid)
        setattr(feedback, 'action', action)
        feedback.save()
    except UserFeedback.DoesNotExist:
        feedback = UserFeedback(userid=userinfo, fbid=fbid, action=action)

    feedback.save()
    print "Feedback Submitted: " + str(userid) + " " + str(fbid) + " " + str(action)

    if action == 1:
        dbutils.sendemailFriend(userid, fbid, fbfriend)

    if action == 2:
        mutualfriendlist = dbutils.getMutualFriends(userid, fbid)
        dbutils.sendemailFoF(userid, fbid, mutualfriendlist)

    if action == 3:
        try:
            if UserFeedback.objects.filter(userid=fbid, fbid=userid).values()[0]['action'] == 3:
                mutualfriendlist = dbutils.getMutualFriends(userid, fbid)
                dbutils.sendemailCute(userid, fbid, mutualfriendlist)
        except:
            return redirect('/tomonotomo/friend')

    return redirect('/tomonotomo/friend')
