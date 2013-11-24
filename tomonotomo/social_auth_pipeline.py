from social_auth.models import UserSocialAuth
from social_auth.backends.facebook import FacebookBackend
from facepy import GraphAPI
import time
import pprint
from random import randint
from datetime import datetime
from datetime import timedelta
import simplejson
import urllib2

from tomonotomo.models import UserTomonotomo, UserFriends, UserProcessing, UserLogin, UserQuota

from django.db import transaction

from django_cron import CronJobBase, Schedule

import logging

logger = logging.getLogger(__name__)

genderdict = { "male":1, "female":2, "not specified":3 }
relstatusdict = { "Single":1, "Engaged":2, "Married":2, "In a relationship":2, "It's complicated":3, "In an open relationship":3, "Widowed":3, "Separated":3, "Divorced":3, "In a civil union":3, "In a domestic partnership":3, "not specified":3 }
 
def create_custom_user(backend, details, user=None, 
                        user_exists=UserSocialAuth.simple_user_exists, *args, **kwargs):

        logger.debug("social_auth_pipeline.create_custom_user - Creating Custom User")

        ## TODO: Make not updating condition stricter. stop only if (not new) and (updated in last 10 days)
        if kwargs['is_new'] == False:
        	logger.debug("social_auth_pipeline.create_custom_user - Returning user " + str(user))
	else:
        	logger.debug("social_auth_pipeline.create_custom_user - Getting data for first time user " + str(user))

        if user is None:
                logger.exception("social_auth_pipeline.create_custom_user - User came as None in the function create_custom_user")
                return
        if backend.__class__ != FacebookBackend:
                return

        res = kwargs['response']

	logger.debug("social_auth_pipeline.create_custom_user - Getting/Updating data for userid " + res.get('id'))
	logger.debug("social_auth_pipeline.create_custom_user - " + str(res))

        try:
            profile = UserTomonotomo.objects.get(userid=res.get('id'))
        except UserTomonotomo.DoesNotExist:
            profile = UserTomonotomo()

        profile.accesstoken = res.get('access_token')
        profile.expiresin = res.get('expires')
        if res.get('work'):
                profile.work= getSanitizedWork(res['work'])
        if res.get('education'):
                profile.education= getSanitizedEducation(res['education'])
        profile.email = res.get('email')
	if not res.get('email'):
		profile.email = str(res.get('username'))+"@facebook.com"
		logger.info("social_auth_pipeline.create_custom_user - Email not found for user " + str(res.get('id')) + ". Using " + profile.email)
		if not res.get('username'):
			logger.exception("social_auth_pipeline.create_custom_user - Critical - Could neither get email nor username@facebook.com for user " + str(res.get('id')))
        profile.first_name = res.get('first_name')
        profile.last_name = res.get('last_name')
        profile.gender = genderdict[res.get('gender') or "not specified"]
        if res.get('hometown'):
                profile.hometown = res.get('hometown').get('name')
        if res.get('location'):
                profile.location = res.get('location').get('name')
	if res.get('relationship_status'):
		profile.relstatus = relstatusdict[res.get('relationship_status') or "not specified"]
        profile.username = res.get('username')
        profile.userid = res.get('id')

        # "----"

        graph = GraphAPI(res.get('access_token'))
        responsegraph = graph.get(str(res['id'])+'?fields=birthday,likes')
        profile.birthday = str(responsegraph.get('birthday'))
	if responsegraph.get('likes'):
		profile.interests = str(extractAllSanitizedLikes(responsegraph.get('likes')))

        profile.save()

        # "----"

        userloggedin = UserTomonotomo.objects.get(userid=res['id'])

	# "----"

        try:
            userprocessing = UserProcessing.objects.get(userloggedin=userloggedin)
        except UserProcessing.DoesNotExist:
            userprocessing = UserProcessing()
            userprocessing.userloggedin = userloggedin
        except UserProcessing.MultipleObjectsReturned:
            userprocessing = userProcessing()
            userprocessing.userloggedin = userloggedin

        userprocessing.accesstoken = res.get('access_token')

        userprocessing.save()

	# "----"

	try:
		userquota = UserQuota.objects.get(userid=res.get('id'))
	except UserQuota.DoesNotExist:
		userquota = UserQuota()
		userquota.userid = res.get('id')
		userquota.quota=30
		userquota.save()

	# "----"

	if kwargs['is_new']==False:
		logger.debug("social_auth_pipeline.create_custom_user - completed for returning user " + str(res.get('id')))
		return

        friendlist = graph.fql('SELECT uid2 FROM friend where uid1=me()')
        peopleontnt = UserTomonotomo.objects.values('userid')

        friendsontnt = list(set(map(lambda x: int(x['uid2']), friendlist.get('data'))) & set(map(lambda x: x['userid'], peopleontnt)))
	
        for friendontnt in friendsontnt:
            try:
                profilefriends = UserFriends.objects.get(userid=userloggedin, friendid=friendontnt)
            except UserFriends.DoesNotExist:
                profilefriends = UserFriends()
                profilefriends.userid = userloggedin
                profilefriends.friendid = friendontnt
                profilefriends.save()

        # "----"

        logger.debug("social_auth_pipeline.create_custom_user - completed for first time user " + str(userloggedin))
        return

