from tomonotomo.models import UserTomonotomo, UserFriends, UserFeedback, UserEmail, UserHappening, UserQuota, TomonotomoQuotes
from django.template import RequestContext, loader
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from random import choice,shuffle
import sendgrid
import math
from django.db.models import Count
from functools32 import lru_cache

import pickle

from datetime import datetime
from datetime import date

import logging

logger = logging.getLogger(__name__)

def print_for_me(fbid,string=""):
	
	string = str(datetime.now()) + " " + string
	if fbid==717323242:
		print str(string)
	return

# Given that the user is logged in, getting the id from email address of the user. 
# If email address was not there, prepared the email address from the facebook username. 
# The case when both email and username does not exist still needs to be checked.
# Always find current user from this and nothing else
def getLoggedInUser (request):
	
	email = ""
	if request.user.email:
		email = request.user.email
	
	elif request.user.username:
		email = request.user.username+"@facebook.com"

	if email=="":
		logger.exception('dbutils.getLoggedInUser - CRITICAL - no email and no username request')
		
	return UserTomonotomo.objects.get(email=email).userid
	
def getMutualFriends (fbid1, fbid2):
        
        fblist1 = UserFriends.objects.filter(userid=fbid1).values('friendid')
        fblist2 = UserFriends.objects.filter(friendid=fbid2).values('userid')

        return list(set(map(lambda x: x['friendid'], fblist1)) & set(map(lambda x: x['userid'], fblist2)))

def getCommonInterests (fbid1, fbid2):

	try:	
		intlist1 = pickle.loads(UserTomonotomo.objects.filter(userid=fbid1).values('interests'))
		intlist2 = pickle.loads(UserTomonotomo.objects.filter(userid=fbid2).values('interests'))

		commonint = set(map(lambda x: x['page_id'], intlist1)) & set(map(lambda x: x['page_id'], intlist2))

		return filter(lambda x: x['page_id'] in commonint, intlist1)
	except:
		return []

@lru_cache(maxsize=16)
def getFriendsofFriends(fbid): 
        fblist = getFriendsonTnT(fbid)
	fofs = map(lambda x: x['friendid'], UserFriends.objects.filter(userid__userid__in=fblist).values('friendid'))
        return list(set(fofs))

@lru_cache(maxsize=16)
def getPotentialFoFs(fbid, reqgender):

	fofs = getFriendsofFriends(fbid)

	if not reqgender==3:
		fofs = list(set(map(lambda x: x['userid'], UserTomonotomo.objects.filter(gender=reqgender).values('userid'))) & set(fofs))

	return fofs

def getBarredListCache(fbid):

	friendlist = map(lambda x: x['friendid'], UserFriends.objects.filter(userid=fbid).values('friendid'))
	skipadmiredlist = map(lambda x: x['fbid'], UserFeedback.objects.filter(userid=fbid, action__range=(3,4)).values('fbid'))
	sadlist = getSadFoFs(fbid)
	barredlist = list(set(friendlist + skipadmiredlist + sadlist))
	return barredlist


def getBarredList(fbid):

        barredlistcache = getBarredListCache(fbid)
        recentlist = map(lambda x: x['fbid'], UserFeedback.objects.filter(userid=fbid, timestamp__gte=date.today()).values('fbid'))
        barredlist = list(set(barredlistcache + recentlist))
	return barredlist

@lru_cache(maxsize=128)
def getSameLocationPeople(loc):
	return map(lambda x: x['userid'], UserTomonotomo.objects.filter(location=loc).values('userid'))
	
@lru_cache(maxsize=32)
def getPopularFoFs(fbid):
	
	admiredpeople=UserFeedback.objects.filter(action=3).values('fbid').annotate(Count('fbid')).order_by('-fbid__count')
	admiredpeople=filter(lambda x: x['fbid__count'] > 3, admiredpeople)
	friendlist = map(lambda x: x['friendid'], UserFriends.objects.filter(userid=fbid).values('friendid'))
	admiredfof=filter(lambda admiredperson: len(set(map(lambda y: y['userid'], UserFriends.objects.filter(friendid=admiredperson['fbid']).values('userid'))) & set(friendlist)), admiredpeople)
	admiredfof = map (lambda x: x['fbid'], admiredfof)
	
	return admiredfof

