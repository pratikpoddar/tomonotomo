from django.http import HttpResponse, Http404
from django.template import RequestContext, loader
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from tomonotomo.models import UserTomonotomo, UserFeedback, UserFriends, UserLogin

from tomonotomo import dbutils

from meta.views import Meta

from django.templatetags.static import static
from django.db.models import Count

import urllib
from datetime import datetime
from datetime import timedelta


def index(request):
    meta = Meta(
        use_og=1,
        url=request.build_absolute_uri(),
        use_sites=True,
        description='We are revolutionising the way dating happens right now. Please give us a try, if you believe in safe, secure and friendly relationship based on trust and respect',
        keywords=['dating', 'tomonotomo', 'friend'],
        image='http://www.tomonotomo.com/static/tomonotomo/img/logo.jpg',
        title='tomonotomo - meet friends of friends'
    )    
    template = loader.get_template('tomonotomo/index.html')
    context = RequestContext(request, {
        'meta': meta,
	'usersdatalen': "{:,}".format(UserTomonotomo.objects.count())
        })
    return HttpResponse(template.render(context))

@login_required(login_url='index')
def friendrandom(request):
    loggedid = UserTomonotomo.objects.get(email=request.user.email).userid
    gender = UserTomonotomo.objects.get(email=request.user.email).gender
    reqgender = 3
    if gender==1:
        reqgender = 2
    if gender==2:
        reqgender = 1
    fbid = dbutils.getRandFoF(loggedid, reqgender)
    if fbid == 0:
        raise Http404

    return redirect('/friend/'+str(fbid))

def friend(request, fbid):
    #fbid = 717323242
    show_button = 1
    if request.user.id:
        loggedid = UserTomonotomo.objects.get(email=request.user.email).userid
        mutualfriends = map(lambda x: {'name': dbutils.getFullName(x), 'id': x}, dbutils.getMutualFriends(loggedid, fbid))
        historyFeedback = dbutils.historyFeedback(loggedid, fbid)
        deactivateList = historyFeedback['deactivate']
        infoList = historyFeedback['info']
	if len(mutualfriends) == 0:
		show_button=0
        try:
		isa_friend = UserFriends.objects.get(userid=loggedid, friendid=fbid)
		show_button=0
	except UserFriends.DoesNotExist:
		show_button=show_button
    else:
        mutualfriends = []
        deactivateList = [1, 2, 3, 4]
        infoList = []
	show_button = 0

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
        description='Tomonotomo - We are revolutionising the way dating happens right now. Please give us a try, if you believe in safe, secure and friendly relationship based on trust and respect',
        keywords=['dating', 'tomonotomo', 'friend'],
        image='http://www.facebook.com/'+str(fbid)+'/picture?type=square',
        title= str(profile.get_full_name()) + ' - tomonotomo - meet friends of friends',
    )        

    
    if profile.work == "":
    	worklist = []
    else:
	worklist = profile.work.split('---')
	worklist.reverse()
	worklist = filter(lambda x: len(x), worklist)

    if profile.education == "":
	educationlist = []
    else:
	educationlist = profile.education.split('---')
	educationlist.reverse()
	educationlist = filter(lambda x: len(x), educationlist)

    if profile.get_age() != "[Age N.A.]":
	if profile.location != "":
		agelocation = str(profile.get_age()) + ", " + profile.location
	else:
		agelocation = profile.get_age()
    else:
	agelocation = profile.location

    context = RequestContext(request, {
		'fbid': fbid,
		'fullname': profile.get_full_name(),
		'agelocation': agelocation,
		'worklist': worklist,
		'educationlist': educationlist,
		'mutualfriends': mutualfriends,
		'meta': meta,
        'deactivateList': deactivateList,
        'infoList': infoList,
        'email_exists': email_exists,
	'show_button': show_button
        })

    return HttpResponse(template.render(context))

def about(request):
    meta = Meta(
        use_og=1,
        url=request.build_absolute_uri(),
        use_sites=True,
        description='We are revolutionising the way dating happens right now. Please give us a try, if you believe in safe, secure and friendly relationship based on trust and respect',
        keywords=['dating', 'tomonotomo', 'friend'],
        image='http://www.tomonotomo.com/static/tomonotomo/img/logo.jpg',
        title='tomonotomo - meet friends of friends'
    )    
    template = loader.get_template('tomonotomo/about.html')
    context = RequestContext(request, {
        'meta': meta
        })
    return HttpResponse(template.render(context))

def terms(request):
    meta = Meta(
        use_og=1,
        url=request.build_absolute_uri(),
        use_sites=True,
        description='We are revolutionising the way dating happens right now. Please give us a try, if you believe in safe, secure and friendly relationship based on trust and respect',
        keywords=['dating', 'tomonotomo', 'friend'],
        image='http://www.tomonotomo.com/static/tomonotomo/img/logo.jpg',
        title='tomonotomo - meet friends of friends'
    )    
    template = loader.get_template('tomonotomo/terms.html')
    context = RequestContext(request, {
        'meta': meta
        })
    return HttpResponse(template.render(context))

