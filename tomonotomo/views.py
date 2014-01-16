from django.http import HttpResponse, Http404
from django.template import RequestContext, loader
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import slugify

from tomonotomo.models import UserTomonotomo, UserFeedback, UserFriends, UserLogin, UserHappening, UserQuota, UserEmail

from tomonotomo import dbutils, dbchecks

from meta.views import Meta

from django.templatetags.static import static
from django.db.models import Count

import urllib
from datetime import datetime
from datetime import timedelta
from datetime import date
from profiling import profile, Profiler
import pytz

import logging

logger = logging.getLogger(__name__)


def index(request):

    if request.user.id:
    	loggedid = dbutils.getLoggedInUser(request)
    else:
	loggedid = 0

    meta = Meta(
        use_og=1,
        url='http://www.tomonotomo.com/',
        use_sites=True,
        description='Looking for interesting people in your network? We are revolutionising the way you meet new people right now. Please give us a try, if you believe in safe, secure and friendly relationship based on trust and respect',
        keywords=['dating', 'tomonotomo', 'friend'],
        image='http://www.tomonotomo.com/static/tomonotomo/img/logo.jpg',
        title='tomonotomo - meet friends of friends'
    )    
    template = loader.get_template('tomonotomo/index.html')
    context = RequestContext(request, {
        'meta': meta,
	'usersdatalen': "{:,}".format(UserTomonotomo.objects.count()),
	'loggeduserid': loggedid,
	'quota': dbutils.getQuota(loggedid),
        })
    return HttpResponse(template.render(context))

@login_required(login_url='index')
def nomatchforyou(request):
    template = loader.get_template('tomonotomo/nomatchforyou.html')
    loggedid = dbutils.getLoggedInUser(request)

    context = RequestContext(request, {
        'loggeduserid': loggedid,
	'quota': dbutils.getQuota(loggedid),
        })
    return HttpResponse(template.render(context))

@login_required(login_url='index')
def quotaover(request):
    template = loader.get_template('tomonotomo/quotaover.html')
    loggedid = dbutils.getLoggedInUser(request)

    context = RequestContext(request, {
        'loggedid': loggedid,
	'loggeduserid': loggedid,
	'quota': dbutils.getQuota(loggedid),
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
        url='http://www.tomonotomo.com',
        use_sites=True,
        description='Looking for interesting people in your network? We are revolutionising the way you meet new people right now. Please give us a try, if you believe in safe, secure and friendly relationship based on trust and respect',
        keywords=['dating', 'tomonotomo', 'friend'],
        image='http://www.tomonotomo.com/static/tomonotomo/img/logo.jpg',
        title='tomonotomo - meet friends of friends'
    )
    
    if profile.work == "":
        worklist = []
    else:
        worklist = profile.work.split('---')
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
                'connectfriendslist': list(set(map(lambda x: x['fbid'], UserFeedback.objects.filter(userid=loggedid,action=1).values('fbid')))),
		'connectdirectlist': list(set(map(lambda x: x['fbid'], UserFeedback.objects.filter(userid=loggedid,action=2).values('fbid')))),
		'admirelist': list(set(map(lambda x: x['fbid'], UserFeedback.objects.filter(userid=loggedid,action=3).values('fbid')))),
		'connecteddirectlybylist': list(set(map(lambda x: x['userid'], UserFeedback.objects.filter(fbid=loggedid,action=2).values('userid')))),
		'nevershowlist': list(set(map(lambda x: x['fbid'], UserFeedback.objects.filter(userid=loggedid,action=4).values('fbid')))),
		'mostadmiredfriends': dbutils.getMostAdmiredFriends(loggedid, 15),
		'quota': dbutils.getQuota(loggedid),
		'secretadmirers': dbutils.getSecretAdmirersCount(loggedid),
        })

    return HttpResponse(template.render(context))

@profile 
@login_required(login_url='index')
def fofrandom(request):
    loggedid = dbutils.getLoggedInUser(request)
    quotaover = dbutils.check_quota_over(loggedid)

    if quotaover:
	return redirect('/quotaover')

    gender = UserTomonotomo.objects.get(userid=loggedid).gender
    reqgender = 3
    if gender==1:
        reqgender = 2
    if gender==2:
        reqgender = 1

    fbid = dbutils.getRandFoF(loggedid, reqgender)

    if fbid == 0:
	logger.exception('dbutils.fofrandom - random friend of friend returned zero - ' + str(loggedid))
        return redirect('/nomatchforyou')

    try:
    	fbname = slugify(dbutils.getFullName(fbid))
    except:
	fbname = 'tomonotomo'

    if str(fbname)=='':
	fbname = 'tomonotomo'

    return redirect('/profile/'+str(fbname)+'/'+str(fbid))

