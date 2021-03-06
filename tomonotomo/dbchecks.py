from tomonotomo.models import UserTomonotomo, UserFriends, UserFeedback, UserEmail, UserHappening, UserQuota, UserProcessing
import math
from django.db.models import Count
import re
from string import expandtabs

import logging

logger = logging.getLogger(__name__)

def dbchecks1():
	string=""
	set11=set([])
	set12=set([])
	set2=set([])
	set11 = set(map(lambda x: x['friendid'], UserFriends.objects.all().values('friendid')))
	set12 = set(map(lambda x: x['userid'], UserFriends.objects.all().values('userid')))
	set1 = set(list(set11)+list(set12))
	set2 = set(map(lambda x: x['userid'], UserTomonotomo.objects.all().values('userid')))
	string+= "<br/>------ Checking that there is no stray element in UserFriends.userid"
	string+= "<br/>" + "(UserFriends.userid + UserFriends.friendid) - UserTomonotomo.userid: " + str(set1-set2)
	string+= "<br/>" + "(UserFriends.userid) - UserTomonotomo.userid: " + str(set12-set2)
	string+= "<br/>" + "Both the above should be null"
	return (string + "<br/>").replace('<br/>','\r\n')

def dbchecks11():
	string =""
	list1=UserFeedback.objects.exclude(action=1).exclude(action=5).values('userid','fbid','action').annotate(Count('id'))
        list2 = filter(lambda x: x['id__count'] > 1, list1)
        string+= "<br/>----- Checking that except 1 and 5, no action is taken twice for a userid, fbid pair in UserFeedback"
        string+= "<br/>" + str(list2)
        string+= "<br/>" + "The number list should be empty"
	return (string + "<br/>").replace('<br/>','\r\n')
	
def dbchecks2():
	string=""
	
	logger.debug('dbchecks.dbchecks2 - Stage 1')

	list3=UserProcessing.objects.values('userloggedin')
	string+= "<br/>" + "----- Checking that all accesstokens have been processed"
	string+= "<br/>" + str(list3)
	string+= "<br/>" + "The above list should be empty"
	
	logger.debug('dbchecks.dbchecks2 - Stage 2')

	list4=UserEmail.objects.filter(action__lt=100).exclude(action=1).values('userid','fofid','friendid','action').annotate(Count('id'))
	list5=filter(lambda x: x['id__count']>1,list4)
	string+= "<br/>" + "----- Checking that no email was sent twice except requesting a friend twice"
	string+= "<br/>" + str(list5)
	string+= "<br/>" + "The above list should be empty"

	logger.debug('dbchecks.dbchecks2 - Stage 3')

	list6=map(lambda x: x['email'], UserTomonotomo.objects.exclude(email=None).values('email'))
	list7=filter(lambda x: not re.match(r'[\w\.\+-]+@[\w\.-]+', x), list6)
	string+= "<br/>" + "----- Checking that all email addresses in database are sane"
	string+= "<br/>" + str(list7)
	string+= "<br/>" + "The above list should be empty"

	logger.debug('dbchecks.dbchecks2 - Stage 4')

        list8=map(lambda x: x['userid'], UserTomonotomo.objects.exclude(email=None).values('userid'))
	list9=list(set(map(lambda x: x['userid'], UserFriends.objects.exclude(userid__in=list8).values('userid'))))
	string+= "<br/>" + "----- Checking that all friends info are only for people who have logged in"
        string+= "<br/>" + str(list(set(list9)))
        string+= "<br/>" + "The above list should be empty"

	logger.debug('dbchecks.dbchecks2 - Stage 5')
	
	tntusers= map(lambda x: x['userid'], UserTomonotomo.objects.exclude(email=None).values('userid'))
	list10 = UserFriends.objects.exclude(friendid__in=tntusers).values('userid').annotate(Count('friendid'))
	list11 = map(lambda x: x['userid'], filter(lambda x: x['friendid__count']<10, list10))
	string+= "<br/>" + "----- Checking that all users have been properly expanded and all friend data extracted. Potentially issues with following"
	string+= "<br/>" + str(list(set(list11)))
	string+= "<br/>" + "The above list should be empty"	
	
	logger.debug('dbchecks.dbchecks2 - Stage 6')

	return (string + "<br/>").replace('<br/>','\r\n')