def getSanitizedEducation (educationProfile):
        """ Helper function to get education profile as a structured string """
        education = ""
        for value in educationProfile:
                if value.get('school') and value['school'].get('name'):
                        education = education + value['school']['name']+'---'
        return education

def getSanitizedWork (workProfile):
        """ Helper function to get work profile as a structured string """
        work = ""
        for value in workProfile:
                if value.get('employer') and value['employer'].get('name'):
                        work = work + value['employer']['name']+'---'
        return work

def extractAllSanitizedLikes (likeResFBGraph):
	
	likesResult = []
	likesResult += getSanitizedLikes(likeResFBGraph['data'])
	try:
		likesResult += getAllLikes(likeResFBGraph['paging']['next'])
	except:
		pass
	return likesResult

def getAllLikes (likelink):
	
	likesdata = simplejson.load(urllib2.urlopen(likelink))
	likesList = []
	likesList += getSanitizedLikes(likesdata['data'])
	try:
		likesList += getAllLikes(likesdata['paging']['next'])
	except:
		pass
	return likesList

def getSanitizedLikes (likesList):
        """ Helper function to get likes as a structured string """
	likesResult = []
	for likevalue in likesList:
		try:
			likesResult.append({'page_id': likevalue['id'], 'name': likevalue['name']})
		except:
			pass
	return likesResult

def postProcessing(userid, accessToken):

	userloggedin = UserTomonotomo.objects.get(userid=userid)
        graph = GraphAPI(accessToken)
        logger.debug("social_auth_pipeline.postProcessing - Processing " + accessToken + " - " + str(userid))
	try:
		## Checking if accesstoken is valid
        	friendnumber = graph.fql('SELECT friend_count FROM user where uid=me()')
        	numberfriends = friendnumber.get('data')[0].get('friend_count')
        	logger.debug("social_auth_pipeline.postProcessing - number of friends " + str(numberfriends))
	except Exception as e:
		logger.exception("social_auth_pipeline.postProcessing - Accesstoken is invalid - " + str(e) + " - " + str(e.args))
		raise

        friendgraphdata= []
        friendgraph= []
        for i in range(0,10):
            query = 'SELECT uid,first_name,last_name,username,name,birthday,education,work,sex,hometown_location,current_location,relationship_status FROM user WHERE uid in (SELECT uid2 FROM friend where uid1=me() limit '+str(max(0,(i*500)-100))+',500)'
            friendgraphdata.append(graph.fql(query))
            friendgraph.extend(friendgraphdata[i].get('data'))
            logger.debug("social_auth_pipeline.postProcessing - received data for " + str(len(friendgraph)) + " friends - some are duplicate")

        logger.debug("social_auth_pipeline.postProcessing - list of friends data "+str(len(friendgraph))+" - some are duplicate")

        count = 0
        for frienddata in friendgraph:

            count = count + 1
            logger.debug("social_auth_pipeline.postProcessing - Saving detailed information for friendid - " + str(frienddata.get('uid')) + " - count " + str(count))

            try:
		profilefriends = UserFriends.objects.get(userid=userloggedin, friendid=frienddata.get('uid'))
            except UserFriends.DoesNotExist:
                profilefriends = UserFriends()
                profilefriends.userid = userloggedin
                profilefriends.friendid = frienddata.get('uid')
		try:
                	profilefriends.save()
		except Exception as e:
			logger.exception("social_auth_pipeline.postProcessing - Exception saving userfriends data - multiple entries in userfriends race error - " + str(e) + " - " + str(e.args))
			pass
	    except UserFriends.MultipleObjectsReturned:
		logger.exception("social_auth_pipeline.postProcessing - Exception saving userfriends data - multiple entries in userfriends race error - ")
            	pass
	    except Exception as e:
	    	logger.exception("social_auth_pipeline.postProcessing - Exception saving UserFriends - " + str(e) + " - " + str(e.args))
		raise

	    try:
                userfriend = UserTomonotomo.objects.get(userid=frienddata.get('uid'))
            except UserTomonotomo.DoesNotExist:
                userfriend = UserTomonotomo()

	    try:	     
            	if frienddata.get('work'):
               		userfriend.work= getSanitizedWork(frienddata['work'])
            	if frienddata.get('education'):
                	userfriend.education= getSanitizedEducation(frienddata['education'])
            	userfriend.first_name = frienddata.get('first_name')
           	userfriend.last_name = frienddata.get('last_name')
		try:
            		userfriend.gender = genderdict[frienddata.get('sex') or "not specified"]
		except:
			userfriend.gender = genderdict["not specified"]
           	if frienddata.get('hometown_location'):
                	userfriend.hometown = frienddata.get('hometown_location').get('name')
            	if frienddata.get('current_location'):
                	userfriend.location = frienddata.get('current_location').get('name')

		try:
			userfriend.relstatus = relstatusdict[frienddata.get('relationship_status') or "not specified"]
		except:
			userfriend.relstatus = relstatusdict["not specified"]

            	userfriend.username = frienddata.get('username')
            	userfriend.userid = frienddata.get('uid')
            
	    	if frienddata.get('birthday'):
                	try:
                    		userfriend.birthday = time.strftime("%m/%d/%Y", time.strptime(frienddata.get('birthday'), "%B %d, %Y"))
                	except:
                    		pass

		try:
			if not userfriend.interests:
				query = 'SELECT page_id, name FROM page WHERE page_id IN (SELECT page_id FROM page_fan WHERE uid=' + str(frienddata.get('uid')) + ')'
				userfriend.interests = graph.fql(query).get('data')
		except Exception as e:
			logger.exception("social_auth_pipeline.postProcessing - Error getting friends' likes - " + str(e) + " - " + str(e.args))
			pass

	    except Exception as e:
		logger.exception("social_auth_pipeline.postProcessing - Error collecting information - " + str(e) + " - " + str(e.args))
		raise

	    try:
            	userfriend.save()
	    except Exception as e:
		logger.exception("social_auth_pipeline.postProcessing - Error saving userdata - " + str(e) + " - " + str(e.args))
		raise

        return