@lru_cache(maxsize=32)
def getSadFoFs(fbid):

        sadpeople=UserFeedback.objects.filter(action=4).values('fbid').annotate(Count('fbid')).order_by('-fbid__count')
        sadpeople=filter(lambda x: x['fbid__count'] > 7, sadpeople)
        friendlist = map(lambda x: x['friendid'], UserFriends.objects.filter(userid=fbid).values('friendid'))
        sadfof=filter(lambda sadperson: len(set(map(lambda y: y['userid'], UserFriends.objects.filter(friendid=sadperson['fbid']).values('userid'))) & set(friendlist)), sadpeople)
        sadfof = map (lambda x: x['fbid'], sadfof)

        return sadfof

def getRandFoF(fbid, reqgender):

	fblist = getFriendsonTnT(fbid)
	barredlist = getBarredList(fbid)
	popularFoFs = getPopularFoFs(fbid)
	secretadmirers = getSecretAdmirers(fbid)
	allpeopleofsamelocation = getSameLocationPeople(UserTomonotomo.objects.get(userid=fbid).location)
	fbidage = UserTomonotomo.objects.get(userid=fbid).get_age()
	if reqgender == 1:
		minlimit=fbidage-2
		maxlimit=fbidage+5
	if reqgender == 2:
		minlimit=fbidage-5
		maxlimit=fbidage+2
	if reqgender == 3:
		minlimit=0
		maxlimit=0
	
	frndattempts = 0
	while frndattempts < 30:
		frndattempts+=1
		shuffle(fblist)
		listofFoFs = list(set(map(lambda x: x['friendid'], UserFriends.objects.filter(userid__userid=fblist[0]).values('friendid'))))
		listofFoFs = list(set(listofFoFs + popularFoFs + secretadmirers))
		listofFoFs = filter(lambda x: x not in barredlist, listofFoFs)
		listofFoFs = filter(lambda x: x in allpeopleofsamelocation, listofFoFs)

		if len(listofFoFs)==0:
			break

		fofattempts = 0
		if fbidage == "[Age N.A.]":
			while fofattempts < 300:
				fofattempts+=1
				chosen_id = choice(listofFoFs)
				chosen_user = UserTomonotomo.objects.get(userid=chosen_id)
				if not chosen_user.relstatus==2:
					if not reqgender==3:
						if chosen_user.gender==reqgender:
							return chosen_id
					else:
						return chosen_id


		fofattempts = 0
		if fbidage != "[Age N.A.]":
		    while fofattempts < 300:
			fofattempts+=1
			try:
				chosen_id = choice(listofFoFs)
				chosen_user = UserTomonotomo.objects.get(userid=chosen_id)
				if chosen_user.get_age() != "[Age N.A.]":
            				if minlimit <= int(chosen_user.get_age()) <= maxlimit:
						if not chosen_user.relstatus==2:
							if not reqgender==3:
								if chosen_user.gender==reqgender:
									return chosen_id
							else:
								return chosen_id
			except Exception as e:
				logger.exception("dbutils.getRandFoF - Exception while choosing random FoF - " + str(e) + " - " + str(e.args)) 
				pass


	logger.exception("dbutils.getRandFoF - Did not get a rand FoF for the user - " + str(fbid)) 
	return 0

def getFullName (fbid):
        return UserTomonotomo.objects.get(userid=fbid).get_full_name()

@lru_cache(maxsize=32)
def getFriendsonTnT (fbid):
        fblist = map(lambda x: x['friendid'], UserFriends.objects.filter(userid=fbid).values('friendid'))
        fblist2 = map(lambda x: x['userid'], UserTomonotomo.objects.exclude(email=None).values('userid'))
        return list(set(fblist) & set(fblist2))

@lru_cache(maxsize=4)
def getUsersGender (gender):
	return map(lambda x: x['userid'], UserTomonotomo.objects.filter(gender=gender).values('userid'))