@profile
@login_required(login_url='index')
def profile(request, fbname, fbid):
    logger.debug('view.profile - ' + fbname + ' - ' + str(fbid))
    #fbid = 717323242
    show_button = 1
    notify_hover_on_button = 0
    notify_invite_friends = 0
    notify_welcome = 0
    notify_like_follow = 0
    notify_tip_arrowkey = 0
    loggedid=0
    if request.user.id:
        loggedid = dbutils.getLoggedInUser(request)
        mutualfriends = map(lambda x: {'name': dbutils.getFullName(x), 'id': x}, dbutils.getMutualFriends(loggedid, fbid))
	commoninterests = map(lambda x: x['name'], dbutils.getCommonInterests(loggedid, fbid))
        historyFeedback = dbutils.historyFeedback(loggedid, fbid)
        deactivateList = historyFeedback['deactivate']
        doneList = historyFeedback['donelist']
        infoList = historyFeedback['info']
        if len(mutualfriends) == 0:
                show_button=0

	if int(loggedid) == int(fbid):
		show_button=0

	lastfeedback = dbutils.getLastFeedback(loggedid,30)

	if len(lastfeedback)==0:
		logger.info('view.profile - Showed Gritter Notification - for welcome - ' + str(loggedid))
		notify_welcome=1

	if len(lastfeedback)==3:
		logger.info('view.profile - Showed Gritter Notification - for arrowkeys - ' + str(loggedid))
		notify_tip_arrowkey = 1

	if len(lastfeedback)==10:
		lastfeedback = filter(lambda x: x not in [4,5], lastfeedback)
		if len(lastfeedback)<2:
			logger.info('view.profile - Showed Gritter Notification - for hover on button - ' + str(loggedid))
			notify_hover_on_button=1

	if (len(lastfeedback)>=13) and (len(lastfeedback)<=22):
		if lastfeedback[0] not in [4,5]:
			lastfeedback = filter(lambda x: x not in [4,5], lastfeedback)
			if len(lastfeedback)==4:
				logger.info('view.profile - Showed Gritter Notification - for like / follow - ' + str(loggedid))
				notify_like_follow=1

	if len(lastfeedback)==25:
		logger.info('view.profile - Showed Gritter Notification - for invite friends - ' + str(loggedid))
		notify_invite_friends=1

    else:
        commoninterests = []
	mutualfriends = []
        deactivateList = [1, 2, 3, 4]
        infoList = []
        doneList = []
        show_button = 0


    template = loader.get_template('tomonotomo/profile.html')
    try:
    	profile = UserTomonotomo.objects.get(userid=fbid)
    except ObjectDoesNotExist:
	logger.exception('views.profile - Requested id for profile page invalid - ' + str(fbid))
        raise Http404

    if UserTomonotomo.objects.get(userid=fbid).email == None:
        email_exists = 0
    else:
        email_exists = 1

    meta = Meta(
        use_og=1,
        url='http://www.tomonotomo.com/profile/' + str(fbid),
        use_sites=True,
        description='Looking for interesting people in your network? We are revolutionising the way you meet new people right now. Please give us a try, if you believe in safe, secure and friendly relationship based on trust and respect',
        keywords=['dating', 'tomonotomo', 'friend'],
        image='http://graph.facebook.com/'+str(fbid)+'/picture?type=square',
        title= 'tomonotomo - meet friends of friends',
    )


    if profile.work == "":
        worklist = []
    else:
        worklist = profile.work.split('---')
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
    #		notify_invite_friends=1
    #		notify_hover_on_button=1
    #		notify_welcome=1
    #		notify_like_follow=1
    #		notify_tip_arrowkey=1
	
    context = RequestContext(request, {
		'loggeduserid': loggedid,
                'fbid': fbid,
                'fullname': profile.get_full_name(),
                'agelocation': agelocation,
                'worklist': worklist,
                'educationlist': educationlist,
                'mutualfriends': mutualfriends,
		'commoninterests': commoninterests,
                'meta': meta,
	        'deactivateList': deactivateList,
	        'infoList': infoList,
	        'doneList': doneList,
	        'email_exists': email_exists,
	        'show_button': show_button,
		'notify_invite_friends': notify_invite_friends,
		'notify_hover_on_button': notify_hover_on_button,
		'notify_welcome': notify_welcome,
		'notify_like_follow': notify_like_follow,
		'notify_tip_arrowkey': notify_tip_arrowkey,
		'quota': dbutils.getQuota(loggedid),
		'secretadmirers': dbutils.getSecretAdmirersCount(fbid),
		'lovequote': dbutils.getRandomLoveQuote(),
        })

    return HttpResponse(template.render(context))