@login_required(login_url='index')
def loginerror(request):
    meta = Meta(
        use_og=1,
        url=request.build_absolute_uri(),
        use_sites=True,
        description='We are revolutionising the way dating happens right now. Please give us a try, if you believe in safe, secure and friendly relationship based on trust and respect',
        keywords=['dating', 'tomonotomo', 'friend'],
        image='http://www.tomonotomo.com/static/tomonotomo/img/logo.jpg',
        title='tomonotomo - meet friends of friends'
    )
    template = loader.get_template('tomonotomo/loginerror.html')
    context = RequestContext(request, {
        'meta': meta
        })
    return HttpResponse(template.render(context))


@login_required(login_url='index')
def loggedin(request):
    fbid = UserTomonotomo.objects.get(email=request.user.email).userid
    template = loader.get_template('tomonotomo/loggedin.html')
    meta = Meta(
        use_og=1,
        url=request.build_absolute_uri(),
        use_sites=True,
        description='We are revolutionising the way dating happens right now. Please give us a try, if you believe in safe, secure and friendly relationship based on trust and respect',
        keywords=['dating', 'tomonotomo', 'friend'],
        image='http://www.tomonotomo.com/static/tomonotomo/img/logo.jpg',
        title='tomonotomo - meet friends of friends'
    )
    dictin = {
		'degree1': "{:,}".format(len(dbutils.getFriendsonTnT(fbid))),
		'degree2': "{:,}".format(len(dbutils.getFriendsofFriends(fbid))),
        	'meta': meta
		}

    context = RequestContext(request, dictin)
    return HttpResponse(template.render(context))

@login_required(login_url='index')
def betathanks(request):
    fbid = UserTomonotomo.objects.get(email=request.user.email).userid
    template = loader.get_template('tomonotomo/betathanks.html')
    meta = Meta(
        use_og=1,
        url=request.build_absolute_uri(),
        use_sites=True,
        description='We are revolutionising the way dating happens right now. Please give us a try, if you believe in safe, secure and friendly relationship based on trust and respect',
        keywords=['dating', 'tomonotomo', 'friend'],
        image='http://www.tomonotomo.com/static/tomonotomo/img/logo.jpg',
        title='tomonotomo - meet friends of friends'
    )
    dictin = {
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
    userinfo = UserTomonotomo.objects.get(email=request.user.email)
    userid = userinfo.userid

#    try:
#        feedback = UserFeedback.objects.get(userid=userinfo, fbid=fbid)
#	if action < 5:
#		setattr(feedback, 'action', action)
#        feedback.save()
#    except UserFeedback.DoesNotExist:
#        feedback = UserFeedback(userid=userinfo, fbid=fbid, action=action)

    feedback = UserFeedback(userid=userinfo, fbid=fbid, action=action)
    feedback.save()
    print "Feedback Submitted: " + str(userid) + " " + str(fbid) + " " + str(action)

    if action == 1:
        dbutils.sendemailFriend(userid, fbid, fbfriend)
	return redirect('/friend/'+str(fbid))

    if action == 2:
        mutualfriendlist = dbutils.getMutualFriends(userid, fbid)
        dbutils.sendemailFoF(userid, fbid)
	return redirect('/friend/'+str(fbid))

    if action == 3:
        try:
            if UserFeedback.objects.filter(userid=fbid, fbid=userid).values()[0]['action'] == 3:
                mutualfriendlist = dbutils.getMutualFriends(userid, fbid)
                dbutils.sendemailCute(userid, fbid)
        except:
            return redirect('/friend/'+str(fbid))

    return redirect('/friend')

def dbsummary(request):

    try: 
	secret = request.GET['secret']
    except:	
    	raise Http404
	 
    template = loader.get_template('tomonotomo/dbsummary.html')
    contextdict = {'dbsummary_users_at': UserTomonotomo.objects.exclude(accesstoken=None).count(),
        'dbsummary_users_email': UserTomonotomo.objects.exclude(email=None).count(),
        'dbsummary_users_data': UserTomonotomo.objects.count(),
        'dbsummary_userfriends': UserFriends.objects.count(),
        'dbsummary_userfeedback': UserFeedback.objects.count(),
	'dbsummary_users': UserTomonotomo.objects.exclude(email=None).values('userid','first_name','last_name','email'),
	'dbsummary_feedback': UserFeedback.objects.values('action').annotate(Count('action')).order_by(),
	'dbsummary_users_login_24': list(set(map(lambda x: x['userlogin'], UserLogin.objects.filter(timestamp__gte=datetime.now()+timedelta(hours=-24)).values('userlogin')))),
	'dbsummary_users_register_24': list(set(map(lambda x: x['userlogin'], UserLogin.objects.filter(timestamp__gte=datetime.now()+timedelta(hours=-24)).values('userlogin')))-set(map(lambda x: x['userlogin'], UserLogin.objects.filter(timestamp__lte=datetime.now()+timedelta(hours=-24)).values('userlogin')))),
	'dbsummary_users_register_1': list(set(map(lambda x: x['userlogin'], UserLogin.objects.filter(timestamp__gte=datetime.now()+timedelta(hours=-1)).values('userlogin')))-set(map(lambda x: x['userlogin'], UserLogin.objects.filter(timestamp__lte=datetime.now()+timedelta(hours=-1)).values('userlogin'))))
    }

    context = RequestContext(request, contextdict)

    return HttpResponse(template.render(context))