def getLastFeedback (userid, num):
	return map(lambda x: x['action'], UserFeedback.objects.filter(userid=userid).order_by('-id').values('action')[0:num])

def getQuota(fbid):
	try:
		quota = UserQuota.objects.get(userid=fbid).quota
	except:
		quota = 0
	return quota

def getSecretAdmirersCount(fbid):
	try:
		num = UserFeedback.objects.filter(fbid=fbid, action=3).count()
	except:
		num = 0

	return num

def getSecretAdmirers(fbid):

	try:
		return map(lambda x: x['userid'], UserFeedback.objects.filter(fbid=fbid, action=3).values('userid'))
	except:
		return []

	return []
	
def check_quota_over(fbid):
	try:
		quota = UserQuota.objects.get(userid=fbid)
		if quota.quota > 0:
			return False
		else:
			return True
	except UserQuota.DoesNotExist:
		return False

	return False

def increase_quota(fbid):
	quota = UserQuota.objects.get(userid=fbid)
	quota.quota = 30 
	quota.save()
	return

def decrease_quota(fbid):
	quota = UserQuota.objects.get(userid=fbid)
	quota.quota +=-1
	quota.save()
	return

def getMostAdmiredFriends(fbid, num):
	people=UserFeedback.objects.filter(action=3).values('fbid').annotate(Count('fbid')).order_by('-fbid__count')
	friendlist = map(lambda x: x['friendid'], UserFriends.objects.filter(userid=fbid).values('friendid'))
	admiredfriends = filter(lambda x: x['fbid'] in friendlist,people)
	admiredfriends = filter(lambda x: x['fbid__count'] > 3, admiredfriends)
	return map(lambda x: x['fbid'], admiredfriends[:num])

def sendemailCute (userid, fofid):

        emaillogging = UserEmail(userid=userid, fofid=fofid, action=3)
        emaillogging.save()

        s = sendgrid.Sendgrid('pratikpoddar', 'P1jaidadiki', secure=True)

        userinfo = UserTomonotomo.objects.get(userid=userid)
        fofinfo = UserTomonotomo.objects.get(userid=fofid)

        contextdict = {}
        subject = "Mutual Connection Request for " + userinfo.first_name + " and " + fofinfo.first_name
        contextdict['teaserline'] = subject
        contextdict['mailheading'] = subject
        contextdict['mailcontent'] = "Hey "+fofinfo.first_name+" and "+userinfo.first_name+", Both of you have indicated privately that you admire each other. Since both of you want to meet each other, by god's grace, we at tomonotomo, have been privileged, to introduce you to each other. You can take it forward from here. Best of Luck. We are happy. :-). Thanks a ton. Regards, Tomonotomo."
        plaintext_message = contextdict['mailcontent']
        html_message = prepareEmail(contextdict, userid, fofid, userinfo.get_full_name(), fofinfo.get_full_name())

        message = sendgrid.Message(("admin@tomonotomo.com","Tomonotomo"), subject, plaintext_message, html_message)

        # add a recipient
        message.add_to(userinfo.email, userinfo.get_full_name())
        message.add_to(fofinfo.email, fofinfo.get_full_name())

        # use the SMTP API to send your message
        s.smtp.send(message)
	
	#message.add_to('pratik.phodu@gmail.com', 'Pratik Poddar')
	#s.smtp.send(message)

        return

