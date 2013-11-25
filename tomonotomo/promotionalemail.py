from tomonotomo.models import UserTomonotomo, UserFriends, UserFeedback, UserEmail, UserHappening
from django.template import RequestContext, loader
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from random import choice,shuffle
import sendgrid
import heapq

from tomonotomo import unsubscribe
from tomonotomo import dbutils

from functools32 import lru_cache

from datetime import datetime

unsubscribe_list = unsubscribe.unsubscribe_list

def num_of_admires(fbid):
	return UserFeedback.objects.filter(fbid=fbid, action=3).count()

def top_admires(userid):
	listofAdmired = map(lambda x: {x['friendid']: num_of_admires(x['friendid'])}, UserFriends.objects.filter(userid=userid).values('friendid'))
	return heapq.nlargest(2, listofAdmired, lambda x: x.values()[0])

def sendPromotionalEmailCuteFriends101(userid):

	# Being saved in email logging as action item 101

	l = top_admires(userid)

	if len(l) < 2:
		return
	
	if min(l[0].values()[0], l[1].values()[0]) < 2:
		return

        s = sendgrid.Sendgrid('pratikpoddar', 'P1jaidadiki', secure=True)

        userinfo = UserTomonotomo.objects.get(userid=userid)
        friend1info = UserTomonotomo.objects.get(userid=l[0].keys()[0])
        friend2info = UserTomonotomo.objects.get(userid=l[1].keys()[0])

	contextdict = {}
        subject = userinfo.first_name + ", your friends find " + friend1info.first_name + " and " + friend2info.first_name + " attractive"
	contextdict['teaserline'] = subject
	contextdict['mailheading'] = subject
	contextdict['mailcontent'] = "Hey "+userinfo.first_name+", Hope you are doing well. Your friends find " + friend1info.first_name + " and " + friend2info.first_name + " attractive. They are trending in your friend network on tomonotomo. You can also secretly indicate that you admire some friend of friend. If he/she also feels the same way, you two would be connected. Best of Luck!"
        plaintext_message = contextdict['mailcontent']
        html_message = dbutils.prepareEmail(contextdict, l[0].keys()[0], l[1].keys()[0], friend1info.get_full_name(), friend2info.get_full_name())
        message = sendgrid.Message(("admin@tomonotomo.com","Tomonotomo"), subject, plaintext_message, html_message)

        # add a recipient
        message.add_to(userinfo.email, userinfo.get_full_name())

        # use the SMTP API to send your message
        s.smtp.send(message)

	#message.add_to('pratik.phodu@gmail.com', 'Pratik Poddar')
        #s.smtp.send(message)

        emaillogging = UserEmail(userid=userid, fofid=l[0].keys()[0], friendid=l[1].keys()[0], action=101)
        emaillogging.save()

        return


def findPeople101():
	friendsofPratik = UserFriends.objects.filter(userid=717323242).values('friendid')
	peopleonTnT = UserTomonotomo.objects.exclude(email=None).values('userid')
	
	return list(set(map(lambda x: x['userid'], peopleonTnT)) & set(map(lambda x: x['friendid'], friendsofPratik)))

def findPeople101_2():
	peopleonTnT = UserTomonotomo.objects.exclude(email=None).values('userid')
	alreadysent = UserEmail.objects.filter(action=101).values('userid')
	
	return list(set(map(lambda x: x['userid'], peopleonTnT)) - set(map(lambda x: x['userid'], alreadysent)))	

def sendEmail101():
	
	lpeople = findPeople101()
	lpeople = filter(lambda x: x not in unsubscribe_list, lpeople)
	for lperson in lpeople:
		sendPromotionalEmailCuteFriends101(lperson)

	return

def sendEmail101_2():
	lpeople = findPeople101_2()
	lpeople = filter(lambda x: x not in unsubscribe_list, lpeople)
	for lperson in lpeople:
		sendPromotionalEmailCuteFriends101(lperson)


	