def profileredir(request, fbid):    
    try:
        fbname = slugify(dbutils.getFullName(fbid))
    except:
        fbname = 'tomonotomo'

    if str(fbname)=='':
	fbname='tomonotomo'

    return redirect('/profile/'+str(fbname)+'/'+str(fbid))

def about(request):

    if request.user.id:
        loggedid = dbutils.getLoggedInUser(request)
    else:
        loggedid = 0

    meta = Meta(
        use_og=1,
        url='http://www.tomonotomo.com/about',
        use_sites=True,
        description='Looking for interesting people in your network? We are revolutionising the way you meet new people right now. Please give us a try, if you believe in safe, secure and friendly relationship based on trust and respect',
        keywords=['dating', 'tomonotomo', 'friend'],
        image='http://www.tomonotomo.com/static/tomonotomo/img/logo.jpg',
        title='tomonotomo - meet friends of friends'
    )    
    template = loader.get_template('tomonotomo/about.html')
    context = RequestContext(request, {
        'meta': meta,
	'loggeduserid': loggedid,
	'quota': dbutils.getQuota(loggedid),
        })
    return HttpResponse(template.render(context))

def terms(request):

    if request.user.id:
        loggedid = dbutils.getLoggedInUser(request)
    else:
        loggedid = 0

    meta = Meta(
        use_og=1,
        url='http://www.tomonotomo.com/terms',
        use_sites=True,
        description='Looking for interesting people in your network? We are revolutionising the way you meet new people right now. Please give us a try, if you believe in safe, secure and friendly relationship based on trust and respect',
        keywords=['dating', 'tomonotomo', 'friend'],
        image='http://www.tomonotomo.com/static/tomonotomo/img/logo.jpg',
        title='tomonotomo - meet friends of friends'
    )    
    template = loader.get_template('tomonotomo/terms.html')
    context = RequestContext(request, {
        'meta': meta,
	'loggeduserid': loggedid,
	'quota': dbutils.getQuota(loggedid),
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
        url='http://www.tomonotomo.com/',
        use_sites=True,
        description='Looking for interesting people in your network? We are revolutionising the way you meet new people right now. Please give us a try, if you believe in safe, secure and friendly relationship based on trust and respect',
        keywords=['dating', 'tomonotomo', 'friend'],
        image='http://www.tomonotomo.com/static/tomonotomo/img/logo.jpg',
        title='tomonotomo - meet friends of friends'
    )
    template = loader.get_template('tomonotomo/loginerror.html')
    context = RequestContext(request, {
        'meta': meta,
	'loggeduserid': loggedid,
	'quota': dbutils.getQuota(loggedid),
        })
    return HttpResponse(template.render(context))

@login_required(login_url='index')
def loggedin(request):

    if request.user.id:
        loggedid = dbutils.getLoggedInUser(request)
    else:
        loggedid = 0
 
    fbid = dbutils.getLoggedInUser(request)
    gender = UserTomonotomo.objects.get(userid=fbid).gender
    template = loader.get_template('tomonotomo/loggedin.html')

    friendsonTnT = dbutils.getFriendsonTnT(fbid)
    friendsoffriends = dbutils.getFriendsofFriends(fbid)
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

    try:
	userloggedin = UserTomonotomo.objects.get(userid=fbid)
        userlogin = UserLogin()
        userlogin.userlogin = userloggedin
	userlogin.friends = len(friendsonTnT)
        userlogin.save()
    except Exception as e:
	logger.exception('views.loggedin - error while saving login information in table UserLogin - error - '+str(e)+' - '+str(e.args))
	pass

    meta = Meta(
        use_og=1,
        url='http://www.tomonotomo.com/',
        use_sites=True,
        description='Looking for interesting people in your network? We are revolutionising the way you meet new people right now. Please give us a try, if you believe in safe, secure and friendly relationship based on trust and respect',
        keywords=['dating', 'tomonotomo', 'friend'],
        image='http://www.tomonotomo.com/static/tomonotomo/img/logo.jpg',
        title='tomonotomo - meet friends of friends'
    )
    dictin = {
		'degree1': "{:,}".format(len(friendsonTnT)),
		'degree2': "{:,}".format(len(friendsoffriends)),
		'number_new_introductions': number_new_introductions,
		'number_new_connect_directly': number_new_connect_directly,
		'number_new_admire': number_new_admire,
		'show_happening': show_happening,
        	'meta': meta,
		'loggeduserid': loggedid,
		'quota': dbutils.getQuota(loggedid),
		'gender': gender,
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

    if UserFeedback.objects.filter(userid=userinfo, fbid=fbid, timestamp__gte=date.today()).count() == 0:
        dbutils.decrease_quota(userid)

    #actionbefore = UserFeedback.objects.filter(userid=userinfo, fbid=fbid).exclude(action=5).count()

    if UserFeedback.objects.filter(userid=userinfo, fbid=fbid, action=action, timestamp__gte=date.today()).exclude(action=1).count() > 0:
	if (action == 1) or (action == 2) or (action == 3):
		return redirect('/profile/'+str(fbname)+'/'+str(fbid))
	if (action == 4) or (action ==5):
		return redirect('/fof')

    feedback = UserFeedback(userid=userinfo, fbid=fbid, action=action)
    feedback.save()

    logger.debug("view.tntAction - " + str(userid) + " " + str(fbid) + " " + str(action) + " " + str(fbfriend))
   
    if action == 1:
	dbutils.sendemailFriend(userid, fbid, fbfriend)
	dbutils.updateUserHappening(fbid, action)
	return redirect('/profile/'+str(fbname)+'/'+str(fbid))

    if action == 2:
        #mutualfriendlist = dbutils.getMutualFriends(userid, fbid)
        dbutils.sendemailFoF(userid, fbid)
	dbutils.updateUserHappening(fbid,action)
	return redirect('/profile/'+str(fbname)+'/'+str(fbid))

    if action == 3:
	dbutils.updateUserHappening(fbid, action)
	try:
		fbidinfo = UserTomonotomo.objects.get(userid=fbid)
		if UserFeedback.objects.filter(userid=fbidinfo, fbid=userid, action=3).count() > 0:
			dbutils.sendemailCute(userid, fbid)
	except Exception as e:
		logger.exception('views.tntAction - checking if there is a reverse feedback for cure - error - '+str(e)+' - '+str(e.args)) 
		pass
	return redirect('/profile/'+str(fbname)+'/'+str(fbid))

    return redirect('/fof')


def dbsummary(request):

    logger.debug('dbsummary starts')
    profiler =  Profiler('tomonotomo.views.dbsummary')
    profiler.start()

    if request.user.id:
        loggedid = dbutils.getLoggedInUser(request)
    else:
        loggedid = 0

    try: 
	secret = request.GET['secret']
    except:	
    	raise Http404

    createerrorlist = ['tomonotomo']
    if 'createerror' in request.GET and request.GET['createerror']:
	createerrorlist = []
    createerrorelem = createerrorlist[0]

    template = loader.get_template('tomonotomo/dbsummary.html')
    contextdict = {
	'loggeduserid': loggedid,
	'quota': dbutils.getQuota(loggedid),
	 #'dbsummary_users_at': UserTomonotomo.objects.exclude(accesstoken=None).count(),
        'dbsummary_users_email': UserTomonotomo.objects.exclude(email=None).count(),
        'dbsummary_users_data': UserTomonotomo.objects.count(),
         #'dbsummary_userfriends': UserFriends.objects.count(),
         #'dbsummary_userfeedback': UserFeedback.objects.count(),
	 #'dbsummary_usergender': UserTomonotomo.objects.values('gender').annotate(Count('gender')),
	 #'dbsummary_userrelstatus': UserTomonotomo.objects.values('relstatus').annotate(Count('relstatus')),
	 #'dbsummary_userinterests': UserTomonotomo.objects.exclude(interests='').exclude(interests=None).count(),
	 #'dbsummary_users': UserTomonotomo.objects.exclude(email=None).values('userid','first_name','last_name','email'),
	'dbsummary_quota': UserQuota.objects.exclude(quota=20).values('userid','quota'),
	'dbsummary_quota_verification': UserFeedback.objects.filter(timestamp__gte=date.today()).values('userid').annotate(Count('fbid', distinct=True)),
	'dbsummary_dbchecksstring': dbchecks.dbchecks2(),
	'dbsummary_feedback': UserFeedback.objects.values('action').annotate(Count('action')).order_by(),
	'dbsummary_users_login_24': UserLogin.objects.filter(timestamp__gte=datetime.now(pytz.timezone('America/Chicago'))+timedelta(hours=-24)).order_by('timestamp').values('userlogin','friends', 'timestamp'),
	'dbsummary_users_register_24': list(set(map(lambda x: x['userlogin'], UserLogin.objects.filter(timestamp__gte=datetime.now(pytz.timezone('America/Chicago'))+timedelta(hours=-24)).values('userlogin')))-set(map(lambda x: x['userlogin'], UserLogin.objects.filter(timestamp__lte=datetime.now(pytz.timezone('America/Chicago'))+timedelta(hours=-24)).values('userlogin')))),
    }
   
    profiler.stop()

    context = RequestContext(request, contextdict)

    return HttpResponse(template.render(context))