def sendemailFriend (userid, fofid, friendid):

        emaillogging = UserEmail(userid=userid, fofid=fofid, friendid=friendid, action=1)
        emaillogging.save()

        s = sendgrid.Sendgrid('pratikpoddar', 'P1jaidadiki', secure=True)

        userinfo = UserTomonotomo.objects.get(userid=userid)
        fofinfo = UserTomonotomo.objects.get(userid=fofid)
        friendinfo = UserTomonotomo.objects.get(userid=friendid)

	contextdict = {}
        subject = "Request by " + userinfo.first_name + " to get connected with " + fofinfo.first_name
	contextdict['teaserline'] = subject
	contextdict['mailheading'] = subject
	contextdict['mailcontent'] = "Hey "+friendinfo.first_name+", Hope you are doing well. I discovered "+fofinfo.first_name+" on www.tomonotomo.com . I think we might hit it off together. Do you mind introducing me to " + fofinfo.first_name + " and I will take it forward from there. Thanks a ton. Regards, "+userinfo.first_name
        plaintext_message = contextdict['mailcontent']
        html_message = prepareEmail(contextdict, userid, fofid, userinfo.get_full_name(), fofinfo.get_full_name())
        message = sendgrid.Message(("admin@tomonotomo.com","Tomonotomo"), subject, plaintext_message, html_message)

        # add a recipient
        message.add_to(userinfo.email, userinfo.get_full_name())
        message.add_to(friendinfo.email, friendinfo.get_full_name())

        # use the SMTP API to send your message
        s.smtp.send(message)

	#message.add_to('pratik.phodu@gmail.com', 'Pratik Poddar')
        #s.smtp.send(message)

        return

def sendemailFoF (userid, fofid):

        emaillogging = UserEmail(userid=userid, fofid=fofid, action=2)
        emaillogging.save()

        s = sendgrid.Sendgrid('pratikpoddar', 'P1jaidadiki', secure=True)

        userinfo = UserTomonotomo.objects.get(userid=userid)
        fofinfo = UserTomonotomo.objects.get(userid=fofid)

        contextdict = {}
        subject = "Connection Request by " + userinfo.first_name + " to connect with " + fofinfo.first_name
        contextdict['teaserline'] = subject
        contextdict['mailheading'] = subject
        contextdict['mailcontent'] = "Hey "+fofinfo.first_name+", Hope you are doing well. I discovered you on www.tomonotomo.com . I think we might hit it off together. I would like to connect with you. To feel comfortable before replying to the email, you can assure yourself through our mutual friends. You can get all the details from my tomonotomo profile page. Thanks a ton. Sincere apologies if I was offensive or intrusive in any way. Regards, "+userinfo.first_name
        plaintext_message = contextdict['mailcontent']
        html_message = prepareEmail(contextdict, userid, fofid, userinfo.get_full_name(), fofinfo.get_full_name())
        message = sendgrid.Message(("admin@tomonotomo.com","Tomonotomo"), subject, plaintext_message, html_message)

        # add a recipient
        message.add_to(userinfo.email, userinfo.get_full_name())
        message.add_to(fofinfo.email, fofinfo.get_full_name())

        # use the SMTP API to send your message
        s.smtp.send(message)

	#message.add_to('pratik.phodu@gmail.com', 'Pratik Poddar')
        #s.smtp.send(message)

        return