class startPostProcessing(CronJobBase):
    RUN_EVERY_MINS = 1 # every 1 min

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'tomonotomo.social_auth_pipeline.startPostProcessing'    # a unique code

    def do(self):
	logger.debug("social_auth_pipeline.startPostProcessing - StartPostProcessing starts")
        pendingusers = UserProcessing.objects.filter(entryaddtime__lte=datetime.now()+timedelta(hours=-1)).values('userloggedin','accesstoken')
	logger.debug("social_auth_pipeline.startPostProcessing - StartPostProcessing starts - length of list is " + str(len(pendingusers)))
        if len(pendingusers) > 0:
        	randnum = randint(0, len(pendingusers)-1)
		userloggedin = pendingusers[randnum].get('userloggedin')
                accesstoken = pendingusers[randnum].get('accesstoken')
		
		UserProcessing.objects.filter(userloggedin = userloggedin).delete()
            	userprocessing = UserProcessing()
	        userprocessing.userloggedin = UserTomonotomo.objects.get(userid=userloggedin)
		userprocessing.accesstoken = accesstoken
		userprocessing.save()

                try:
			logger.debug("social_auth_pipeline.startPostProcessing - Starting Post Processing for " + str(userloggedin) + " with accesstoken " + accesstoken)
                	postProcessing(userloggedin, accesstoken)
			logger.debug("social_auth_pipeline.startPostProcessing - Almost Completed Post Processing for " + str(userloggedin) + " with accesstoken " + accesstoken)
                	UserProcessing.objects.filter(userloggedin = userloggedin).delete()
                	logger.debug("social_auth_pipeline.startPostProcessing - Completed Post Processing for " + str(userloggedin) + " with accesstoken " + accesstoken)
        	except:
            		logger.exception("social_auth_pipeline.startPostProcessing - Failed Post Processing for " + str(userloggedin) + " with accesstoken " + accesstoken)

		logger.debug("social_auth_pipeline.startPostProcessing - Before this operation - length of list was " + str(len(pendingusers)))

    	return

class updateQuota(CronJobBase):
	RUN_AT_TIMES = ['00:00']
	schedule = Schedule(run_at_times=RUN_AT_TIMES)
	code='tomonotomo.social_auth_pipeline.updateQuota'

	def do(self):
		logger.debug("social_auth_pipeline.updateQuota - UpdateQuota starts")
		users = UserTomonotomo.objects.all().exclude(email=None).values('userid')
		for user in users:
			try:
                		userquota = UserQuota.objects.get(userid=user['userid'])
				userquota.quota=30
        		except UserQuota.DoesNotExist:
                		userquota = UserQuota(userid=user['userid'], quota=30)
                	userquota.save()

		logger.debug("social_auth_pipeline.updateQuota - Done UpdateQuota")
		return

