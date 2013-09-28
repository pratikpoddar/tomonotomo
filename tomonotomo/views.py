from django.http import HttpResponse, Http404
from django.template import RequestContext, loader
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import slugify

from tomonotomo.models import UserTomonotomo, UserFeedback, UserFriends, UserLogin, UserHappening, UserQuota, UserEmail

from tomonotomo import dbutils

from meta.views import Meta

from django.templatetags.static import static
from django.db.models import Count

import urllib
from datetime import datetime
from datetime import timedelta
from datetime import date

import logging

logger = logging.getLogger(__name__)

def index(request):

    if request.user.id:
    	loggedid = dbutils.getLoggedInUser(request)
    else:
	loggedid = 0

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
	'usersdatalen': "{:,}".format(UserTomonotomo.objects.count()),
	'loggeduserid': loggedid
        })
    return HttpResponse(template.render(context))

def sitemapgen(request, number):
    template = loader.get_template('tomonotomo/sitemap.html')

    if request.user.id:
        loggedid = dbutils.getLoggedInUser(request)
    else:
        loggedid = 0

    if number < 0:
	listofusers  = []

    else:
    	try:
    		listofusers = UserTomonotomo.objects.filter(id__range=(int(number)*500, int(number)*500+520)).values('userid')
   	except:
		listofusers = []
    
    context = RequestContext(request, {
        'listofusers' : map(lambda x: {'name': dbutils.getFullName(x['userid']), 'id':x['userid']},  listofusers),
	'sitemaplist' : range(1,1001),
	'loggeduserid': loggedid
        })
    return HttpResponse(template.render(context))

def sitemap(request):
    return sitemapgen(request,-1)

@login_required(login_url='index')
def quotaover(request):
    template = loader.get_template('tomonotomo/quotaover.html')
    loggedid = dbutils.getLoggedInUser(request)

    context = RequestContext(request, {
        'loggedid': loggedid,
	'loggeduserid': loggedid
        })
    return HttpResponse(template.render(context))

@login_required(login_url='index')
def quotaincrease(request):

     loggedid = dbutils.getLoggedInUser(request)
     dbutils.increase_quota(loggedid)

     return redirect('/fof')

@login_required(login_url='index')
def personalprofile(request):

    loggedid = dbutils.getLoggedInUser(request)
    logger.debug('view.personalprofile - ' + str(loggedid))

    template = loader.get_template('tomonotomo/personalprofile.html')
    profile = UserTomonotomo.objects.get(userid=loggedid)

    meta = Meta(
        use_og=1,
        url=request.build_absolute_uri(),
        use_sites=True,
        description='We are revolutionising the way dating happens right now. Please give us a try, if you believe in safe, secure and friendly relationship based on trust and respect',
        keywords=['dating', 'tomonotomo', 'friend'],
        image='http://www.tomonotomo.com/static/tomonotomo/img/logo.jpg',
        title='tomonotomo - meet friends of friends'
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
		'loggeduserid': loggedid,
                'fbid': loggedid,
                'fullname': profile.get_full_name(),
                'agelocation': agelocation,
                'worklist': worklist,
                'educationlist': educationlist,
                'meta': meta,
                'title': str(profile.get_full_name()) + ' - tomonotomo - meet friends of friends',
                'connectfriendslist': list(set(map(lambda x: x['fbid'], UserFeedback.objects.filter(userid=loggedid,action=1).values('fbid')))),
		'connectdirectlist': list(set(map(lambda x: x['fbid'], UserFeedback.objects.filter(userid=loggedid,action=2).values('fbid')))),
		'admirelist': list(set(map(lambda x: x['fbid'], UserFeedback.objects.filter(userid=loggedid,action=3).values('fbid')))),
		'connecteddirectlybylist': list(set(map(lambda x: x['userid'], UserFeedback.objects.filter(fbid=loggedid,action=2).values('userid')))),
		'nevershowlist': list(set(map(lambda x: x['fbid'], UserFeedback.objects.filter(userid=loggedid,action=4).values('fbid')))),
		'mostadmiredfriends': dbutils.getMostAdmiredFriends(loggedid, 15)
        })

    return HttpResponse(template.render(context))
 
@login_required(login_url='index')
def fofrandom(request):
    loggedid = dbutils.getLoggedInUser(request)
    quotaover = dbutils.check_quota_over(loggedid)
    gender = UserTomonotomo.objects.get(userid=loggedid).gender
    reqgender = 3
    if gender==1:
        reqgender = 2
    if gender==2:
        reqgender = 1
    fbid = dbutils.getRandFoF(loggedid, reqgender)
    if fbid == 0:
        raise Http404

    if quotaover:
	return redirect('/quotaover')

    try:
    	fbname = slugify(dbutils.getFullName(fbid))
    except:
	fbname = 'tomonotomo'

    return redirect('/profile/'+str(fbname)+'/'+str(fbid))