def historyFeedback (userid1, userid2):

        # return {'deactivate': [1, 2, 4], 'info': ["checking 1", "checking 2", "checking 3"]}

        result1 = UserFeedback.objects.filter(userid=userid1, fbid=userid2)
        result2 = UserFeedback.objects.filter(userid=userid2, fbid=userid1)

        deactivate = []
        info = []
	donelist = []

        if (len(result1) > 0) and (len(result2) == 0):
	   
	    for i in range(0,len(result1)):

	            if result1.values()[i]['action'] == 1:
        	        info.append("You have sent Introduction Request to Friends")

	            if result1.values()[i]['action'] == 2:
        	        deactivate.append(1)
	                donelist.append(2)
	                deactivate.append(3)
	                deactivate.append(4)
        	        info.append("You have sent Direct Connection Request")

	            if result1.values()[i]['action'] == 3:
	                donelist.append(3)
	                deactivate.append(4)
	                info.append("You marked - Admire Secretly")

	            if result1.values()[i]['action'] == 4:
	                deactivate.append(3)
	                donelist.append(4)
	                info.append("You marked - Skip, and never show")

        if (len(result1) == 0) and (len(result2) > 0):

	    for i in range(0, len(result2)):

	            if result2.values()[i]['action'] == 2:
        	        info.append("You would have received a Direct Connection Request over email. Best of Luck")

        if (len(result1) > 0) and (len(result2) > 0):

	
	    for i in range(0, len(result1)):
		for j in range(0, len(result2)):
	
	            if (result2.values()[j]['action'] == 1) or (result2.values()[j]['action'] == 4):

        	        if result1.values()[i]['action'] == 1:
                	    info.append("You have sent Introduction Request to Friends")

	                if result1.values()[i]['action'] == 2:
	                    deactivate.append(1)
	                    donelist.append(2)
	                    deactivate.append(3)
	                    deactivate.append(4)
	                    info.append("You have sent Direct Connection Request")

        	        if result1.values()[i]['action'] == 3:
	                    donelist.append(3)
	                    deactivate.append(4)
	                    info.append("You marked - Admire Secretly")

        	        if result1.values()[i]['action'] == 4:
	                    deactivate.append(3)
	                    donelist.append(4)
        	            info.append("You marked - Skip, and never show")

	            if result2.values()[j]['action'] == 2:

        	        if result1.values()[i]['action'] == 1:
	                    deactivate.append(2)
        	            deactivate.append(3)
               		    deactivate.append(4)
	                    info.append("You have sent Introduction Request to Friends")
	                    info.append("You would have received a Direct Connection Request over email")

	                if result1.values()[i]['action'] == 2:
	                    deactivate.append(1)
	                    donelist.append(2)
	                    deactivate.append(3)
	                    deactivate.append(4)
	                    info.append("You have sent Direct Connection Request")
        	            info.append("You would have received a Direct Connection Request over email")

	                if result1.values()[i]['action'] == 3:
        	            deactivate.append(1)
	                    donelist.append(3)
	                    deactivate.append(4)
        	            info.append("You marked - Admire Secretly")
	                    info.append("You would have received a Direct Connection Request over email")

        	        if result1.values()[i]['action'] == 4:
                	    deactivate.append(1)
	                    deactivate.append(3)
        	            donelist.append(4)
                	    info.append("You marked - Skip, and never show")
	                    info.append("You would have received a Direct Connection Request over email")

        	    if result2.values()[j]['action'] == 3:
	
        	        if result1.values()[i]['action'] == 1:
                	    info.append("You have sent Introduction Request to Friends")

	                if result1.values()[i]['action'] == 2:
	                    deactivate.append(1)
        	            donelist.append(2)
                	    deactivate.append(3)
	                    deactivate.append(4)
        	            info.append("You have sent Direct Connection Request")

	                if result1.values()[i]['action'] == 3:
	                    deactivate.append(1)
	                    donelist.append(3)
        	            deactivate.append(4)
	                    info.append("Both of you admire each other. Tomonotomo sent an email to both of you. Best of Luck")

        	        if result1.values()[i]['action'] == 4:
	                    deactivate.append(3)
        	            donelist.append(4)
                	    info.append("You marked - Skip, and never show")

        return {'deactivate': list(set(deactivate) - set(donelist)), 'info': list(set(info)), 'donelist': list(set(donelist))}


def prepareEmail(contextdict, userid, fofid, username, fofname):

	contextdict['leftimage'] = "https://graph.facebook.com/"+str(userid)+"/picture?width=200&height=200"
	contextdict['rightimage'] = "https://graph.facebook.com/"+str(fofid)+"/picture?width=200&height=200"
	
	contextdict['leftcontent'] = ""
	contextdict['rightcontent'] = ""

	contextdict['lefttitle']  = username
	contextdict['righttitle'] = fofname

	contextdict['leftid'] = userid
	contextdict['rightid'] = fofid

	contextdict['title'] = "tomonotomo - meet friends of friends"
	contextdict['headerimage'] = "http://www.tomonotomo.com/static/tomonotomo/img/emailbanner.png"

	output = render_to_string('tomonotomo/email.html', contextdict)
	return output

def updateUserHappening(userid, action):

	userhappening = UserHappening(userid=userid, action=action)
	userhappening.save()
	return

def getRandomLoveQuote():
	try:
		return TomonotomoQuotes.objects.order_by('?')[0].quote.strip()
	except:
		return ""