def profile(request, fbname, fbid):
    logger.debug('view.profile - ' + fbname + ' - ' + str(fbid))
    #fbid = 717323242
    show_button = 1
    notify_hover_on_button = 0
    notify_invite_friends = 0
    notify_welcome = 0
    loggedid=0
    if request.user.id:
        loggedid = dbutils.getLoggedInUser(request)
        mutualfriends = map(lambda x: {'name': dbutils.getFullName(x), 'id': x}, dbutils.getMutualFriends(loggedid, fbid))
        historyFeedback = dbutils.historyFeedback(loggedid, fbid)
        deactivateList = historyFeedback['deactivate']
        doneList = historyFeedback['donelist']
        infoList = historyFeedback['info']
        if len(mutualfriends) == 0:
                show_button=0
        try:
                isa_friend = UserFriends.objects.get(userid=loggedid, friendid=fbid)
                show_button=0
        except UserFriends.DoesNotExist:
                show_button=show_button

	if int(loggedid) == int(fbid):
		show_button=0

	lastfeedback = dbutils.getLastFeedback(loggedid,30)

	if len(lastfeedback)==0:
		notify_welcome=1

	if len(lastfeedback)==10:
		try:
			lastfeedback.remove(4)
		except:
			pass
		try:
			lastfeeback.remove(5)
		except:
			pass
		if len(lastfeedback)<2:
			logger.info('view.profile - Showed Gritter Notification - for hover on button - ' + str(loggedid))
			notify_hover_on_button=1

	if len(lastfeedback)==25:
		logger.info('view.profile - Showed Gritter Notification - for invite friends - ' + str(loggedid))
		notify_invite_friends=1

    else:
        mutualfriends = []
        deactivateList = [1, 2, 3, 4]
        infoList = []
        doneList = []
        show_button = 0


    template = loader.get_template('tomonotomo/profile.html')
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
        image='http://graph.facebook.com/'+str(fbid)+'/picture?type=square',
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

    #if int(loggedid)==717323242:
	#	notify_invite_friends=1
	#	notify_hover_on_button=1
	#	notify_welcome=1
	
    context = RequestContext(request, {
		'loggeduserid': loggedid,
                'fbid': fbid,
                'fullname': profile.get_full_name(),
                'agelocation': agelocation,
                'worklist': worklist,
                'educationlist': educationlist,
                'mutualfriends': mutualfriends,
                'meta': meta,
	        'deactivateList': deactivateList,
	        'infoList': infoList,
	        'doneList': doneList,
	        'email_exists': email_exists,
	        'show_button': show_button,
		'title': str(profile.get_full_name()) + ' - tomonotomo - meet friends of friends',
		'notify_invite_friends': notify_invite_friends,
		'notify_hover_on_button': notify_hover_on_button,
		'notify_welcome': notify_welcome
        })

    return HttpResponse(template.render(context))


def profileredir(request, fbid):    
    try:
        fbname = slugify(dbutils.getFullName(fbid))
    except:
        fbname = 'tomonotomo'

    return redirect('/profile/'+str(fbname)+'/'+str(fbid))

def about(request):

    if request.user.id:
        loggedid = dbutils.getLoggedInUser(request)
    else:
        loggedid = 0

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
        'meta': meta,
	'loggeduserid': loggedid
        })
    return HttpResponse(template.render(context))

def terms(request):

    if request.user.id:
        loggedid = dbutils.getLoggedInUser(request)
    else:
        loggedid = 0

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
        'meta': meta,
	'loggeduserid': loggedid
        })
    return HttpResponse(template.render(context))

@login_required(login_url='index')
def loginerror(request):

    if request.user.id:
        loggedid = dbutils.getLoggedInUser(request)
    else:
        loggedid = 0

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
        'meta': meta,
	'loggeduserid': loggedid
        })
    return HttpResponse(template.render(context))


@login_required(login_url='index')
def loggedin(request):

    if request.user.id:
        loggedid = dbutils.getLoggedInUser(request)
    else:
        loggedid = 0

    fbid = dbutils.getLoggedInUser(request)
    template = loader.get_template('tomonotomo/loggedin.html')

    number_new_introductions = UserHappening.objects.filter(userid=fbid, action=1).count()
    number_new_connect_directly = UserHappening.objects.filter(userid=fbid, action=2).count()
    number_new_admire = UserHappening.objects.filter(userid=fbid, action=3).count()
    show_happening = 0
    if number_new_introductions + number_new_connect_directly + number_new_admire > 0:
	show_happening = 1

    try:
    	UserHappening.objects.filter(userid=fbid).delete()
    except:
	pass

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
		'number_new_introductions': number_new_introductions,
		'number_new_connect_directly': number_new_connect_directly,
		'number_new_admire': number_new_admire,
		'show_happening': show_happening,
        	'meta': meta,
		'loggeduserid': loggedid
		}

    context = RequestContext(request, dictin)
    return HttpResponse(template.render(context))

@login_required(login_url='index')
def betathanks(request):

    if request.user.id:
        loggedid = dbutils.getLoggedInUser(request)
    else:
        loggedid = 0

    fbid = dbutils.getLoggedInUser(request)
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
        'meta': meta,
	'loggeduserid': loggedid
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
    userid = dbutils.getLoggedInUser(request)
    userinfo = UserTomonotomo.objects.get(userid=userid)
    fbname = slugify(dbutils.getFullName(fbid))

    if not fbid in map(lambda x: x['fbid'], UserFeedback.objects.filter(userid=userinfo, timestamp__gte=date.today()).values('fbid')):
        dbutils.decrease_quota(userid)

    actionbefore = UserFeedback.objects.filter(userid=userinfo, fbid=fbid).exclude(action=5).count()

    feedback = UserFeedback(userid=userinfo, fbid=fbid, action=action)
    feedback.save()

    logger.debug("view.tntAction - " + str(userid) + " " + str(fbid) + " " + str(action) + " " + str(fbfriend))
   
    if action == 1:
	dbutils.sendemailFriend(userid, fbid, fbfriend)
	dbutils.updateUserHappening(fbid, action)
	return redirect('/profile/'+str(fbname)+'/'+str(fbid))

    if action == 2:
        mutualfriendlist = dbutils.getMutualFriends(userid, fbid)
        dbutils.sendemailFoF(userid, fbid)
	dbutils.updateUserHappening(fbid,action)
	return redirect('/profile/'+str(fbname)+'/'+str(fbid))

    if action == 3:
	dbutils.updateUserHappening(fbid, action)
        try:
            if UserFeedback.objects.filter(userid=fbid, fbid=userid).values()[0]['action'] == 3:
                mutualfriendlist = dbutils.getMutualFriends(userid, fbid)
                dbutils.sendemailCute(userid, fbid)
        except:
            return redirect('/profile/'+str(fbname)+'/'+str(fbid))

    return redirect('/fof')

def dbsummary(request):

    if request.user.id:
        loggedid = dbutils.getLoggedInUser(request)
    else:
        loggedid = 0

    try: 
	secret = request.GET['secret']
    except:	
    	raise Http404
	 
    template = loader.get_template('tomonotomo/dbsummary.html')
    contextdict = {
	'loggeduserid': loggedid,
	'dbsummary_users_at': UserTomonotomo.objects.exclude(accesstoken=None).count(),
        'dbsummary_users_email': UserTomonotomo.objects.exclude(email=None).count(),
        'dbsummary_users_data': UserTomonotomo.objects.count(),
        'dbsummary_userfriends': UserFriends.objects.count(),
        'dbsummary_userfeedback': UserFeedback.objects.count(),
	'dbsummary_usergender': UserTomonotomo.objects.values('gender').annotate(Count('gender')),
	'dbsummary_userrelstatus': UserTomonotomo.objects.values('relstatus').annotate(Count('relstatus')),
	'dbsummary_users': UserTomonotomo.objects.exclude(email=None).values('userid','first_name','last_name','email'),
	'dbsummary_quota': UserQuota.objects.exclude(quota=30).values('userid','quota'),
	'dbsummary_quota_verification': UserFeedback.objects.filter(timestamp__gte=date.today()).values('userid').annotate(Count('fbid')),
	'dbsummary_feedback': UserFeedback.objects.values('action').annotate(Count('action')).order_by(),
	'dbsummary_users_login_24': UserLogin.objects.filter(timestamp__gte=datetime.now()+timedelta(hours=-24)).order_by('timestamp').values('userlogin','timestamp'),
	'dbsummary_users_register_24': list(set(map(lambda x: x['userlogin'], UserLogin.objects.filter(timestamp__gte=datetime.now()+timedelta(hours=-24)).values('userlogin')))-set(map(lambda x: x['userlogin'], UserLogin.objects.filter(timestamp__lte=datetime.now()+timedelta(hours=-24)).values('userlogin')))),
    }

    context = RequestContext(request, contextdict)

    return HttpResponse(template.render(context))

